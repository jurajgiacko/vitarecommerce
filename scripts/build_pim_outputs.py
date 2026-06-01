#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "products.json"
OUT = ROOT / "outputs"
REPORTS = OUT / "reports"
HTML = OUT / "html"
PROCESSED = ROOT / "data" / "processed"
PUBLIC_DATA = OUT / "data"


SEO_TEMPLATES = {
    "Imunita a nachlazení": {
        "h1": "Imunita a nachlazení",
        "title": "Vitamíny na imunitu a nachlazení | Vitar",
        "description": "Doplňky stravy pro podporu imunity: vitamin C, zinek, rakytník, betaglukany a bylinné produkty pro dospělé i děti.",
    },
    "Hořčík a minerály": {
        "h1": "Hořčík a minerály",
        "title": "Hořčík, zinek, vápník a minerály | Vitar",
        "description": "Minerální látky ve formě tablet, kapslí, šumivých tablet a stick packů. Vyberte podle účinku, formy a věku.",
    },
    "Krása, vlasy, pleť": {
        "h1": "Vlasy, nehty, pleť a krása",
        "title": "Kolagen, biotin a péče o vlasy, nehty a pleť | Vitar",
        "description": "Beauty doplňky s kolagenem, kyselinou hyaluronovou, koenzymem Q10, zinkem a vitaminy pro každodenní péči.",
    },
    "Energie, stres, spánek": {
        "h1": "Energie, stres a spánek",
        "title": "Doplňky pro energii, stres a klidný spánek | Vitar",
        "description": "Produkty pro únavu, psychickou pohodu, soustředění a spánek: hořčík, B-komplex, ashwagandha a bylinné kombinace.",
    },
    "Děti": {
        "h1": "Vitamíny pro děti",
        "title": "Vitamíny a doplňky pro děti | Vitar Kids a Maxi Vita Kids",
        "description": "Dětské multivitaminy, omega-3, betaglukany, probiotika a želé/tabletové formy pro školáky i menší děti.",
    },
}

COMPETITOR_NOTES = [
    {
        "name": "GymBeam",
        "url": "https://gymbeam.cz/vitaminy/bez-prichuti",
        "takeaway": "Hloubková navigace podle typu látky i cíle: imunita, spánek, vlasy/nehty/pokožka, stres, trávení, játra, nootropika.",
    },
    {
        "name": "Vilgain",
        "url": "https://vilgain.com/essential-vitamins-and-minerals/brand/vilgain",
        "takeaway": "Používá kombinaci produktových a lifestyle filtrů: sale, new, in stock, vegan, gluten-free, caffeine-free, lactose-free.",
    },
    {
        "name": "iHerb",
        "url": "https://www.iherb.com/c/Multivitamins",
        "takeaway": "Silná dôvera cez kvalitu: iTested, nezávislé laboratóriá, heavy metals/microbial testing a kategórie podľa segmentu.",
    },
    {
        "name": "BrainMarket",
        "url": "https://www.brainmarket.cz/doplnky-stravy/?pv462=5214",
        "takeaway": "Navigácia delí doplnky podľa cieľa, typu vitamínu a segmentu: deti, muži, ženy, imunita, omega, probiotiká.",
    },
]

FILTER_MODEL = [
    {"field": "brand", "label": "Značka / produktová řada", "source": "Vitar portfolio + GymBeam/BrainMarket brand navigation pattern", "priority": "P0", "ui": "top navigation + filter", "seo": "indexable brand pages"},
    {"field": "category_recommendation", "label": "Hlavní potřeba", "source": "GymBeam and BrainMarket goal-based navigation", "priority": "P0", "ui": "main navigation after brands", "seo": "indexable category landings"},
    {"field": "form", "label": "Forma", "source": "PIM attribute, visible competitor pattern", "priority": "P0", "ui": "facet filter", "seo": "noindex, selected curated landings only"},
    {"field": "active_ingredients", "label": "Aktivní látky", "source": "manual/PIM enrichment, common supplement shopping behavior", "priority": "P0", "ui": "facet filter + search synonyms", "seo": "curated landings for vitamin C, magnesium, collagen, omega-3, D3/K2"},
    {"field": "target_group", "label": "Cílová skupina", "source": "iHerb/BrainMarket segment navigation", "priority": "P0", "ui": "facet filter", "seo": "curated landings for děti, ženy, muži, senioři"},
    {"field": "age_group", "label": "Věk", "source": "children/senior supplement segmentation", "priority": "P1", "ui": "facet filter", "seo": "noindex except selected child/senior pages"},
    {"field": "diet_flags", "label": "Bez cukru / vegan / gluten-free / lactose-free", "source": "Vilgain lifestyle filters", "priority": "P1", "ui": "facet filter", "seo": "noindex"},
    {"field": "pack_size", "label": "Velikost balení", "source": "scraped attributes", "priority": "P1", "ui": "facet filter or product comparison only", "seo": "noindex"},
    {"field": "flavour", "label": "Příchuť", "source": "name extraction + PIM enrichment", "priority": "P1", "ui": "facet filter for drinks/effervescent only", "seo": "noindex"},
    {"field": "availability", "label": "Skladem / dostupnost", "source": "NašeVitamíny commerce data + iHerb available items pattern", "priority": "P1", "ui": "toggle", "seo": "noindex"},
    {"field": "price_per_unit", "label": "Cena za dávku / kus", "source": "commerce calculation", "priority": "P2", "ui": "sort/comparison, not a primary facet", "seo": "noindex"},
    {"field": "quality_claims", "label": "Certifikace/testování/kvalita", "source": "iHerb iTested trust pattern", "priority": "P2", "ui": "trust badge + facet only when data exists", "seo": "supporting content, not filter SEO"},
]

