#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from scrape_products import (
    RAW_DIR,
    OUT_DIR,
    REPORT_DIR,
    SITES,
    classify_url,
    get,
    meta,
    norm_space,
    sitemap_urls,
    slugify,
    vitar_product,
    nase_product,
)


CONTENT_MD_DIR = Path(__file__).resolve().parents[1] / "outputs" / "content-pages"
PUBLIC_DATA_DIR = Path(__file__).resolve().parents[1] / "outputs" / "data"


def cache_path(site_key, url):
    return RAW_DIR / f"{site_key}_{slugify(urlparse(url).path.strip('/')) or 'home'}.html"


def page_family(url, title, h1, text):
    path = urlparse(url).path.strip("/").lower()
    hay = " ".join([path, title, h1, text[:500]]).lower()
    if path.startswith(("vitar-klub", "soutez")):
        return "marketing_club"
    if path.startswith("znacky"):
        return "brand_landing"
    if path in {"produkty", "novinky", "darkova-baleni", "stick-packy", "dostupny-sortiment"} or path.startswith(("produkty/", "homepage/", "darkova-baleni/", "darkova-vyhodna-baleni/")):
        return "category_or_listing"
    if "kariera" in path or "volna-mista" in path:
        return "career"
    if any(x in path for x in ["obchodni-podminky", "ochrana-osobnich-udaju", "doprava", "platba", "kontakt"]):
        return "commerce_support"
    if path.startswith("pro-zdravi") or any(x in path for x in ["ambasadori", "seminar", "pohar-zdravi", "30-minut-pro-zdravi"]):
        return "article_or_knowledge"
    if path.startswith("o-nas") or any(x in hay for x in ["o společnosti", "historie", "pro media", "pomahame", "spoluprace"]):
        return "corporate_group"
    if any(x in path for x in ["blog", "aktuality", "pro-zdravi", "magazin"]):
        return "article_or_knowledge"
    return "other_content"


def suggested_destination(record):
    family = record["family"]
    url = record["url"]
    path = urlparse(url).path.strip("/")
    path_l = path.lower()
    site = record["source_site"]
    if any(x in path_l for x in ["veterinae", "veterina", "pro-zvirata", "pro-zvireci-mazlicky"]):
        return {
            "action": "move_to_veterina_shop",
            "destination": "veterina.vittar.group or dedicated VITAR Veterina e-shop",
            "reason": "Veterina is being split into its own BU and should not be part of the main VITAR.cz taxonomy.",
        }
    if family == "corporate_group":
        return {
            "action": "move_to_group_web",
            "destination": f"vittar.group/{path}",
            "reason": "Group story, company trust, manufacturing and employer content belong to the VITAR GROUP corporate layer.",
        }
    if family == "career":
        return {
            "action": "move_to_group_web",
            "destination": "vittar.group/kariera",
            "reason": "Employer branding and hiring should be centralized on the group website.",
        }
    if family == "brand_landing":
        return {
            "action": "keep_on_vitar_cz",
            "destination": f"vitar.cz/{path}",
            "reason": "Brand landings support D2C navigation, SEO and the approved portfolio hierarchy.",
        }
    if family == "category_or_listing":
        return {
            "action": "rebuild_on_vitar_cz",
            "destination": f"vitar.cz/{path}",
            "reason": "Use as SEO/category inspiration, but rebuild in the new taxonomy and PIM-driven faceting.",
        }
    if family == "commerce_support":
        return {
            "action": "keep_or_merge_on_shop",
            "destination": f"vitar.cz/{path}" if site == "vitar.cz" else f"nasevitaminy.cz/{path}",
            "reason": "Required operational content for checkout, customer trust, legal and support.",
        }
    if family == "marketing_club":
        return {
            "action": "rewrite_for_vitar_club",
            "destination": "vitar.cz/vitar-klub",
            "reason": "Keep the loyalty concept, but rewrite around the new customer account and CRM model.",
        }
    if family == "article_or_knowledge":
        return {
            "action": "audit_for_knowledge_base",
            "destination": "vitar.cz/blog or knowledge base",
            "reason": "Useful for SEO and recommender context, but needs medical/legal claim review.",
        }
    return {
        "action": "manual_review",
        "destination": "TBD",
        "reason": "Content value or owner is unclear.",
    }


