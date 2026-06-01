#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
MD_DIR = ROOT / "outputs" / "pim-product-cards"
REPORT_DIR = ROOT / "outputs" / "reports"

SITES = {
    "vitar": {
        "base": "https://www.vitar.cz",
        "sitemap": "https://www.vitar.cz/sitemap.xml",
        "delay": 1.0,
    },
    "nasevitaminy": {
        "base": "https://www.nasevitaminy.cz",
        "sitemap": "https://www.nasevitaminy.cz/sitemap.xml",
        "delay": 0.15,
    },
}

CATEGORY_MAP = [
    ("immune", "Imunita a nachlazení", ["imunit", "nachlaz", "echinacea", "betaglukan", "vitamin c", "rakytn"]),
    ("kids", "Děti", ["kids", "děti", "deti", "škol", "skol", "kolostrum"]),
    ("magnesium", "Hořčík a minerály", ["hořčík", "horcik", "magnez", "vapnik", "vápník", "zinek", "miner"]),
    ("beauty", "Krása, vlasy, pleť", ["beauty", "kolagen", "vlasy", "nehty", "pokoz", "pokož", "pleť", "plet", "revitalon"]),
    ("joints", "Klouby a pohyb", ["kloub", "pohyb", "artivit", "motion"]),
    ("digestion_detox", "Trávení a detox", ["detox", "tráven", "trav", "odkysel", "játra", "jater", "střeva", "streva"]),
    ("energy_stress", "Energie, stres, spánek", ["energit", "energie", "stres", "spánek", "spanek", "tryptofan", "ashwagandha"]),
    ("eyes", "Zrak", ["zrak", "oči", "oci", "lutein"]),
    ("heart", "Srdce a oběh", ["srdce", "oběh", "obeh", "q10", "koenzym"]),
    ("urinary", "Močové cesty", ["moč", "moc", "brusink"]),
    ("repellents", "Repelenty a paraziti", ["predator", "repelent", "komár", "komar", "klíšť", "klist", "parazit"]),
    ("pets", "Veterinae a zvířata", ["veterinae", "zvíř", "zvir", "pes", "kočka", "kocka"]),
    ("drinks", "Nápoje a pitný režim", ["capri", "ovoce", "nápoj", "napoj", "pitný", "pitny", "rehydrat"]),
    ("sweeteners", "Sladidla", ["irbis", "sladid", "stevie", "sukral", "aspartam", "sacharin"]),
    ("hangover", "Vyprošťovák", ["vyprostovak", "vyprošťovák"]),
]

BRANDS = [
    "Maxi Vita Essentials",
    "Maxi Vita",
    "Maxivita",
    "Revital Botanicals",
    "Revitalon",
    "Revital",
    "Energit",
    "Predator",
    "Capri-Sun",
    "Vyprošťovák",
    "Vyprostovak",
    "Irbis",
    "eMVe",
    "Vitar Veterinae",
    "Veterinae",
    "OvoCé",
    "Ovoce",
    "Vitar Kids",
    "Vitar Kings",
    "Vitar Eko",
    "Vitar",
]

FORM_KEYWORDS = [
    ("effervescent_tablets", "Šumivé tablety", ["šumiv", "sumiv", "eff"]),
    ("tablets", "Tablety", ["tablet", "tbl"]),
    ("capsules", "Kapsle", ["kaps", "cps"]),
    ("stick_pack", "Stick pack", ["stick"]),
    ("syrup", "Sirup / elixír", ["sirup", "elix"]),
    ("powder", "Prášek / sypká směs", ["práš", "pras", "sypk", "směs", "smes"]),
    ("drink", "Nápoj", ["nápoj", "napoj", "0,2", "0.2", "0,33", "0.33"]),
    ("cosmetic", "Kosmetika", ["šampon", "sampon", "sérum", "serum", "vazel", "gel"]),
]

NEED_STATES = [
    "pro děti", "imunita", "energie", "stres", "spánek", "zrak", "klouby", "srdce",
    "detox", "trávení", "močové cesty", "krása", "vlasy", "pleť", "hořčík",
    "vitamin c", "beta-karoten", "repelent", "zvířata",
]


def norm_space(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def slugify(value):
    value = value.lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[\s_]+", "-", value)
    return value.strip("-")


def get(url, session, delay=0):
    if delay:
        time.sleep(delay)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; VitarEcommerceMigrationAudit/1.0; +https://github.com/jurajgiacko/vitarecommerce)"
    }
    response = session.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def sitemap_urls(url, session):
    xml = get(url, session)
    root = ET.fromstring(xml.encode("utf-8"))
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    if root.tag.endswith("sitemapindex"):
        urls = []
        for loc in root.findall(".//sm:sitemap/sm:loc", ns):
            urls.extend(sitemap_urls(loc.text.strip(), session))
        return urls
    return [loc.text.strip() for loc in root.findall(".//sm:url/sm:loc", ns)]


