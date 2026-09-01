#!/usr/bin/env python3
"""Create an auditable product snapshot from all VITAR consumer websites."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import threading
import time
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CURRENT_DIR = DATA_DIR / "current"
RAW_DIR = DATA_DIR / "raw"
APP_DATA_DIR = ROOT / "src" / "data"


@dataclass(frozen=True)
class Site:
    key: str
    domain: str
    sitemap: str


SITES = {
    "vitar": Site("vitar", "vitar.cz", "https://www.vitar.cz/sitemap.xml"),
    "nasevitaminy": Site(
        "nasevitaminy", "nasevitaminy.cz", "https://www.nasevitaminy.cz/sitemap.xml"
    ),
    "ceskevitaminy": Site(
        "ceskevitaminy", "ceske-vitaminy.cz", "https://www.ceske-vitaminy.cz/sitemap.xml"
    ),
}

BRANDS = [
    "Maxi Vita Essentials",
    "Revital Botanicals",
    "Vitar Veterinae",
    "VITAR Veterinae",
    "Vitar Origin",
    "VITAR Origin",
    "Vitar Kids",
    "Vitar Eko",
    "Vitar Kings",
    "Maxi Vita",
    "Maxivita",
    "Revitalon",
    "Revital",
    "Energit",
    "Predator",
    "Capri-Sun",
    "Vyprošťovák",
    "Vyprostovak",
    "Irbis",
    "eMVe",
    "Veterinae",
    "OvoCé",
    "Vitar",
    "VITAR",
]

CATEGORY_RULES = [
    ("veterina", "Veterina", ["veterinae", "pro psy", "pro kočky", "pro kocky"]),
    ("repellents", "Repelenty a ochrana", ["predator", "repelent", "klíšť", "klist", "parazit", "hmyz"]),
    ("kids", "Děti", ["kids", "pro děti", "pro deti", "děts", "dets", "kolostrum"]),
    ("womens_health", "Zdraví žen", ["fembalance", "goddess", "hormon", "menopau", "ženy", "zeny"]),
    ("mens_health", "Zdraví mužů", ["alphamale", "mužská vitalita", "muzska vitalita", "erektor", "pro muže"]),
    ("sleep_stress", "Spánek a stres", ["spánek", "spanek", "sleep", "stres", "ashwagandha", "večerní pohoda"]),
    ("energy", "Energie a výkon", ["energie", "energy", "výkon", "vykon", "kofein", "guarana"]),
    ("immunity", "Imunita", ["imunit", "betaglukan", "echinacea", "rakytn", "nachlaz"]),
    ("magnesium", "Hořčík", ["hořčík", "horcik", "magnesium", "magnezium"]),
    ("vitamins_minerals", "Vitaminy a minerály", ["vitamin", "multivit", "zinek", "železo", "zelezo", "vápník", "vapnik", "minerál"]),
    ("beauty", "Krása, vlasy a pleť", ["beauty", "kolagen", "vlasy", "nehty", "pleť", "plet", "pokož", "revitalon"]),
    ("joints", "Klouby a pohyb", ["kloub", "artivit", "motion", "vazy", "šlach", "slach"]),
    ("digestion", "Trávení a probiotika", ["tráven", "traven", "probiotik", "střeva", "streva", "vláknin"]),
    ("detox", "Játra a detox", ["detox", "játra", "jatra", "jater", "odkysel"]),
    ("heart", "Srdce a oběh", ["srdce", "oběh", "obeh", "omega", "koenzym", "q10"]),
    ("eyes", "Zrak", ["zrak", "oči", "oci", "lutein"]),
    ("urinary", "Močové cesty", ["moč", "moc", "brusink"]),
    ("hydration", "Hydratace a nápoje", ["rehydrat", "nápoj", "napoj", "pitný", "pitny", "capri", "ovocé"]),
    ("sweeteners", "Sladidla", ["irbis", "sladid", "stevie", "sukral", "aspartam", "sacharin"]),
    ("dextrose", "Hroznový cukr a cukrovinky", ["energit", "hroznový cukr", "hroznovy cukr", "dextróz", "dextroz"]),
    ("hangover", "Vyprošťovák", ["vyprošťovák", "vyprostovak"]),
]

FORM_RULES = [
    ("effervescent_tablets", "Šumivé tablety", ["šumiv", "sumiv", "effervescent"]),
    ("gummies", "Želé / gummies", ["želé", "zele", "gumm"]),
    ("capsules", "Kapsle", ["kapsl", "cps"]),
    ("tablets", "Tablety", ["tablet", " tbl"]),
    ("stick", "Stick pack", ["stick"]),
    ("drops", "Kapky", ["kapky"]),
    ("spray", "Sprej", ["sprej", "spray"]),
    ("syrup", "Sirup / elixír", ["sirup", "elixír", "elixir"]),
    ("powder", "Prášek", ["prášek", "prasek", "sypká", "sypka"]),
    ("drink", "Nápoj", ["nápoj", "napoj", "shot", "0,2 l", "0,33 l"]),
    ("cosmetic", "Kosmetika", ["šampon", "sampon", "sérum", "serum", "vazelína", "vazelina", "gel"]),
]

CONTENT_PATH_WORDS = {
    "o-nas",
    "kontakt",
    "kariera",
    "gdpr",
    "obchodni-podminky",
    "ochrana-osobnich-udaju",
    "doprava-a-platba",
    "reklamacni-rad",
    "zasady",
    "soutez",
    "aktuality",
    "clanky",
}

session_local = threading.local()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_space(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalized_key(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("maxivita", "maxi vita")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return normalize_space(value)


def slug(value: str) -> str:
    return normalized_key(value).replace(" ", "-")


def digits(value: Any) -> str:
    return re.sub(r"\D", "", str(value or ""))


def parse_price(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"([0-9][0-9\s\u00a0]*(?:[,.][0-9]{1,2})?)", str(value))
    if not match:
        return None
    number = match.group(1).replace(" ", "").replace("\u00a0", "").replace(",", ".")
    try:
        return float(number)
    except ValueError:
        return None


def get_session() -> requests.Session:
    if not hasattr(session_local, "session"):
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; VitarAssortmentAudit/2.0; "
                    "+https://github.com/jurajgiacko/vitar-assortment-workbench)"
                )
            }
        )
        session_local.session = session
    return session_local.session


def request(url: str, timeout: int = 45) -> requests.Response:
    response = get_session().get(url, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    return response


def sitemap_entries(url: str, seen: set[str] | None = None) -> list[dict[str, str]]:
    seen = seen or set()
    if url in seen:
        return []
    seen.add(url)
    response = request(url)
    root = ET.fromstring(response.content)
    entries: list[dict[str, str]] = []
    if root.tag.endswith("sitemapindex"):
        for node in root:
            loc = next((normalize_space(x.text) for x in node if x.tag.endswith("loc")), "")
            if loc:
                entries.extend(sitemap_entries(loc, seen))
        return entries
    for node in root:
        loc = next((normalize_space(x.text) for x in node if x.tag.endswith("loc")), "")
        lastmod = next((normalize_space(x.text) for x in node if x.tag.endswith("lastmod")), "")
        if loc:
            entries.append({"url": loc, "lastmod": lastmod})
    return entries


def meta(soup: BeautifulSoup, selector: str, attr: str = "content") -> str:
    tag = soup.select_one(selector)
    return normalize_space(tag.get(attr, "")) if tag else ""


def text_of(tag: Tag | None) -> str:
    return normalize_space(tag.get_text(" ", strip=True)) if tag else ""


def parse_jsonld(soup: BeautifulSoup) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []

    def add(value: Any) -> None:
        if isinstance(value, dict):
            objects.append(value)
            graph = value.get("@graph")
            if isinstance(graph, list):
                for child in graph:
                    add(child)
        elif isinstance(value, list):
            for child in value:
                add(child)

    for tag in soup.select('script[type="application/ld+json"]'):
        raw = tag.string or tag.get_text()
        if not raw.strip():
            continue
        try:
            add(json.loads(raw))
        except (json.JSONDecodeError, TypeError):
            continue
    return objects


def detect_brand(name: str, url: str, manufacturer: str = "") -> str:
    haystack = normalized_key(f"{name} {url} {manufacturer}")
    for brand in BRANDS:
        if normalized_key(brand) in haystack:
            if brand == "Maxivita":
                return "Maxi Vita"
            if brand in {"VITAR Veterinae", "Veterinae"}:
                return "Vitar Veterinae"
            if brand in {"VITAR Origin", "Vitar Origin"}:
                return "Vitar Origin"
            if brand == "Vyprostovak":
                return "Vyprošťovák"
            if brand == "VITAR":
                return "Vitar"
            return brand
    return normalize_space(manufacturer) or "Neurčeno"


def detect_category(product: dict[str, Any]) -> dict[str, Any]:
    haystack = normalized_key(
        " ".join(
            [
                product.get("name", ""),
                product.get("description", ""),
                product.get("brand", ""),
                " ".join(product.get("breadcrumbs", [])),
                " ".join(product.get("category_paths", [])),
            ]
        )
    )
    matches = []
    for index, (key, label, words) in enumerate(CATEGORY_RULES):
        score = sum(1 for word in words if normalized_key(word) in haystack)
        if score:
            matches.append((score, -index, key, label))
    if not matches:
        return {"key": "unclassified", "label": "Nezařazeno", "confidence": "low"}
    matches.sort(reverse=True)
    score, _, key, label = matches[0]
    return {"key": key, "label": label, "confidence": "high" if score >= 2 else "medium"}


def detect_form(product: dict[str, Any]) -> dict[str, str]:
    haystack = normalized_key(
        " ".join(
            [
                product.get("name", ""),
                product.get("description", ""),
                json.dumps(product.get("attributes", {}), ensure_ascii=False),
            ]
        )
    )
    for key, label, words in FORM_RULES:
        if any(normalized_key(word) in haystack for word in words):
            return {"key": key, "label": label}
    return {"key": "unknown", "label": "Neurčeno"}


def base_product(site: Site, url: str, soup: BeautifulSoup) -> dict[str, Any]:
    canonical = soup.select_one('link[rel="canonical"]')
    return {
        "source_id": hashlib.sha1(f"{site.domain}:{url}".encode()).hexdigest()[:16],
        "source_key": site.key,
        "source_site": site.domain,
        "url": url,
        "canonical_url": normalize_space(canonical.get("href")) if canonical else url,
        "slug": urlparse(url).path.strip("/"),
        "name": "",
        "brand": "Neurčeno",
        "manufacturer": "",
        "sku": "",
        "ean": "",
        "price_czk": None,
        "availability": "",
        "description": "",
        "images": [],
        "breadcrumbs": [],
        "category_paths": [],
        "attributes": {},
        "content_sections": {},
        "outbound_product_urls": [],
        "seo": {
            "title": text_of(soup.title),
            "meta_description": meta(soup, 'meta[name="description"]'),
            "og_title": meta(soup, 'meta[property="og:title"]'),
            "og_image": meta(soup, 'meta[property="og:image"]'),
        },
    }


def finish_product(product: dict[str, Any]) -> dict[str, Any]:
    product["name"] = normalize_space(product.get("name"))
    product["sku"] = normalize_space(product.get("sku"))
    product["ean"] = digits(product.get("ean"))
    product["images"] = list(dict.fromkeys(x for x in product.get("images", []) if x))
    product["brand"] = detect_brand(
        product["name"], product["url"], product.get("manufacturer", "")
    )
    product["category_recommendation"] = detect_category(product)
    product["form_recommendation"] = detect_form(product)
    product["quality"] = {
        "has_name": bool(product["name"]),
        "has_sku": bool(product["sku"]),
        "has_ean": len(product["ean"]) >= 8,
        "has_price": product.get("price_czk") is not None,
        "has_image": bool(product["images"]),
        "has_description": len(product.get("description", "")) >= 40,
        "has_long_content": sum(len(v) for v in product.get("content_sections", {}).values()) >= 250,
    }
    return product


def parse_vitar_product(site: Site, url: str, soup: BeautifulSoup) -> dict[str, Any]:
    product = base_product(site, url, soup)
    view = soup.select_one(".product-view")
    attrs: dict[str, str] = {}
    for wrap in soup.select(".option-wrap"):
        label = text_of(wrap.select_one(".option-label")).strip(":")
        value = text_of(wrap.select_one(".option-content"))
        if label and value:
            attrs[label] = value
    sections: dict[str, str] = {}
    for heading in soup.select(".product-view-bottom h2, .product-view-bottom h3, .productInfo h3"):
        title = text_of(heading)
        sibling = heading.find_next_sibling()
        content = text_of(sibling if isinstance(sibling, Tag) else None)
        if title and len(content) >= 30:
            sections[title] = content[:12000]
    if not sections and view:
        content = text_of(view.select_one(".product-view-bottom"))
        if len(content) >= 80:
            sections["Popis produktu"] = content[:20000]
    images = [meta(soup, 'meta[property="og:image"]')]
    for image in soup.select(".product-view img")[:12]:
        source = normalize_space(image.get("data-src") or image.get("src"))
        if source:
            images.append(urljoin(url, source))
    product.update(
        {
            "name": text_of(view.select_one("h1") if view else soup.select_one("h1")),
            "manufacturer": attrs.get("Výrobce", ""),
            "sku": attrs.get("Kód", "") or attrs.get("SKU", ""),
            "ean": attrs.get("EAN", ""),
            "price_czk": parse_price(attrs.get("Běžná cena") or attrs.get("Cena")),
            "availability": text_of(soup.select_one(".availability, .stock, .product-stock")),
            "description": product["seo"]["meta_description"],
            "images": images,
            "breadcrumbs": [
                text_of(item).rstrip(" /")
                for item in soup.select(".breadcrumbs li, .breadcrumb li")
                if text_of(item)
            ],
            "attributes": attrs,
            "content_sections": sections,
        }
    )
    product["category_paths"] = product["breadcrumbs"][1:-1]
    return finish_product(product)


def parse_nase_product(site: Site, url: str, soup: BeautifulSoup) -> dict[str, Any]:
    product = base_product(site, url, soup)
    product_ld = next(
        (obj for obj in parse_jsonld(soup) if str(obj.get("@type", "")).lower() == "product"),
        {},
    )
    info: dict[str, str] = {}
    for node in soup.select(".vc-commoditydetail_info dl"):
        label = text_of(node.select_one("dt"))
        value = text_of(node.select_one("dd"))
        if label and value:
            info[label] = value
    offers = product_ld.get("offers") if isinstance(product_ld.get("offers"), dict) else {}
    spec = offers.get("priceSpecification") if isinstance(offers, dict) else {}
    spec = spec if isinstance(spec, dict) else {}
    images = product_ld.get("image", [])
    if isinstance(images, str):
        images = [images]
    sections: dict[str, str] = {}
    description_box = soup.select_one(".vc-commoditydetail_description")
    if description_box:
        headings = description_box.select("h2, h3, h4")
        for heading in headings:
            title = text_of(heading)
            chunks: list[str] = []
            sibling = heading.find_next_sibling()
            while isinstance(sibling, Tag) and sibling.name not in {"h2", "h3", "h4"}:
                value = text_of(sibling)
                if value:
                    chunks.append(value)
                sibling = sibling.find_next_sibling()
            content = normalize_space(" ".join(chunks))
            if title and len(content) >= 30:
                sections[title] = content[:12000]
        whole = text_of(description_box)
        if not sections and len(whole) >= 80:
            sections["Popis produktu"] = whole[:20000]
    categories = [text_of(x) for x in soup.select(".vc-commoditydetail_categories a") if text_of(x)]
    name = normalize_space(product_ld.get("name")) or text_of(soup.select_one("h1"))
    description = normalize_space(product_ld.get("description")) or product["seo"]["meta_description"]
    product.update(
        {
            "name": name,
            "canonical_url": normalize_space(product_ld.get("url")) or product["canonical_url"],
            "manufacturer": info.get("Výrobce", ""),
            "sku": product_ld.get("productID", "") or info.get("Kód", ""),
            "ean": product_ld.get("gtin13", "") or product_ld.get("gtin", "") or info.get("EAN", ""),
            "price_czk": parse_price(spec.get("price")) or parse_price(soup.select_one("[data-price]").get("data-price") if soup.select_one("[data-price]") else None),
            "availability": info.get("Dostupnost", ""),
            "description": description,
            "images": list(images) + [product["seo"]["og_image"]],
            "breadcrumbs": [text_of(x) for x in soup.select("#breadcrumbs li") if text_of(x)],
            "category_paths": categories,
            "attributes": info,
            "content_sections": sections,
        }
    )
    return finish_product(product)


def parse_ceske_product(site: Site, url: str, soup: BeautifulSoup) -> dict[str, Any]:
    product = base_product(site, url, soup)
    main = soup.select_one("main") or soup.body
    sections: dict[str, str] = {}
    if main:
        for heading in main.select("h2, h3"):
            title = text_of(heading)
            chunks: list[str] = []
            sibling = heading.find_next_sibling()
            while isinstance(sibling, Tag) and sibling.name not in {"h2", "h3"}:
                value = text_of(sibling)
                if value:
                    chunks.append(value)
                sibling = sibling.find_next_sibling()
            content = normalize_space(" ".join(chunks))
            if title and len(content) >= 30:
                sections[title] = content[:12000]
    outbound = []
    for anchor in soup.select("a[href]"):
        href = urljoin(url, normalize_space(anchor.get("href")))
        if "nasevitaminy.cz" in href or "vitar.cz" in href:
            outbound.append(href)
    images = [product["seo"]["og_image"]]
    for image in soup.select("main img, body img")[:20]:
        source = normalize_space(image.get("src"))
        if source and not source.startswith("data:"):
            images.append(urljoin(url, source))
    product_slug = urlparse(url).path.rstrip("/").split("/")[-1]
    product_names = {
        "alphamale": "AlphaMale",
        "fembalance": "FemBalance",
        "goddess": "Goddess",
        "magnesium-bisglycinate": "Magnesium Bisglycinate",
        "magnesium-malate": "Magnesium Malate",
        "motion-plus": "Motion+",
        "regensleep": "RegenSleep",
    }
    profile_name = product_names.get(product_slug, text_of(soup.select_one("h1")))
    product.update(
        {
            "name": f"Maxi Vita Essentials {profile_name}",
            "description": product["seo"]["meta_description"],
            "images": images,
            "category_paths": ["Maxi Vita Essentials"],
            "content_sections": sections,
            "outbound_product_urls": list(dict.fromkeys(outbound)),
        }
    )
    return finish_product(product)


def classify_page(site: Site, url: str, soup: BeautifulSoup) -> str:
    body_classes = set(soup.body.get("class", [])) if soup.body else set()
    path = urlparse(url).path.strip("/").lower()
    if site.key == "vitar" and (
        "catalog-product-view" in body_classes or soup.select_one(".product-view")
    ):
        return "product"
    if site.key == "nasevitaminy" and (
        "view-commodity-detail" in body_classes or soup.select_one(".commodityDetail")
    ):
        return "product"
    if site.key == "ceskevitaminy" and path.startswith("produkty/"):
        return "product_profile"
    if not path:
        return "homepage"
    if path in {"produkty", "znacky"} or path.startswith(("produkty/", "znacky/", "homepage")):
        return "category_or_landing"
    if any(word in path for word in CONTENT_PATH_WORDS):
        return "content"
    if soup.select_one("article") or "blog" in path or "aktualit" in path:
        return "content"
    return "other"


def crawl_one(site: Site, entry: dict[str, str], refresh: bool) -> tuple[dict[str, Any], dict[str, Any] | None]:
    url = entry["url"]
    cache_dir = RAW_DIR / site.key
    cache_path = cache_dir / f"{hashlib.sha1(url.encode()).hexdigest()}.html"
    inventory: dict[str, Any] = {
        "source_key": site.key,
        "source_site": site.domain,
        "url": url,
        "sitemap_lastmod": entry.get("lastmod", ""),
        "status": "pending",
        "page_type": "unknown",
        "http_status": None,
        "final_url": "",
        "title": "",
        "canonical_url": "",
        "content_hash": "",
        "error": "",
    }
    try:
        if cache_path.exists() and not refresh:
            html = cache_path.read_text(encoding="utf-8")
            final_url = url
            http_status = 200
        else:
            response = request(url)
            html = response.text
            final_url = response.url
            http_status = response.status_code
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(html, encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        page_type = classify_page(site, final_url, soup)
        canonical = soup.select_one('link[rel="canonical"]')
        inventory.update(
            {
                "status": "ok",
                "page_type": page_type,
                "http_status": http_status,
                "final_url": final_url,
                "title": text_of(soup.title),
                "canonical_url": normalize_space(canonical.get("href")) if canonical else final_url,
                "content_hash": hashlib.sha256(html.encode()).hexdigest(),
            }
        )
        product = None
        if page_type == "product":
            product = (
                parse_vitar_product(site, final_url, soup)
                if site.key == "vitar"
                else parse_nase_product(site, final_url, soup)
            )
        elif page_type == "product_profile":
            product = parse_ceske_product(site, final_url, soup)
        return inventory, product
    except Exception as exc:  # noqa: BLE001 - every failed URL belongs in the audit
        inventory.update({"status": "error", "page_type": "error", "error": str(exc)})
        return inventory, None


class DisjointSet:
    def __init__(self, values: Iterable[str]):
        self.parent = {value: value for value in values}

    def find(self, value: str) -> str:
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left: str, right: str) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def unique_values(products: list[dict[str, Any]], field: str) -> list[Any]:
    values = []
    for product in products:
        value = product.get(field)
        if value not in (None, "", []) and value not in values:
            values.append(value)
    return values


def assortment_recommendation(product: dict[str, Any]) -> dict[str, Any]:
    brand = product.get("brand", "")
    category = product.get("category", {}).get("key", "")
    name_key = normalized_key(product.get("name", ""))
    if category == "veterina" or brand == "Vitar Veterinae":
        return {
            "channels": ["vitar_veterina"],
            "confidence": "high",
            "reason": "Veterinární portfolio je samostatná business unit a e-shop.",
        }
    if brand in {"Energit", "Vitar Kings"}:
        return {
            "channels": ["review"],
            "confidence": "low",
            "reason": "Rozhodnout mezi VITAR.cz a NašeVitamíny.cz podle pozice, ceny a cílové skupiny.",
        }
    if brand in {"Maxi Vita Essentials", "Vitar Origin", "Revital Botanicals"}:
        return {
            "channels": ["vitar.cz", "nasevitaminy.cz"],
            "primary": "vitar.cz",
            "confidence": "medium",
            "reason": "Prémiová nebo nová řada patří do hero nabídky VITAR.cz; druhý listing je k rozhodnutí.",
        }
    if brand in {"Predator", "Irbis", "Capri-Sun"}:
        return {
            "channels": ["review"],
            "confidence": "low",
            "reason": "Portfolio je mimo hlavní health proposition; nutné obchodní rozhodnutí.",
        }
    if brand in {"Maxi Vita", "Revital", "eMVe"}:
        return {
            "channels": ["nasevitaminy.cz"],
            "primary": "nasevitaminy.cz",
            "confidence": "medium",
            "reason": "Retailová klasika a cenově dostupné řady odpovídají roli NašeVitamíny.cz.",
        }
    if "wip" in name_key:
        return {"channels": ["review"], "confidence": "low", "reason": "WIP produkt vyžaduje vlastní návrh."}
    return {
        "channels": ["review"],
        "confidence": "low",
        "reason": "Bez automatického rozhodnutí; zařadit v domácí úloze.",
    }


def build_master(products: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_id = {product["source_id"]: product for product in products}
    dsu = DisjointSet(by_id)
    match_events: list[dict[str, Any]] = []

    identifier_ambiguities: list[dict[str, Any]] = []

    def union_index(field: str, normalizer, reason: str) -> None:
        index: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for product in products:
            value = normalizer(product.get(field, ""))
            if value:
                index[value].append(product)
        for value, matches in index.items():
            for left_index, left in enumerate(matches):
                for right in matches[left_index + 1 :]:
                    if left["source_key"] == right["source_key"]:
                        continue
                    left_sku, right_sku = normalize_space(left.get("sku")), normalize_space(right.get("sku"))
                    left_ean, right_ean = digits(left.get("ean")), digits(right.get("ean"))
                    if field == "ean" and left_sku and right_sku and left_sku != right_sku:
                        identifier_ambiguities.append(
                            {
                                "left": left["source_id"],
                                "right": right["source_id"],
                                "method": reason,
                                "value": value,
                                "reason": "same_ean_different_sku",
                            }
                        )
                        continue
                    if field == "name" and (
                        (left_sku and right_sku and left_sku != right_sku)
                        or (left_ean and right_ean and left_ean != right_ean)
                    ):
                        identifier_ambiguities.append(
                            {
                                "left": left["source_id"],
                                "right": right["source_id"],
                                "method": reason,
                                "value": value,
                                "reason": "same_name_different_identifier",
                            }
                        )
                        continue
                    dsu.union(left["source_id"], right["source_id"])
                    match_events.append(
                        {
                            "left": left["source_id"],
                            "right": right["source_id"],
                            "method": reason,
                            "value": value,
                            "confidence": "high",
                        }
                    )

    union_index("ean", lambda x: digits(x) if len(digits(x)) >= 8 else "", "exact_ean")
    union_index("sku", lambda x: normalize_space(x), "exact_sku")
    union_index("name", normalized_key, "exact_name")

    url_index: dict[str, str] = {}
    for product in products:
        url_index[urlparse(product["url"]).path.strip("/").lower()] = product["source_id"]
        url_index[urlparse(product.get("canonical_url", "")).path.strip("/").lower()] = product["source_id"]
    for product in products:
        if product["source_key"] != "ceskevitaminy":
            continue
        for outbound in product.get("outbound_product_urls", []):
            target = url_index.get(urlparse(outbound).path.strip("/").lower())
            if target and target != product["source_id"]:
                dsu.union(product["source_id"], target)
                match_events.append(
                    {
                        "left": product["source_id"],
                        "right": target,
                        "method": "explicit_outbound_url",
                        "value": outbound,
                        "confidence": "high",
                    }
                )

    fuzzy_suggestions: list[dict[str, Any]] = []
    commerce = [p for p in products if p["source_key"] != "ceskevitaminy"]
    for profile in [p for p in products if p["source_key"] == "ceskevitaminy"]:
        if any(event["left"] == profile["source_id"] for event in match_events):
            continue
        scored = sorted(
            [
                (
                    SequenceMatcher(None, normalized_key(profile["name"]), normalized_key(candidate["name"])).ratio(),
                    candidate,
                )
                for candidate in commerce
            ],
            key=lambda item: item[0],
            reverse=True,
        )
        if not scored:
            continue
        best_score, best = scored[0]
        margin = best_score - (scored[1][0] if len(scored) > 1 else 0)
        suggestion = {
            "source_id": profile["source_id"],
            "candidate_source_id": best["source_id"],
            "score": round(best_score, 4),
            "margin": round(margin, 4),
            "status": "manual_review",
        }
        fuzzy_suggestions.append(suggestion)
        if best_score >= 0.86 and margin >= 0.08:
            dsu.union(profile["source_id"], best["source_id"])
            suggestion["status"] = "auto_accepted"
            match_events.append(
                {
                    "left": profile["source_id"],
                    "right": best["source_id"],
                    "method": "high_confidence_name_similarity",
                    "value": round(best_score, 4),
                    "confidence": "medium",
                }
            )

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for product in products:
        groups[dsu.find(product["source_id"])].append(product)

    masters: list[dict[str, Any]] = []
    used_master_ids: set[str] = set()
    source_rank = {"vitar": 0, "nasevitaminy": 1, "ceskevitaminy": 2}
    for grouped in groups.values():
        grouped.sort(key=lambda item: source_rank[item["source_key"]])
        primary = grouped[0]
        eans = unique_values(grouped, "ean")
        skus = unique_values(grouped, "sku")
        names = unique_values(grouped, "name")
        descriptions = sorted(
            [x.get("description", "") for x in grouped if x.get("description")], key=len, reverse=True
        )
        category_candidates = [x["category_recommendation"] for x in grouped]
        category_candidates.sort(
            key=lambda value: {"high": 2, "medium": 1, "low": 0}.get(value["confidence"], 0),
            reverse=True,
        )
        master_key = eans[0] if eans else (skus[0] if skus else normalized_key(primary["name"]))
        master_id = "prd_" + hashlib.sha1(master_key.encode()).hexdigest()[:12]
        if master_id in used_master_ids:
            disambiguator = ":".join(sorted(item["source_id"] for item in grouped))
            master_id = "prd_" + hashlib.sha1(f"{master_key}:{disambiguator}".encode()).hexdigest()[:12]
        used_master_ids.add(master_id)
        fields_with_conflicts = []
        for field, values in {"name": names, "sku": skus, "ean": eans, "brand": unique_values(grouped, "brand")}.items():
            if len(values) > 1:
                severity = "high" if field in {"sku", "ean"} else "info"
                if field == "brand":
                    severity = "medium"
                if field == "name":
                    similarities = [
                        SequenceMatcher(None, normalized_key(values[0]), normalized_key(value)).ratio()
                        for value in values[1:]
                    ]
                    severity = "high" if similarities and min(similarities) < 0.5 else "info"
                fields_with_conflicts.append({"field": field, "values": values, "severity": severity})
        source_summary = [
            {
                "source_id": item["source_id"],
                "source_key": item["source_key"],
                "source_site": item["source_site"],
                "url": item["url"],
                "name": item["name"],
                "sku": item["sku"],
                "ean": item["ean"],
                "price_czk": item["price_czk"],
                "image": item["images"][0] if item["images"] else "",
                "description": item["description"],
                "content_sections": item["content_sections"],
                "quality": item["quality"],
            }
            for item in grouped
        ]
        master = {
            "id": master_id,
            "name": names[0] if names else primary["name"],
            "brand": primary["brand"],
            "sku": skus[0] if skus else "",
            "ean": eans[0] if eans else "",
            "category": category_candidates[0],
            "form": primary["form_recommendation"],
            "description": descriptions[0] if descriptions else "",
            "image": next((item["images"][0] for item in grouped if item["images"]), ""),
            "price_czk": next(
                (item["price_czk"] for item in grouped if item["price_czk"] is not None), None
            ),
            "source_count": len(grouped),
            "source_keys": sorted({item["source_key"] for item in grouped}),
            "sources": source_summary,
            "field_conflicts": fields_with_conflicts,
            "coverage": {
                "vitar": any(item["source_key"] == "vitar" for item in grouped),
                "nasevitaminy": any(item["source_key"] == "nasevitaminy" for item in grouped),
                "ceskevitaminy": any(item["source_key"] == "ceskevitaminy" for item in grouped),
            },
            "quality": {
                "has_sku": bool(skus),
                "has_ean": bool(eans),
                "has_image": any(item["quality"]["has_image"] for item in grouped),
                "has_description": any(item["quality"]["has_description"] for item in grouped),
                "has_long_content": any(item["quality"]["has_long_content"] for item in grouped),
                "has_price": any(item["quality"]["has_price"] for item in grouped),
                "has_conflict": any(item["severity"] == "high" for item in fields_with_conflicts),
                "has_variation": bool(fields_with_conflicts),
            },
            "system_recommendation": {},
            "lifecycle": "live",
            "review_status": "unreviewed",
        }
        master["system_recommendation"] = assortment_recommendation(master)
        masters.append(master)

    masters.sort(key=lambda product: (normalized_key(product["brand"]), normalized_key(product["name"])))
    matching = {
        "match_events": match_events,
        "identifier_ambiguities": identifier_ambiguities,
        "fuzzy_suggestions": fuzzy_suggestions,
        "unmatched_ceskevitaminy": [
            product["source_id"]
            for product in products
            if product["source_key"] == "ceskevitaminy"
            and len(groups[dsu.find(product["source_id"])]) == 1
        ],
    }
    return masters, matching


def compact_product(master: dict[str, Any]) -> dict[str, Any]:
    return {
        key: master[key]
        for key in [
            "id",
            "name",
            "brand",
            "sku",
            "ean",
            "category",
            "form",
            "description",
            "image",
            "price_czk",
            "source_count",
            "source_keys",
            "sources",
            "field_conflicts",
            "coverage",
            "quality",
            "system_recommendation",
            "lifecycle",
            "review_status",
        ]
    }


def write_outputs(
    crawl_started_at: str,
    inventory: list[dict[str, Any]],
    products: list[dict[str, Any]],
    masters: list[dict[str, Any]],
    matching: dict[str, Any],
    sitemap_counts: dict[str, int],
) -> None:
    CURRENT_DIR.mkdir(parents=True, exist_ok=True)
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    page_type_counts = Counter((item["source_key"], item["page_type"]) for item in inventory)
    status_counts = Counter(item["status"] for item in inventory)
    coverage_by_site = {}
    for site_key, sitemap_count in sitemap_counts.items():
        site_inventory = [item for item in inventory if item["source_key"] == site_key]
        coverage_by_site[site_key] = {
            "sitemap_urls": sitemap_count,
            "inventory_urls": len(site_inventory),
            "ok": sum(item["status"] == "ok" for item in site_inventory),
            "errors": sum(item["status"] == "error" for item in site_inventory),
            "products": sum(item["page_type"] in {"product", "product_profile"} for item in site_inventory),
            "page_types": {
                page_type: count
                for (key, page_type), count in page_type_counts.items()
                if key == site_key
            },
            "reconciled": sitemap_count == len(site_inventory),
        }
    summary = {
        "crawl_started_at": crawl_started_at,
        "generated_at": utc_now(),
        "coverage": coverage_by_site,
        "inventory_status": dict(status_counts),
        "source_products": len(products),
        "master_products": len(masters),
        "duplicates_merged": len(products) - len(masters),
        "by_brand": dict(Counter(master["brand"] for master in masters)),
        "by_category": dict(Counter(master["category"]["label"] for master in masters)),
        "quality": {
            key: sum(bool(master["quality"].get(key)) for master in masters)
            for key in [
                "has_sku",
                "has_ean",
                "has_image",
                "has_description",
                "has_long_content",
                "has_price",
                "has_conflict",
            ]
        },
        "matching": {
            "events": len(matching["match_events"]),
            "manual_fuzzy_reviews": sum(
                item["status"] == "manual_review" for item in matching["fuzzy_suggestions"]
            ),
            "unmatched_ceskevitaminy": len(matching["unmatched_ceskevitaminy"]),
        },
    }
    crawl_bundle = {
        "summary": summary,
        "url_inventory": inventory,
        "source_products": products,
    }
    catalog_bundle = {
        "summary": summary,
        "products": masters,
        "matching_audit": matching,
    }
    (CURRENT_DIR / "crawl.json").write_text(
        json.dumps(crawl_bundle, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CURRENT_DIR / "catalog.json").write_text(
        json.dumps(catalog_bundle, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CURRENT_DIR / "coverage-report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (APP_DATA_DIR / "catalog.json").write_text(
        json.dumps(
            {"summary": summary, "products": [compact_product(master) for master in masters]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    with (CURRENT_DIR / "catalog.csv").open("w", newline="", encoding="utf-8-sig") as file:
        columns = [
            "id",
            "name",
            "brand",
            "sku",
            "ean",
            "category",
            "form",
            "price_czk",
            "vitar",
            "nasevitaminy",
            "ceskevitaminy",
            "recommendation",
            "recommendation_reason",
            "source_count",
            "has_conflict",
        ]
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for master in masters:
            writer.writerow(
                {
                    "id": master["id"],
                    "name": master["name"],
                    "brand": master["brand"],
                    "sku": master["sku"],
                    "ean": master["ean"],
                    "category": master["category"]["label"],
                    "form": master["form"]["label"],
                    "price_czk": master["price_czk"],
                    "vitar": master["coverage"]["vitar"],
                    "nasevitaminy": master["coverage"]["nasevitaminy"],
                    "ceskevitaminy": master["coverage"]["ceskevitaminy"],
                    "recommendation": ", ".join(master["system_recommendation"].get("channels", [])),
                    "recommendation_reason": master["system_recommendation"].get("reason", ""),
                    "source_count": master["source_count"],
                    "has_conflict": master["quality"]["has_conflict"],
                }
            )
    lines = [
        "# Crawl coverage report",
        "",
        f"Generated: {summary['generated_at']}",
        f"Source records: {summary['source_products']}",
        f"Master products: {summary['master_products']}",
        "",
        "## Source reconciliation",
        "",
        "| Source | Sitemap | Inventory | OK | Errors | Products | Reconciled |",
        "| --- | ---: | ---: | ---: | ---: | ---: | :---: |",
    ]
    for site_key, values in coverage_by_site.items():
        lines.append(
            f"| {site_key} | {values['sitemap_urls']} | {values['inventory_urls']} | "
            f"{values['ok']} | {values['errors']} | {values['products']} | "
            f"{'yes' if values['reconciled'] else 'NO'} |"
        )
    lines.extend(
        [
            "",
            "## Matching controls",
            "",
            f"- Explicit match events: {summary['matching']['events']}",
            f"- Manual fuzzy reviews: {summary['matching']['manual_fuzzy_reviews']}",
            f"- Unmatched CeskeVitaminy profiles: {summary['matching']['unmatched_ceskevitaminy']}",
            f"- Master field conflicts: {summary['quality']['has_conflict']}",
            "",
            "A reconciled sitemap proves that every published URL was classified. It does not prove that every ERP SKU is online; ERP reconciliation remains a separate gate.",
            "",
        ]
    )
    (CURRENT_DIR / "coverage-report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", choices=["all", *SITES.keys()], default="all")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    crawl_started_at = utc_now()
    selected = list(SITES.values()) if args.site == "all" else [SITES[args.site]]
    jobs: list[tuple[Site, dict[str, str]]] = []
    sitemap_counts: dict[str, int] = {}
    for site in selected:
        entries = sitemap_entries(site.sitemap)
        if args.limit:
            entries = entries[: args.limit]
        sitemap_counts[site.key] = len(entries)
        jobs.extend((site, entry) for entry in entries)
        print(f"[{site.key}] sitemap URLs: {len(entries)}", flush=True)

    inventory: list[dict[str, Any]] = []
    products: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {
            pool.submit(crawl_one, site, entry, args.refresh): (site, entry)
            for site, entry in jobs
        }
        completed = 0
        for future in as_completed(futures):
            site, entry = futures[future]
            completed += 1
            try:
                page, product = future.result()
            except Exception as exc:  # pragma: no cover - last-resort accounting
                page = {
                    "source_key": site.key,
                    "source_site": site.domain,
                    "url": entry["url"],
                    "status": "error",
                    "page_type": "error",
                    "error": str(exc),
                }
                product = None
            inventory.append(page)
            if product:
                products.append(product)
            if completed % 25 == 0 or completed == len(jobs):
                errors = sum(item["status"] == "error" for item in inventory)
                print(
                    f"crawl {completed}/{len(jobs)} products={len(products)} errors={errors}",
                    flush=True,
                )

    inventory.sort(key=lambda item: (item["source_key"], item["url"]))
    products.sort(key=lambda item: (item["source_key"], item["url"]))
    masters, matching = build_master(products)
    write_outputs(crawl_started_at, inventory, products, masters, matching, sitemap_counts)
    errors = [item for item in inventory if item["status"] == "error"]
    print(
        json.dumps(
            {
                "sitemap_counts": sitemap_counts,
                "source_products": len(products),
                "master_products": len(masters),
                "errors": len(errors),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