def extract_main_text(soup):
    copy = BeautifulSoup(str(soup), "html.parser")
    for tag in copy.select("script, style, noscript, svg, nav, header, footer, form, iframe"):
        tag.decompose()
    main = copy.select_one("main, .main, #main, .content, .page, .cms-page, article") or copy.body or copy
    return norm_space(main.get_text(" ", strip=True))


def extract_page(site_key, url, html):
    soup = BeautifulSoup(html, "html.parser")
    product = vitar_product(soup, url) if site_key == "vitar" else nase_product(soup, url)
    if product:
        return None
    title = norm_space((soup.title or {}).get_text(" ", strip=True) if soup.title else "")
    h1_tag = soup.select_one("h1")
    h1 = norm_space(h1_tag.get_text(" ", strip=True)) if h1_tag else ""
    description = meta(soup, 'meta[name="description"]') or meta(soup, 'meta[property="og:description"]')
    canonical = soup.select_one('link[rel="canonical"]')
    text = extract_main_text(soup)
    if len(text) < 80 and not h1:
        return None
    source_site = SITES[site_key]["base"].replace("https://www.", "").replace("https://", "")
    record = {
        "content_id": hashlib.sha1(url.encode("utf-8")).hexdigest()[:12],
        "source_site": source_site,
        "url": url,
        "canonical_url": canonical.get("href") if canonical else url,
        "slug": urlparse(url).path.strip("/") or "home",
        "title": title,
        "h1": h1,
        "meta_description": description,
        "family": page_family(url, title, h1, text),
        "text_length": len(text),
        "text_sample": text[:800],
        "headings": [norm_space(h.get_text(" ", strip=True)) for h in soup.select("h1, h2, h3") if norm_space(h.get_text(" ", strip=True))][:30],
        "links_internal_count": len([a for a in soup.select("a[href]") if SITES[site_key]["base"] in a.get("href", "") or a.get("href", "").startswith("/")]),
        "images_count": len(soup.select("img")),
    }
    record["migration"] = suggested_destination(record)
    return record


def scrape_content(site_key, include_candidate_non_products=False, limit=0, refresh=False):
    site = SITES[site_key]
    session = requests.Session()
    urls = sitemap_urls(site["sitemap"], session)
    if include_candidate_non_products:
        candidates = urls
    else:
        candidates = [u for u in urls if classify_url(site_key, u) in {"content", "category_or_landing"}]
    if limit:
        candidates = candidates[:limit]
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pages = []
    errors = []
    for idx, url in enumerate(candidates, 1):
        path = cache_path(site_key, url)
        try:
            if path.exists() and not refresh:
                html = path.read_text(encoding="utf-8")
            else:
                html = get(url, session, delay=site["delay"])
                path.write_text(html, encoding="utf-8")
            page = extract_page(site_key, url, html)
            if page:
                pages.append(page)
            print(f"[{site_key}] {idx}/{len(candidates)} content={len(pages)} {url}", flush=True)
        except Exception as exc:
            errors.append({"url": url, "error": str(exc)})
            print(f"[{site_key}] ERROR {url}: {exc}", file=sys.stderr, flush=True)
    return {
        "site": site_key,
        "sitemap_url_count": len(urls),
        "candidate_count": len(candidates),
        "content_count": len(pages),
        "pages": pages,
        "errors": errors,
    }


def write_content_cards(pages):
    CONTENT_MD_DIR.mkdir(parents=True, exist_ok=True)
    for page in pages:
        fname = f"{page['source_site'].replace('.', '-')}_{page['slug'].replace('/', '__')}.md"
        path = CONTENT_MD_DIR / fname
        md = f"""# {page['h1'] or page['title']}

- Source: {page['source_site']}
- URL: {page['url']}
- Family: {page['family']}
- Migration action: {page['migration']['action']}
- Destination: {page['migration']['destination']}
- Reason: {page['migration']['reason']}
- Title: {page['title']}
- Meta description: {page['meta_description']}

## Headings
{chr(10).join(f"- {h}" for h in page['headings'])}

## Text Sample
{page['text_sample']}
"""
        path.write_text(md, encoding="utf-8")