SUPPRESSED_FILTERS = [
    {"label": "Výrobce jako samostatný e-shop filter", "reason": "Většina portfolia je VITAR, s.r.o.; používat raději značku/produktovou řadu."},
    {"label": "Interní SKU/EAN jako facet", "reason": "Patří do search/admin view, ne do zákaznické filtrace."},
    {"label": "Cena jako rozsahový slider", "reason": "U doplňků s nízkou cenovou disperzí má menší hodnotu než cena za dávku a řazení."},
    {"label": "Duplicitní kombinace brand + potřeba jako indexované URL", "reason": "Riziko thin/duplicate SEO. Indexovat jen ručně vybrané landing pages."},
    {"label": "Veterinae v hlavní Vitar kategorii", "reason": "Jiný shopper intent; držet jako oddělený sortiment mimo hlavní lidské doplňky."},
]


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))["products"]


def is_veterinary(product):
    return product.get("brand") == "Vitar Veterinae" or product["category_recommendation"]["label"] == "Veterinae a zvířata"


def scope_for(product):
    if is_veterinary(product):
        return {
            "key": "separate_veterinary",
            "label": "Veterinae - samostatný sortiment",
            "main_navigation": False,
            "note": "Vyčlenit mimo hlavní strukturu VITAR doplňků pro lidi; držet jako separátní portfolio/sekci.",
        }
    return {
        "key": "main_vitar",
        "label": "Hlavní VITAR sortiment",
        "main_navigation": True,
        "note": "Produkty pro hlavní e-shopovou navigaci podle značky a potřeby.",
    }


def master_products(products):
    grouped = defaultdict(list)
    for product in products:
        key = product.get("ean") or product.get("sku") or product["product_id"]
        grouped[key].append(product)
    masters = []
    for key, records in grouped.items():
        records = sorted(records, key=lambda x: 0 if x["source_site"] == "nasevitaminy.cz" else 1)
        primary = dict(records[0])
        primary["source_records"] = [
            {
                "source_site": r["source_site"],
                "url": r["url"],
                "sku": r.get("sku"),
                "ean": r.get("ean"),
                "has_price": r.get("price_czk") is not None,
            }
            for r in records
        ]
        primary["duplicate_count"] = len(records)
        vitar = next((r for r in records if r["source_site"] == "vitar.cz"), None)
        shop = next((r for r in records if r["source_site"] == "nasevitaminy.cz"), None)
        if shop:
            primary.update({k: shop[k] for k in ["price_czk", "availability"] if k in shop})
        if vitar and len(vitar.get("description", "")) > len(primary.get("description", "")):
            primary["description"] = vitar["description"]
        primary["assortment_scope"] = scope_for(primary)
        primary["pim_recommendation"] = {
            "master_key": key,
            "import_priority": "Separate" if primary["assortment_scope"]["key"] == "separate_veterinary" else ("P0" if primary["category_recommendation"]["label"] in {"Imunita a nachlazení", "Hořčík a minerály", "Děti", "Krása, vlasy, pleť"} else "P1"),
            "canonical_source": "nasevitaminy.cz for price/availability, vitar.cz for brand/category content",
            "needs_manual_enrichment": missing_enrichment(primary),
        }
        masters.append(primary)
    return sorted(masters, key=lambda x: (x["assortment_scope"]["key"], x["brand"], x["category_recommendation"]["label"], x["name"]))


def missing_enrichment(product):
    missing = []
    if not product.get("ean"):
        missing.append("ean")
    if product["form"]["key"] == "unknown":
        missing.append("form")
    if not product.get("need_states"):
        missing.append("need_states")
    missing.extend(["active_ingredients", "dosage", "target_group", "contraindications", "health_claims"])
    return missing