def parse_jsonld(soup):
    items = []
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text()
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            items.extend(data)
        else:
            items.append(data)
    return items


def meta(soup, selector, attr="content"):
    tag = soup.select_one(selector)
    return norm_space(tag.get(attr, "")) if tag else ""


def detect_brand(name, url, manufacturer=""):
    hay = f"{name} {url} {manufacturer}".lower()
    for brand in BRANDS:
        if brand.lower() in hay:
            if brand == "Maxivita":
                return "Maxi Vita"
            if brand == "Vyprostovak":
                return "Vyprošťovák"
            return brand
    return manufacturer or "VITAR portfolio"


def detect_form(text):
    hay = text.lower()
    for key, label, words in FORM_KEYWORDS:
        if any(w in hay for w in words):
            return {"key": key, "label": label}
    return {"key": "unknown", "label": "Neurčeno"}


def classify_category(record):
    hay = " ".join([
        record.get("name", ""),
        record.get("slug", ""),
        record.get("description", ""),
        " ".join(record.get("breadcrumbs", [])),
        record.get("brand", ""),
    ]).lower()
    matched = []
    for key, label, words in CATEGORY_MAP:
        score = sum(1 for w in words if w in hay)
        if score:
            matched.append((score, key, label))
    if matched:
        matched.sort(reverse=True)
        return {"key": matched[0][1], "label": matched[0][2], "score": matched[0][0]}
    return {"key": "other", "label": "Ostatní / nezařazeno", "score": 0}


def extract_need_states(record):
    hay = " ".join([record.get("name", ""), record.get("description", ""), record.get("slug", "")]).lower()
    return [state for state in NEED_STATES if state in hay]


def vitar_product(soup, url):
    body_classes = soup.body.get("class", []) if soup.body else []
    if "catalog-product-view" not in body_classes and not soup.select_one(".product-view"):
        return None
    jsonlds = parse_jsonld(soup)
    product_ld = next((x for x in jsonlds if x.get("@type") == "Product"), {})
    name = norm_space((soup.select_one("h1") or {}).get_text(" ", strip=True) if soup.select_one("h1") else "")
    if not name:
        name = meta(soup, 'meta[property="og:title"]').replace("| VITAR, s.r.o.", "").strip()
    desc = meta(soup, 'meta[name="description"]') or meta(soup, 'meta[property="og:description"]')
    image = meta(soup, 'meta[property="og:image"]')
    canonical = soup.select_one('link[rel="canonical"]')
    attrs = {}
    for wrap in soup.select(".option-wrap"):
        label = norm_space((wrap.select_one(".option-label") or wrap).get_text(" ", strip=True)).strip(":")
        content = wrap.select_one(".option-content")
        value = norm_space(content.get_text(" ", strip=True)) if content else ""
        if label and value:
            attrs[label] = value
    breadcrumbs = [norm_space(x.get_text(" ", strip=True)) for x in soup.select(".breadcrumbs li, .breadcrumb li") if norm_space(x.get_text(" ", strip=True))]
    sections = {}
    for heading in soup.select(".productInfo h3, .product-info h3, h3"):
        title = norm_space(heading.get_text(" ", strip=True))
        box = heading.find_next_sibling()
        if title and box:
            text = norm_space(box.get_text(" ", strip=True))
            if text and len(text) > 20:
                sections[title] = text[:5000]
    sku = attrs.get("Kód") or attrs.get("SKU") or product_ld.get("sku", "")
    ean = attrs.get("EAN") or product_ld.get("gtin13", "")
    brand = detect_brand(name, url, attrs.get("Výrobce", ""))
    record = {
        "source_site": "vitar.cz",
        "url": url,
        "canonical_url": canonical.get("href") if canonical else url,
        "slug": urlparse(url).path.strip("/"),
        "name": name,
        "brand": brand,
        "manufacturer": attrs.get("Výrobce", ""),
        "sku": sku,
        "ean": ean,
        "price_czk": None,
        "availability": "",
        "description": desc,
        "image": image,
        "breadcrumbs": breadcrumbs,
        "attributes": attrs,
        "content_sections": sections,
        "seo": {
            "title": norm_space((soup.title or {}).get_text(" ", strip=True) if soup.title else ""),
            "meta_description": desc,
            "og_title": meta(soup, 'meta[property="og:title"]'),
            "og_image": image,
        },
    }
    enrich(record)
    return record