def write_report(bundle):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    pages = bundle["pages"]
    lines = [
        "# VITAR content migration inventory",
        "",
        f"Generated: {bundle['generated_at']}",
        f"Content pages: {len(pages)}",
        "",
        "## Critical Build Readiness",
        "",
        "Verdict: this is enough for discovery, vendor briefing and information architecture, but not yet enough for a final e-shop build. The product scrape gives a strong first PIM seed, but the new platform still needs enriched active ingredients, dosage, claims/legal review, availability/pricing source of truth, redirect rules and final brand architecture decisions.",
        "",
        "Given the 2026 VITAR GROUP context, the build should be split into three workstreams: `vittar.group` for corporate/employer/B2B trust, `vitar.cz` for D2C shop and knowledge base, and a separate Veterina shop/BU for veterinary products.",
        "",
        "## Recommended Migration Actions",
        "",
    ]
    for action, count in Counter(p["migration"]["action"] for p in pages).most_common():
        lines.append(f"- {action}: {count}")
    lines.extend([
        "",
        "## By Content Family",
        "",
    ])
    for family, count in Counter(p["family"] for p in pages).most_common():
        lines.append(f"- {family}: {count}")
    lines.extend([
        "",
        "## Priority Pages",
        "",
        "| Action | Family | Source | H1 / Title | Destination | Reason |",
        "|---|---|---|---|---|---|",
    ])
    priority_order = {
        "move_to_group_web": 0,
        "move_to_veterina_shop": 1,
        "keep_on_vitar_cz": 2,
        "rebuild_on_vitar_cz": 3,
        "keep_or_merge_on_shop": 4,
        "rewrite_for_vitar_club": 5,
        "audit_for_knowledge_base": 6,
        "manual_review": 7,
    }
    def cell(value):
        return str(value).replace("|", "\\|")
    sorted_pages = sorted(pages, key=lambda p: (priority_order.get(p["migration"]["action"], 99), p["family"], p["source_site"], p["slug"]))
    for page in sorted_pages[:120]:
        lines.append(
            f"| {page['migration']['action']} | {page['family']} | [{page['source_site']}]({page['url']}) | {cell(page['h1'] or page['title'])} | {cell(page['migration']['destination'])} | {cell(page['migration']['reason'])} |"
        )
    lines.extend([
        "",
        "## Missing Before Development Freeze",
        "",
        "- Final routing map: old URL -> new URL -> owner -> redirect status.",
        "- Content owner per page: Group/CMO, D2C e-shop, Veterina BU, legal, HR, B2B/OEM.",
        "- Claim review for health content and product descriptions before import.",
        "- Enriched PIM attributes: active ingredients, dosage, age/target group, allergens/diet flags, contraindications, pack size, price per dose.",
        "- Decision on legacy brand handling: VITAR premium hero, MaxiVita Essentials top tier, MaxiVita mass market, Revital sunset/migration, Vitar Botanicals.",
    ])
    (REPORT_DIR / "content-migration-inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(results):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    pages = []
    for result in results:
        pages.extend(result["pages"])
    bundle = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_sites": [r["site"] for r in results],
        "counts": {
            "pages": len(pages),
            "by_site": dict(Counter(p["source_site"] for p in pages)),
            "by_family": dict(Counter(p["family"] for p in pages)),
            "by_action": dict(Counter(p["migration"]["action"] for p in pages)),
        },
        "pages": pages,
        "crawl_results": [{k: v for k, v in r.items() if k != "pages"} for r in results],
    }
    bundle_json = json.dumps(bundle, ensure_ascii=False, indent=2)
    (OUT_DIR / "content-pages.json").write_text(bundle_json, encoding="utf-8")
    (PUBLIC_DATA_DIR / "content-pages.json").write_text(bundle_json, encoding="utf-8")
    for csv_path in [OUT_DIR / "content-pages.csv", PUBLIC_DATA_DIR / "content-pages.csv"]:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "source_site", "family", "action", "destination", "h1", "title", "meta_description", "text_length", "url"
            ])
            writer.writeheader()
            for p in pages:
                writer.writerow({
                    "source_site": p["source_site"],
                    "family": p["family"],
                    "action": p["migration"]["action"],
                    "destination": p["migration"]["destination"],
                    "h1": p["h1"],
                    "title": p["title"],
                    "meta_description": p["meta_description"],
                    "text_length": p["text_length"],
                    "url": p["url"],
                })
    write_content_cards(pages)
    write_report(bundle)
    return bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", choices=["all", "vitar", "nasevitaminy"], default="all")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--include-candidate-non-products", action="store_true")
    args = parser.parse_args()
    sites = ["vitar", "nasevitaminy"] if args.site == "all" else [args.site]
    results = [
        scrape_content(site, include_candidate_non_products=args.include_candidate_non_products, limit=args.limit, refresh=args.refresh)
        for site in sites
    ]
    bundle = write_outputs(results)
    print(json.dumps(bundle["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