def category_rows(products):
    by_cat = defaultdict(list)
    for p in products:
        if p["assortment_scope"]["key"] != "main_vitar":
            continue
        by_cat[p["category_recommendation"]["label"]].append(p)
    rows = []
    for cat, items in sorted(by_cat.items(), key=lambda kv: len(kv[1]), reverse=True):
        brands = Counter(i["brand"] for i in items).most_common(5)
        forms = Counter(i["form"]["label"] for i in items).most_common(5)
        rows.append({
            "category": cat,
            "count": len(items),
            "brands": brands,
            "forms": forms,
            "seo": SEO_TEMPLATES.get(cat, {
                "h1": cat,
                "title": f"{cat} | Vitar",
                "description": f"Produkty Vitar v kategorii {cat.lower()} přehledně podle značky, formy, aktivní látky a cílové skupiny.",
            }),
        })
    return rows


def brand_rows(products):
    by_brand = defaultdict(list)
    for p in products:
        if p["assortment_scope"]["key"] == "main_vitar":
            by_brand[p["brand"]].append(p)
    rows = []
    preferred_order = [
        "Maxi Vita", "Vitar", "Maxi Vita Essentials", "Revital", "Revital Botanicals",
        "Energit", "Predator", "Capri-Sun", "Vitar Kids", "Vitar Eko", "Revitalon",
        "Irbis", "eMVe", "OvoCé", "Vyprošťovák", "Vitar Kings",
    ]
    for brand in preferred_order:
        items = by_brand.pop(brand, [])
        if items:
            rows.append(brand_row(brand, items))
    for brand, items in sorted(by_brand.items(), key=lambda kv: len(kv[1]), reverse=True):
        rows.append(brand_row(brand, items))
    return rows


def brand_row(brand, items):
    categories = Counter(i["category_recommendation"]["label"] for i in items).most_common(4)
    forms = Counter(i["form"]["label"] for i in items).most_common(4)
    return {
        "brand": brand,
        "count": len(items),
        "categories": categories,
        "forms": forms,
        "role": brand_role(brand),
    }


def brand_role(brand):
    roles = {
        "Maxi Vita": "Core vitamin/mineral umbrella; primary brand landing.",
        "Vitar": "Functional legacy products and pharmacy staples.",
        "Maxi Vita Essentials": "Modern premium/lifestyle sub-brand; strong for segmented landings.",
        "Revital": "Effervescent/value vitamin line.",
        "Revital Botanicals": "Botanical/effervescent sub-line; use as brand plus format story.",
        "Energit": "Energy/glucose/dextrose; separate sport/energy intent.",
        "Predator": "Repellents and parasite protection; seasonal separate cluster.",
        "Capri-Sun": "Beverage/distribution portfolio; keep outside supplement taxonomy where needed.",
        "Vitar Kids": "Kids portfolio; brand and target-group landing.",
        "Vitar Eko": "Eco/natural positioning; support with quality and ingredient filters.",
        "Revitalon": "Hair/beauty line; beauty category + brand landing.",
        "Irbis": "Sweeteners; separate food/sweetener cluster.",
        "eMVe": "Value vitamin line; brand filter, lower SEO priority.",
        "OvoCé": "Powdered drink range; drinks/pitný režim.",
        "Vyprošťovák": "Hangover micro-brand; campaign/seasonal landing.",
        "Vitar Kings": "Male/lifestyle line; target group male.",
    }
    return roles.get(brand, "Portfolio brand; keep as filter and evaluate SEO demand.")


def separate_assortments(products):
    veterinary = [p for p in products if p["assortment_scope"]["key"] == "separate_veterinary"]
    return [
        {
            "key": "separate_veterinary",
            "label": "Veterinae - samostatný sortiment",
            "count": len(veterinary),
            "recommendation": "Zobrazit jako separátní sekci/portfolio mimo hlavní VITAR strom pro lidské doplňky. V PIM ponechat stejné produktové atributy, ale navigačně a SEO oddělit.",
            "top_forms": Counter(p["form"]["label"] for p in veterinary).most_common(5),
        }
    ]


def write_json(products, masters, categories, brands, separate):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_records": len(products),
        "master_products": len(masters),
        "duplicate_raw_records": len(products) - len(masters),
        "main_products": sum(1 for p in masters if p["assortment_scope"]["key"] == "main_vitar"),
        "separate_products": sum(1 for p in masters if p["assortment_scope"]["key"] != "main_vitar"),
        "brands": brands,
        "categories": categories,
        "separate_assortments": separate,
        "filters": FILTER_MODEL,
        "suppressed_filters": SUPPRESSED_FILTERS,
        "competitor_notes": COMPETITOR_NOTES,
        "products": masters,
    }
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    (PROCESSED / "pim-master.json").write_text(payload_json, encoding="utf-8")
    (PUBLIC_DATA / "pim-master.json").write_text(payload_json, encoding="utf-8")
    return payload