def nase_product(soup, url):
    body_classes = soup.body.get("class", []) if soup.body else []
    if "view-commodity-detail" not in body_classes and not soup.select_one(".commodityDetail"):
        return None
    jsonlds = parse_jsonld(soup)
    product_ld = next((x for x in jsonlds if x.get("@type") == "Product"), {})
    name = norm_space(product_ld.get("name") or (soup.select_one("h1") or {}).get_text(" ", strip=True))
    desc = meta(soup, 'meta[name="description"]') or norm_space((soup.select_one(".vc-commoditydetail_annotation") or {}).get_text(" ", strip=True) if soup.select_one(".vc-commoditydetail_annotation") else "")
    info = {}
    for dl in soup.select(".vc-commoditydetail_info dl"):
        dt = norm_space((dl.select_one("dt") or dl).get_text(" ", strip=True))
        dd = norm_space((dl.select_one("dd") or dl).get_text(" ", strip=True))
        if dt and dd:
            info[dt] = dd
    breadcrumbs = [norm_space(x.get_text(" ", strip=True)) for x in soup.select("#breadcrumbs li") if norm_space(x.get_text(" ", strip=True))]
    price = None
    offers = product_ld.get("offers") or {}
    spec = offers.get("priceSpecification") or {}
    if isinstance(spec, dict):
        price = spec.get("price")
    if price is None:
        match = re.search(r"productPrice\":?\s*([0-9.]+)", soup.get_text(" ", strip=True))
        if match:
            price = float(match.group(1))
    images = product_ld.get("image") or []
    if isinstance(images, str):
        images = [images]
    brand = detect_brand(name, url, info.get("Výrobce", ""))
    record = {
        "source_site": "nasevitaminy.cz",
        "url": url,
        "canonical_url": product_ld.get("url") or meta(soup, 'meta[property="og:url"]') or url,
        "slug": urlparse(url).path.strip("/"),
        "name": name,
        "brand": brand,
        "manufacturer": info.get("Výrobce", ""),
        "sku": product_ld.get("productID") or info.get("Kód", ""),
        "ean": info.get("EAN", ""),
        "price_czk": price,
        "availability": info.get("Dostupnost", ""),
        "description": desc,
        "image": images[0] if images else meta(soup, 'meta[property="og:image"]'),
        "breadcrumbs": breadcrumbs,
        "attributes": info,
        "content_sections": extract_nase_sections(soup),
        "seo": {
            "title": norm_space((soup.title or {}).get_text(" ", strip=True) if soup.title else ""),
            "meta_description": desc,
            "og_title": meta(soup, 'meta[property="og:title"]'),
            "og_image": meta(soup, 'meta[property="og:image"]'),
        },
    }
    enrich(record)
    return record


def extract_nase_sections(soup):
    sections = {}
    for box in soup.select(".vc-commoditydetail_description, .commodityDetail .description, .vc-tabs, .wysiwyg"):
        text = norm_space(box.get_text(" ", strip=True))
        if len(text) > 80:
            key = "Popis" if "Popis" not in sections else f"Popis {len(sections) + 1}"
            sections[key] = text[:5000]
    return sections


def enrich(record):
    record["product_id"] = hashlib.sha1(record["url"].encode("utf-8")).hexdigest()[:12]
    record["form"] = detect_form(" ".join([record.get("name", ""), record.get("slug", ""), json.dumps(record.get("attributes", {}), ensure_ascii=False)]))
    record["category_recommendation"] = classify_category(record)
    record["need_states"] = extract_need_states(record)
    record["pim_status"] = {
        "has_sku": bool(record.get("sku")),
        "has_ean": bool(record.get("ean")),
        "has_image": bool(record.get("image")),
        "has_description": len(record.get("description", "")) > 20,
        "has_price": record.get("price_czk") is not None,
    }


def classify_url(site_key, url):
    path = urlparse(url).path.strip("/")
    category_prefixes = ("produkty", "znacky", "homepage", "darkova", "novinky", "stick-packy", "dostupny-sortiment")
    if path == "" or path in {"produkty", "znacky"}:
        return "category_or_landing"
    if path.startswith(category_prefixes):
        return "category_or_landing"
    if any(x in path for x in ["o-nas", "kariera", "kontakt", "ochrana", "obchodni", "doprava", "registrace", "soutez", "pro-zdravi", "vitar-klub"]):
        return "content"
    return "candidate_product"


def scrape_site(site_key, limit=0, refresh=False):
    site = SITES[site_key]
    session = requests.Session()
    urls = sitemap_urls(site["sitemap"], session)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = [u for u in urls if classify_url(site_key, u) == "candidate_product"]
    if limit:
        candidates = candidates[:limit]
    products = []
    errors = []
    for idx, url in enumerate(candidates, 1):
        cache_path = RAW_DIR / f"{site_key}_{slugify(urlparse(url).path.strip('/')) or 'home'}.html"
        try:
            if cache_path.exists() and not refresh:
                html = cache_path.read_text(encoding="utf-8")
            else:
                html = get(url, session, delay=site["delay"])
                cache_path.write_text(html, encoding="utf-8")
            soup = BeautifulSoup(html, "html.parser")
            product = vitar_product(soup, url) if site_key == "vitar" else nase_product(soup, url)
            if product:
                products.append(product)
            print(f"[{site_key}] {idx}/{len(candidates)} products={len(products)} {url}", flush=True)
        except Exception as exc:
            errors.append({"url": url, "error": str(exc)})
            print(f"[{site_key}] ERROR {url}: {exc}", file=sys.stderr, flush=True)
    return {
        "site": site_key,
        "sitemap_url_count": len(urls),
        "candidate_count": len(candidates),
        "product_count": len(products),
        "products": products,
        "errors": errors,
    }


def write_markdown_cards(products):
    MD_DIR.mkdir(parents=True, exist_ok=True)
    for product in products:
        fname = f"{product['source_site'].replace('.', '-')}_{product['slug'].replace('/', '__')}.md"
        path = MD_DIR / fname
        attrs = "\n".join(f"- {k}: {v}" for k, v in product.get("attributes", {}).items())
        sections = "\n\n".join(f"## {k}\n{v}" for k, v in product.get("content_sections", {}).items())
        md = f"""# {product['name']}

- Source: {product['source_site']}
- URL: {product['url']}
- Brand: {product['brand']}
- SKU: {product.get('sku') or ''}
- EAN: {product.get('ean') or ''}
- Recommended category: {product['category_recommendation']['label']}
- Form: {product['form']['label']}
- Need states: {', '.join(product.get('need_states') or [])}
- Image: {product.get('image') or ''}

## Short Description
{product.get('description') or ''}

## Attributes
{attrs}

{sections}
"""
        path.write_text(md, encoding="utf-8")


def write_outputs(results):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    products = []
    for result in results:
        products.extend(result["products"])
    bundle = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_sites": [r["site"] for r in results],
        "counts": {
            "products": len(products),
            "by_site": dict(Counter(p["source_site"] for p in products)),
            "by_brand": dict(Counter(p["brand"] for p in products)),
            "by_category": dict(Counter(p["category_recommendation"]["label"] for p in products)),
            "by_form": dict(Counter(p["form"]["label"] for p in products)),
        },
        "products": products,
        "crawl_results": [{k: v for k, v in r.items() if k != "products"} for r in results],
    }
    (OUT_DIR / "products.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT_DIR / "products.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "source_site", "name", "brand", "sku", "ean", "price_czk", "category", "form", "need_states", "url", "image"
        ])
        writer.writeheader()
        for p in products:
            writer.writerow({
                "source_site": p["source_site"],
                "name": p["name"],
                "brand": p["brand"],
                "sku": p.get("sku", ""),
                "ean": p.get("ean", ""),
                "price_czk": p.get("price_czk", ""),
                "category": p["category_recommendation"]["label"],
                "form": p["form"]["label"],
                "need_states": ", ".join(p.get("need_states") or []),
                "url": p["url"],
                "image": p.get("image", ""),
            })
    write_markdown_cards(products)
    write_summary(bundle)
    return bundle


def write_summary(bundle):
    lines = [
        "# VITAR / NašeVitamíny PIM scrape summary",
        "",
        f"Generated: {bundle['generated_at']}",
        f"Products: {bundle['counts']['products']}",
        "",
        "## By Site",
    ]
    for key, value in sorted(bundle["counts"]["by_site"].items()):
        lines.append(f"- {key}: {value}")
    lines.append("\n## By Brand")
    for key, value in Counter(bundle["counts"]["by_brand"]).most_common():
        lines.append(f"- {key}: {value}")
    lines.append("\n## Recommended Categories")
    for key, value in Counter(bundle["counts"]["by_category"]).most_common():
        lines.append(f"- {key}: {value}")
    lines.append("\n## PIM Quality Checks")
    products = bundle["products"]
    for field, label in [
        ("has_sku", "SKU"),
        ("has_ean", "EAN"),
        ("has_image", "Image"),
        ("has_description", "Description"),
        ("has_price", "Price"),
    ]:
        ok = sum(1 for p in products if p["pim_status"][field])
        lines.append(f"- {label}: {ok}/{len(products)}")
    (REPORT_DIR / "scrape-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", choices=["all", "vitar", "nasevitaminy"], default="all")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    sites = ["vitar", "nasevitaminy"] if args.site == "all" else [args.site]
    results = [scrape_site(site, args.limit, args.refresh) for site in sites]
    bundle = write_outputs(results)
    print(json.dumps(bundle["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