def write_report(payload):
    REPORTS.mkdir(parents=True, exist_ok=True)
    products = payload["products"]
    main_products = [p for p in products if p["assortment_scope"]["key"] == "main_vitar"]
    lines = [
        "# VITAR ecommerce PIM preparation",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Executive Summary",
        "",
        f"- Scraped raw product records: {payload['raw_records']}",
        f"- Recommended master products after SKU/EAN dedupe: {payload['master_products']}",
        f"- Main VITAR human supplement assortment: {payload['main_products']} master products",
        f"- Separate/non-main assortment: {payload['separate_products']} master products",
        f"- Cross-site duplicate records merged: {payload['duplicate_raw_records']}",
        "- Recommended source strategy: NašeVitamíny for commerce fields, VITAR.cz for brand/content enrichment.",
        "",
        "## Portfolio Structure",
        "",
        "Recommended navigation order: separate portfolios first for governance visibility, then brand-led entry points, then customer-need categories. Veterinary products should be present in PIM and reporting, but excluded from the main VITAR human supplement taxonomy.",
        "",
        "| Separate portfolio | Products | Recommendation | Top forms |",
        "|---|---:|---|---|",
    ]
    def cell(value):
        return str(value).replace("|", "\\|")

    for row in payload["separate_assortments"]:
        forms = ", ".join(f"{b} ({c})" for b, c in row["top_forms"])
        lines.append(f"| {cell(row['label'])} | {row['count']} | {cell(row['recommendation'])} | {cell(forms)} |")
    lines.extend([
        "",
        "### Brand Navigation",
        "",
        "| Brand | Products | Role | Top categories | Top forms |",
        "|---|---:|---|---|---|",
    ])
    for row in payload["brands"]:
        categories = ", ".join(f"{b} ({c})" for b, c in row["categories"])
        forms = ", ".join(f"{b} ({c})" for b, c in row["forms"])
        lines.append(f"| {cell(row['brand'])} | {row['count']} | {cell(row['role'])} | {cell(categories)} | {cell(forms)} |")
    lines.extend([
        "",
        "## Category Management Recommendation",
        "",
        "Use a hybrid model: top-level brand entry points for recognisable VITAR lines, then main category navigation by customer need. Keep brands indexable where they carry demand, but let filters and category pages solve shopping intent.",
        "",
        "| Category | Products | Top brands | Top forms | SEO title |",
        "|---|---:|---|---|---|",
    ])

    for row in payload["categories"]:
        brands = ", ".join(f"{b} ({c})" for b, c in row["brands"])
        forms = ", ".join(f"{b} ({c})" for b, c in row["forms"])
        lines.append(f"| {cell(row['category'])} | {row['count']} | {cell(brands)} | {cell(forms)} | {cell(row['seo']['title'])} |")
    lines.extend([
        "",
        "## Filter Model for PIM",
        "",
        "| Priority | Filter | PIM field | UI behavior | SEO behavior | Source |",
        "|---|---|---|---|---|---|",
    ])
    for f in payload["filters"]:
        lines.append(f"| {f['priority']} | {cell(f['label'])} | `{f['field']}` | {cell(f['ui'])} | {cell(f['seo'])} | {cell(f['source'])} |")
    lines.extend([
        "",
        "### Filters to suppress or keep out",
        "",
        "| Filter / URL pattern | Why remove or suppress |",
        "|---|---|",
    ])
    for f in payload["suppressed_filters"]:
        lines.append(f"| {cell(f['label'])} | {cell(f['reason'])} |")
    lines.extend([
        "",
        "## SEO Setup",
        "",
        "- Build indexable brand pages first for core demand: Maxi Vita, Vitar, Revital, Energit, Predator, Vitar Kids, Maxi Vita Essentials and selected micro-brands.",
        "- Build one indexable landing page per customer need in the main assortment: immunity, magnesium/minerals, kids, beauty, joints, digestion/detox, energy/stress/sleep, eyes, heart, urinary, drinks and sweeteners.",
        "- Keep Veterinae/Veterinary as a separate portfolio. It can have its own landing and product URLs, but it should not appear in the main VITAR human supplement category tree.",
        "- Use noindex/follow for combinatorial filter URLs, except curated SEO landings such as `vitamin-c`, `horcik`, `kolagen`, `vitaminy-pro-deti`, `repelenty-pro-deti`.",
        "- Product pages need structured data: Product, Offer, Brand, AggregateRating where available, BreadcrumbList and FAQ for claims/dosage questions.",
        "",
        "## Competitor Patterns Used",
        "",
    ])
    for note in payload["competitor_notes"]:
        lines.append(f"- [{note['name']}]({note['url']}): {note['takeaway']}")
    lines.extend([
        "",
        "## Data Quality Risks",
        "",
        f"- Missing EAN: {sum(1 for p in products if not p.get('ean'))}/{len(products)} master products.",
        f"- Unknown form: {sum(1 for p in products if p['form']['key'] == 'unknown')}/{len(products)} master products.",
        f"- Main taxonomy excludes {len(products) - len(main_products)} separate products by design; keep them visible in admin/PIM QA.",
        "- Active ingredients, dosage, health claims and contraindications require manual or NLP-assisted enrichment before final PIM import.",
        "- Some VITAR content is richer than NašeVitamíny product text; merge descriptions deliberately instead of overwriting.",
        "",
        "## Development Handoff",
        "",
        "- Use `data/processed/pim-master.json` as the development seed.",
        "- Use `data/processed/products.csv` for quick spreadsheet review.",
        "- Use `outputs/pim-product-cards/*.md` for per-product editorial review.",
        "- Use `outputs/html/vitar-category-planner.html` as the interactive category-management view.",
    ])
    (REPORTS / "pim-category-management-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload):
    HTML.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VITAR - PIM Category Planner</title>
<style>
:root {{ --bg:#f6f7f9; --panel:#fff; --line:#dfe3e8; --text:#1d2430; --muted:#667085; --accent:#27704a; --accent2:#235f9e; --warn:#b45309; --bad:#b42318; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); }}
header {{ position:sticky; top:0; z-index:10; background:var(--panel); border-bottom:1px solid var(--line); padding:14px 22px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
h1 {{ font-size:18px; margin:0; font-weight:650; }}
button, select, input {{ font:inherit; }}
.actions {{ display:flex; gap:8px; align-items:center; }}
.btn {{ border:1px solid var(--line); background:#f2f4f7; border-radius:6px; padding:7px 11px; cursor:pointer; }}
.btn.primary {{ background:var(--accent); color:white; border-color:var(--accent); }}
.stats {{ display:flex; gap:22px; padding:10px 22px; border-bottom:1px solid var(--line); background:var(--panel); color:var(--muted); font-size:13px; flex-wrap:wrap; }}
.stats b {{ color:var(--text); }}
.layout {{ display:grid; grid-template-columns:310px 1fr; min-height:calc(100vh - 90px); }}
aside {{ background:var(--panel); border-right:1px solid var(--line); padding:16px; overflow:auto; }}
main {{ padding:18px; overflow:auto; }}
.section-title {{ font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); margin:12px 0 8px; font-weight:700; }}
.cat {{ display:flex; justify-content:space-between; align-items:center; gap:10px; padding:7px 9px; border-radius:6px; cursor:pointer; font-size:13px; }}
.cat:hover, .cat.active {{ background:#e9f5ee; color:#14532d; }}
.cat.separate:hover, .cat.separate.active {{ background:#fef3c7; color:#92400e; }}
.count {{ color:var(--muted); background:#eef1f4; border-radius:12px; padding:1px 7px; font-size:11px; }}
.tabs {{ display:flex; gap:6px; flex-wrap:wrap; margin-bottom:14px; }}
.tab {{ border:1px solid var(--line); background:var(--panel); padding:8px 12px; border-radius:6px; cursor:pointer; color:var(--muted); }}
.tab.active {{ background:var(--accent2); color:white; border-color:var(--accent2); }}
.toolbar {{ display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap; }}
.toolbar input, .toolbar select {{ border:1px solid var(--line); border-radius:6px; padding:8px 10px; background:white; min-width:180px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(360px,1fr)); gap:10px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px; display:grid; grid-template-columns:74px 1fr; gap:12px; min-height:130px; }}
.card img {{ width:74px; height:74px; object-fit:contain; background:#f8fafc; border:1px solid var(--line); border-radius:6px; }}
.name {{ font-weight:650; font-size:14px; margin-bottom:3px; }}
.meta {{ color:var(--muted); font-size:12px; line-height:1.55; }}
.pillrow {{ display:flex; flex-wrap:wrap; gap:4px; margin-top:8px; }}
.pill {{ font-size:11px; padding:2px 7px; border-radius:999px; background:#eef2ff; color:#344054; }}
.pill.p0 {{ background:#dcfce7; color:#166534; }}
.pill.warn {{ background:#fef3c7; color:#92400e; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
th, td {{ text-align:left; border-bottom:1px solid var(--line); padding:9px 10px; font-size:13px; vertical-align:top; }}
th {{ background:#f2f4f7; color:#475467; font-weight:650; }}
.panel {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px; margin-bottom:12px; }}
.panel h2 {{ font-size:16px; margin:0 0 8px; }}
textarea {{ width:100%; min-height:300px; border:1px solid var(--line); border-radius:8px; padding:12px; font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12px; }}
@media (max-width: 860px) {{ .layout {{ grid-template-columns:1fr; }} aside {{ border-right:0; border-bottom:1px solid var(--line); }} .card {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
  <h1>VITAR <span style="color:var(--accent)">PIM Category Planner</span></h1>
  <div class="actions">
    <button class="btn" onclick="exportData('json')">JSON</button>
    <button class="btn" onclick="exportData('md')">Markdown</button>
    <button class="btn primary" onclick="setTab('products')">Products</button>
  </div>
</header>
<div class="stats" id="stats"></div>
<div class="layout">
  <aside>
    <div class="section-title">Separate portfolio</div>
    <div id="separate"></div>
    <div class="section-title">Brands</div>
    <div id="brands"></div>
    <div class="section-title">Main categories</div>
    <div id="cats"></div>
  </aside>
  <main>
    <div class="tabs">
      <button class="tab active" data-tab="products" onclick="setTab('products')">Products</button>
      <button class="tab" data-tab="taxonomy" onclick="setTab('taxonomy')">Taxonomy</button>
      <button class="tab" data-tab="filters" onclick="setTab('filters')">Filters</button>
      <button class="tab" data-tab="seo" onclick="setTab('seo')">SEO</button>
      <button class="tab" data-tab="competitors" onclick="setTab('competitors')">Competitors</button>
      <button class="tab" data-tab="export" onclick="setTab('export')">Export</button>
    </div>
    <div id="view"></div>
  </main>
</div>
<script>
const DATA = {data};
let currentTab = 'products';
let scope = 'main_vitar';
let category = 'all';
let brand = 'all';
let query = '';

function countBy(items, fn) {{
  const map = new Map();
  items.forEach(x => map.set(fn(x), (map.get(fn(x)) || 0) + 1));
  return [...map.entries()].sort((a,b) => b[1]-a[1]);
}}
function filtered() {{
  return DATA.products.filter(p =>
    (scope === 'all' || p.assortment_scope.key === scope) &&
    (category === 'all' || p.category_recommendation.label === category) &&
    (brand === 'all' || p.brand === brand) &&
    (!query || (p.name + ' ' + p.sku + ' ' + p.ean + ' ' + p.description).toLowerCase().includes(query.toLowerCase()))
  );
}}
function scopedProducts() {{
  return DATA.products.filter(p => scope === 'all' || p.assortment_scope.key === scope);
}}
function mainProducts() {{
  return DATA.products.filter(p => p.assortment_scope.key === 'main_vitar');
}}
function renderStats() {{
  document.getElementById('stats').innerHTML = `
    <span><b>${{DATA.master_products}}</b> master products</span>
    <span><b>${{DATA.main_products}}</b> main VITAR</span>
    <span><b>${{DATA.separate_products}}</b> separate</span>
    <span><b>${{DATA.brands.length}}</b> brands</span>
    <span><b>${{DATA.raw_records}}</b> raw records</span>
    <span><b>${{DATA.duplicate_raw_records}}</b> merged duplicates</span>
    <span><b>${{DATA.filters.length}}</b> PIM filters</span>`;
}}
function setScope(next) {{
  scope = next;
  category = 'all';
  brand = 'all';
  renderAll();
}}
function setCategory(next) {{
  scope = 'main_vitar';
  category = next;
  renderAll();
}}
function setBrand(next) {{
  scope = 'main_vitar';
  brand = next;
  renderAll();
}}
function renderSide() {{
  const scopes = [
    ['main_vitar', 'Main VITAR assortment', DATA.main_products],
    ...DATA.separate_assortments.map(s => [s.key, s.label + ' bokom', s.count])
  ];
  document.getElementById('separate').innerHTML = scopes.map(([key,label,n]) => `<div class="cat ${{key !== 'main_vitar' && key !== 'all' ? 'separate' : ''}} ${{scope===key?'active':''}}" onclick='setScope(${{JSON.stringify(key)}})'><span>${{label}}</span><span class="count">${{n}}</span></div>`).join('');
  const productsForSide = mainProducts();
  const catRows = [['all', DATA.main_products], ...DATA.categories.map(c => [c.category, c.count])];
  document.getElementById('cats').innerHTML = catRows.map(([c,n]) => `<div class="cat ${{category===c?'active':''}}" onclick='setCategory(${{JSON.stringify(c)}})'><span>${{c==='all'?'All main categories':c}}</span><span class="count">${{n}}</span></div>`).join('');
  const brands = [['all', DATA.main_products], ...DATA.brands.map(b => [b.brand, b.count])];
  document.getElementById('brands').innerHTML = brands.map(([b,n]) => `<div class="cat ${{brand===b?'active':''}}" onclick='setBrand(${{JSON.stringify(b)}})'><span>${{b==='all'?'All brands':b}}</span><span class="count">${{n}}</span></div>`).join('');
}}
function setTab(tab) {{
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  renderView();
}}
function productCard(p) {{
  const miss = p.pim_recommendation.needs_manual_enrichment.slice(0, 4);
  return `<article class="card">
    <img src="${{p.image || ''}}" alt="">
    <div>
      <div class="name">${{p.name}}</div>
      <div class="meta">${{p.brand}} · SKU ${{p.sku || '-'}} · EAN ${{p.ean || '-'}}<br>${{p.category_recommendation.label}} · ${{p.form.label}} · ${{p.price_czk ? p.price_czk + ' Kč' : 'bez ceny'}}</div>
      <div class="pillrow">
        <span class="pill p0">${{p.pim_recommendation.import_priority}}</span>
        <span class="pill ${{p.assortment_scope.key === 'main_vitar' ? '' : 'warn'}}">${{p.assortment_scope.label}}</span>
        <span class="pill">${{p.duplicate_count}} source${{p.duplicate_count>1?'s':''}}</span>
        ${{miss.map(m => `<span class="pill warn">${{m}}</span>`).join('')}}
      </div>
    </div>
  </article>`;
}}
function renderProducts() {{
  const list = filtered();
  const scopeOptions = [['main_vitar','Main VITAR assortment'], ...DATA.separate_assortments.map(s => [s.key, s.label + ' bokom'])];
  const modeNote = scope === 'main_vitar'
    ? 'Main category and brand filters are scoped to the VITAR human supplement assortment.'
    : 'Separate portfolio view: this is kept outside the main category tree.';
  return `<div class="toolbar">
    <input placeholder="Search name, SKU, EAN..." value="${{query}}" oninput="query=this.value;renderView()">
    <select onchange="setScope(this.value)">${{scopeOptions.map(([k,l])=>`<option ${{scope===k?'selected':''}} value="${{k}}">${{l}}</option>`).join('')}}</select>
    <select onchange="setCategory(this.value)">${{['all',...DATA.categories.map(c=>c.category)].map(c=>`<option ${{category===c?'selected':''}} value="${{c}}">${{c==='all'?'All categories':c}}</option>`).join('')}}</select>
    <select onchange="setBrand(this.value)">${{['all',...DATA.brands.map(b=>b.brand)].map(b=>`<option ${{brand===b?'selected':''}} value="${{b}}">${{b==='all'?'All brands':b}}</option>`).join('')}}</select>
  </div><div class="meta" style="margin-bottom:10px">${{list.length}} visible products · ${{modeNote}}</div><div class="grid">${{list.map(productCard).join('')}}</div>`;
}}
function renderTaxonomy() {{
  return `<div class="panel"><h2>Separate portfolio</h2><div class="meta">These products stay visible for PIM and admin planning, but outside the main VITAR human supplement taxonomy.</div></div>
  <table><thead><tr><th>Portfolio</th><th>Products</th><th>Recommendation</th><th>Top forms</th></tr></thead><tbody>${{DATA.separate_assortments.map(s => `<tr><td><b>${{s.label}}</b></td><td>${{s.count}}</td><td>${{s.recommendation}}</td><td>${{s.top_forms.map(x=>x[0]+' ('+x[1]+')').join(', ')}}</td></tr>`).join('')}}</tbody></table>
  <div class="panel" style="margin-top:12px"><h2>Brand navigation first</h2><div class="meta">Use these as top entry points and brand landings, then let the customer choose categories and filters underneath.</div></div>
  <table><thead><tr><th>Brand</th><th>Products</th><th>Role</th><th>Top categories</th><th>Top forms</th></tr></thead><tbody>${{DATA.brands.map(b => `<tr><td><b>${{b.brand}}</b></td><td>${{b.count}}</td><td>${{b.role}}</td><td>${{b.categories.map(x=>x[0]+' ('+x[1]+')').join(', ')}}</td><td>${{b.forms.map(x=>x[0]+' ('+x[1]+')').join(', ')}}</td></tr>`).join('')}}</tbody></table>
  <div class="panel" style="margin-top:12px"><h2>Main categories below brands</h2><div class="meta">Customer-need categories exclude Veterinae and other separate portfolio products.</div></div>
  <table><thead><tr><th>Category</th><th>Products</th><th>Top brands</th><th>Top forms</th><th>SEO H1</th></tr></thead><tbody>${{DATA.categories.map(c => `<tr><td><b>${{c.category}}</b></td><td>${{c.count}}</td><td>${{c.brands.map(x=>x[0]+' ('+x[1]+')').join(', ')}}</td><td>${{c.forms.map(x=>x[0]+' ('+x[1]+')').join(', ')}}</td><td>${{c.seo.h1}}</td></tr>`).join('')}}</tbody></table>`;
}}
function renderFilters() {{
  return `<div class="panel"><h2>Recommended filter stack</h2><div class="meta">P0 filters are launch-critical. P1 filters need clean PIM data before exposing broadly. P2 filters are useful, but should not drive the main navigation.</div></div>
  <table><thead><tr><th>Priority</th><th>Filter</th><th>Field</th><th>UI</th><th>SEO</th><th>Source</th></tr></thead><tbody>${{DATA.filters.map(f => `<tr><td><b>${{f.priority}}</b></td><td>${{f.label}}</td><td><code>${{f.field}}</code></td><td>${{f.ui}}</td><td>${{f.seo}}</td><td>${{f.source}}</td></tr>`).join('')}}</tbody></table>
  <div class="panel" style="margin-top:12px"><h2>Suppress / remove</h2><div class="meta">These facets or URL patterns create noise, duplicate SEO, or poor shopper value.</div></div>
  <table><thead><tr><th>Filter / pattern</th><th>Reason</th></tr></thead><tbody>${{DATA.suppressed_filters.map(f => `<tr><td><b>${{f.label}}</b></td><td>${{f.reason}}</td></tr>`).join('')}}</tbody></table>`;
}}
function renderSeo() {{
  return `<div class="panel"><h2>SEO routing principle</h2><div class="meta">Index brand pages and curated customer-need category pages. Keep combinatorial filters noindex/follow unless a filtered state has real demand and curated content. Veterinae can have its own landing, but remains outside the main VITAR human supplement tree.</div></div>` +
    DATA.categories.map(c => `<div class="panel"><h2>${{c.category}}</h2><div class="meta"><b>Title:</b> ${{c.seo.title}}<br><b>Meta:</b> ${{c.seo.description}}</div></div>`).join('');
}}
function renderCompetitors() {{
  return DATA.competitor_notes.map(n => `<div class="panel"><h2><a href="${{n.url}}" target="_blank">${{n.name}}</a></h2><div class="meta">${{n.takeaway}}</div></div>`).join('');
}}
function exportData(format) {{
  setTab('export');
  const out = document.getElementById('exportBox');
  if (!out) return;
  out.value = format === 'json' ? JSON.stringify(DATA, null, 2) : [
    '# VITAR PIM planner',
    '',
    '## Separate portfolio',
    ...DATA.separate_assortments.map(s => `- ${{s.label}}: ${{s.count}} products. ${{s.recommendation}}`),
    '',
    '## Brands',
    ...DATA.brands.map(b => `- ${{b.brand}}: ${{b.count}} products. ${{b.role}}`),
    '',
    '## Main categories',
    ...DATA.categories.map(c => `- ${{c.category}}: ${{c.count}} products. SEO title: ${{c.seo.title}}`),
    '',
    '## Filters',
    ...DATA.filters.map(f => `- [${{f.priority}}] ${{f.label}} (${{f.field}}): ${{f.ui}} / ${{f.seo}}`),
  ].join('\\n');
}}
function renderExport() {{
  return `<div class="panel"><h2>Export</h2><textarea id="exportBox">${{JSON.stringify(DATA, null, 2)}}</textarea></div>`;
}}
function renderView() {{
  const v = document.getElementById('view');
  if (currentTab === 'products') v.innerHTML = renderProducts();
  if (currentTab === 'taxonomy') v.innerHTML = renderTaxonomy();
  if (currentTab === 'filters') v.innerHTML = renderFilters();
  if (currentTab === 'seo') v.innerHTML = renderSeo();
  if (currentTab === 'competitors') v.innerHTML = renderCompetitors();
  if (currentTab === 'export') v.innerHTML = renderExport();
}}
function renderAll() {{ renderStats(); renderSide(); renderView(); }}
renderAll();
</script>
</body>
</html>
"""
    (HTML / "vitar-category-planner.html").write_text(html, encoding="utf-8")


def main():
    products = load()
    masters = master_products(products)
    categories = category_rows(masters)
    brands = brand_rows(masters)
    separate = separate_assortments(masters)
    payload = write_json(products, masters, categories, brands, separate)
    write_report(payload)
    write_html(payload)
    print(json.dumps({
        "raw_records": payload["raw_records"],
        "master_products": payload["master_products"],
        "main_products": payload["main_products"],
        "separate_products": payload["separate_products"],
        "brands": len(payload["brands"]),
        "categories": len(payload["categories"]),
        "html": str(HTML / "vitar-category-planner.html"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
