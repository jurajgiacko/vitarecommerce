#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "outputs"
PUBLIC_DATA = OUT / "data"
REPORTS = OUT / "reports"
HTML = OUT / "html"

PRODUCT_QA = PUBLIC_DATA / "product-qa.json"
PIM_MASTER = PUBLIC_DATA / "pim-master.json"
GROUP_PAGES = PUBLIC_DATA / "vitar-group-pages.json"
CONTENT_PAGES = PUBLIC_DATA / "content-pages.json"


PIM_ATTRIBUTE_MODEL = [
    {"group": "Identity", "field": "master_key", "priority": "P0", "owner": "PIM/Data", "source": "EAN/SKU dedupe", "note": "Stable product master identifier."},
    {"group": "Identity", "field": "sku", "priority": "P0", "owner": "PIM/Data", "source": "vitar.cz + nasevitaminy.cz", "note": "Required for import, ERP and stock joins."},
    {"group": "Identity", "field": "ean", "priority": "P0", "owner": "PIM/Data", "source": "nasevitaminy.cz preferred", "note": "Required for marketplaces, feeds and retail consistency."},
    {"group": "Portfolio", "field": "sbu_owner", "priority": "P0", "owner": "VITAR GROUP", "source": "governance decision", "note": "Main VITAR, Sport, Veterina, Pharma/MaxFarma, OEM/B2B, exclude."},
    {"group": "Portfolio", "field": "brand_architecture_role", "priority": "P0", "owner": "CMO/Brand", "source": "approved brand architecture", "note": "Hero, top-tier, mass-market, legacy, separate BU."},
    {"group": "Merchandising", "field": "category", "priority": "P0", "owner": "E-commerce", "source": "QA proposed category", "note": "Customer navigation category, not necessarily internal taxonomy."},
    {"group": "Merchandising", "field": "need_state", "priority": "P0", "owner": "E-commerce/Content", "source": "PIM enrichment", "note": "Immunity, sleep, magnesium, beauty, urinary, joints, children."},
    {"group": "Merchandising", "field": "active_ingredients", "priority": "P0", "owner": "Product/Regulatory", "source": "label/content extraction + review", "note": "Must support ingredient search and comparison."},
    {"group": "Product facts", "field": "form", "priority": "P0", "owner": "PIM/Data", "source": "cross-source QA", "note": "Tablets, capsules, effervescent, syrup, powder, drink, cosmetic."},
    {"group": "Product facts", "field": "dosage", "priority": "P0", "owner": "Product/Regulatory", "source": "label/content extraction + review", "note": "Needed for product page, structured data and customer trust."},
    {"group": "Product facts", "field": "pack_size", "priority": "P1", "owner": "PIM/Data", "source": "scraped attributes", "note": "Units, grams, ml, number of tablets/capsules."},
    {"group": "Product facts", "field": "flavour", "priority": "P1", "owner": "PIM/Data", "source": "name/content extraction", "note": "Important for drinks, effervescent tablets and kids products."},
    {"group": "Audience", "field": "target_group", "priority": "P0", "owner": "E-commerce/Regulatory", "source": "PIM enrichment", "note": "Children, women, men, seniors, sport, pets."},
    {"group": "Audience", "field": "age_group", "priority": "P1", "owner": "Product/Regulatory", "source": "manual review", "note": "Expose only where approved and useful."},
    {"group": "Trust", "field": "claims", "priority": "P0", "owner": "Regulatory/Legal", "source": "approved label claims", "note": "Prevent overclaiming before content migration."},
    {"group": "Trust", "field": "warnings", "priority": "P0", "owner": "Regulatory/Legal", "source": "label/content extraction + review", "note": "Contraindications, dosage warnings, pregnancy/kids warnings."},
    {"group": "Trust", "field": "quality_proof", "priority": "P1", "owner": "Quality/CMO", "source": "certificates/lab proof", "note": "Supports premium positioning and VITAR GROUP trust story."},
    {"group": "Commerce", "field": "price", "priority": "P0", "owner": "E-commerce", "source": "nasevitaminy.cz / new platform", "note": "Current VITAR.cz often lacks commerce price."},
    {"group": "Commerce", "field": "availability", "priority": "P0", "owner": "E-commerce/Ops", "source": "nasevitaminy.cz / new platform", "note": "Required for feeds and UX."},
    {"group": "Commerce", "field": "cross_sell_matrix", "priority": "P1", "owner": "E-commerce/AI", "source": "manual + analytics later", "note": "Bundles, alternatives, complementary products."},
    {"group": "SEO", "field": "canonical_url", "priority": "P0", "owner": "SEO/E-commerce", "source": "migration mapping", "note": "Old to new product/category/content URL decisions."},
    {"group": "SEO", "field": "structured_data", "priority": "P1", "owner": "Dev/SEO", "source": "platform implementation", "note": "Product, Offer, Brand, BreadcrumbList, FAQ where applicable."},
]


BACKLOG = [
    {"epic": "Assortment governance", "task": "Lock final SBU ownership for every SKU", "priority": "P0", "owner": "VITAR GROUP + E-commerce", "status": "next", "deliverable": "Approved governance matrix"},
    {"epic": "Assortment governance", "task": "Approve products excluded from main VITAR.cz", "priority": "P0", "owner": "E-commerce + CMO", "status": "next", "deliverable": "Exclude/accessory decision list"},
    {"epic": "Assortment governance", "task": "Confirm VITAR Sport split for Enervit/Royal Bay/compression items", "priority": "P0", "owner": "VITAR Sport", "status": "next", "deliverable": "Sport SBU product list"},
    {"epic": "Veterina separation", "task": "Confirm VITAR Veterina domain and platform direction", "priority": "P0", "owner": "VITAR Veterina", "status": "next", "deliverable": "Separate e-shop decision"},
    {"epic": "PIM model", "task": "Approve launch PIM attribute schema", "priority": "P0", "owner": "PIM/Data + E-commerce", "status": "ready_for_review", "deliverable": "PIM attribute model v1"},
    {"epic": "PIM model", "task": "Merge recoverable missing form fields from vitar.cz into master PIM", "priority": "P0", "owner": "PIM/Data", "status": "next", "deliverable": "114 cross-source form enrichments"},
    {"epic": "PIM model", "task": "Extract dosage, active ingredients, warnings and approved claims", "priority": "P0", "owner": "Product/Regulatory", "status": "next", "deliverable": "Regulatory-safe product facts"},
    {"epic": "Category management", "task": "Lock main VITAR.cz category tree v2", "priority": "P0", "owner": "E-commerce + SEO", "status": "next", "deliverable": "Navigation, filter and SEO taxonomy"},
    {"epic": "Category management", "task": "Define indexable landing pages vs noindex filter states", "priority": "P0", "owner": "SEO + E-commerce", "status": "next", "deliverable": "SEO URL rulebook"},
    {"epic": "Product UX", "task": "Create product page blueprint for supplements, drinks, cosmetics and accessories", "priority": "P0", "owner": "E-commerce + UX + Regulatory", "status": "next", "deliverable": "Product detail page spec"},
    {"epic": "Product UX", "task": "Define bundle and cross-sell logic by need state", "priority": "P1", "owner": "E-commerce/AI", "status": "backlog", "deliverable": "Cross-sell matrix v1"},
    {"epic": "Content migration", "task": "Approve which content remains on VITAR.cz vs moves to vitar-group.cz", "priority": "P0", "owner": "CMO + E-commerce", "status": "next", "deliverable": "Content destination matrix"},
    {"epic": "Content migration", "task": "Create redirect map for product/category/content URLs", "priority": "P0", "owner": "SEO + Dev", "status": "next", "deliverable": "301 redirect workbook"},
    {"epic": "VITAR GROUP web", "task": "Rewrite P0 group pages for new SBU/Coca-Cola operating model", "priority": "P0", "owner": "Central marketing", "status": "next", "deliverable": "Group website copy deck"},
    {"epic": "VITAR GROUP web", "task": "Create B2B/OEM lead-gen flow and forms", "priority": "P0", "owner": "B2B/OEM + Digital", "status": "backlog", "deliverable": "Lead-gen IA and form spec"},
    {"epic": "Platform selection", "task": "Compare platform options against PIM, content, SEO and B2B needs", "priority": "P0", "owner": "Digital/AI architecture", "status": "next", "deliverable": "Platform decision matrix"},
    {"epic": "Platform selection", "task": "Define integration scope: ERP, stock, prices, feeds, analytics, CRM/Vitar Klub", "priority": "P0", "owner": "Digital/IT/E-commerce", "status": "next", "deliverable": "Integration map"},
    {"epic": "Analytics", "task": "Design measurement plan for migration", "priority": "P1", "owner": "Digital growth + CMO", "status": "backlog", "deliverable": "GA4/GTM/server-side event plan"},
    {"epic": "Governance", "task": "Set approval workflow for claims, SEO copy and product changes", "priority": "P1", "owner": "CMO + Regulatory + Legal", "status": "backlog", "deliverable": "Content/PIM governance workflow"},
    {"epic": "Commercial", "task": "Classify SKUs by traffic driver, margin driver, hero, legacy, bundle candidate", "priority": "P1", "owner": "E-commerce + Sales", "status": "backlog", "deliverable": "Commercial SKU role matrix"},
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def governance_owner(row):
    action = row["recommended_action"]
    brand = row["proposed_brand"]
    category = row["proposed_category"]
    if action == "separate_veterinae":
        return "VITAR Veterina"
    if action == "separate_vitar_sport_review" or brand in {"Enervit", "ROYAL BAY", "Vedici"}:
        return "VITAR Sport"
    if action == "exclude_from_main_or_accessories":
        return "Exclude / accessory decision"
    if "Doplňky a merchandising" in category:
        return "Accessory / merchandising"
    return "VITAR.cz B2C/D2C"


def platform_destination(row):
    owner = governance_owner(row)
    if owner == "VITAR Veterina":
        return "Dedicated VITAR Veterina e-shop / domain TBD"
    if owner == "VITAR Sport":
        return "VITAR Sport platform / SBU decision"
    if owner == "Exclude / accessory decision":
        return "Do not import to main navigation until approved"
    return "New VITAR.cz commerce platform"


def build_governance(products):
    rows = []
    for product in products:
        owner = governance_owner(product)
        readiness = product["qa_status"]
        if product["cross_source_recoverable_fields"]:
            readiness = "enrich_from_other_source"
        rows.append({
            "name": product["name"],
            "sku": product["sku"],
            "ean": product["ean"],
            "brand": product["proposed_brand"],
            "current_brand": product["current_brand"],
            "category": product["proposed_category"],
            "governance_owner": owner,
            "platform_destination": platform_destination(product),
            "readiness": readiness,
            "qa_status": product["qa_status"],
            "readiness_score": product["readiness_score"],
            "recommended_action": product["recommended_action"],
            "vitar_url": product["vitar_url"],
            "nasevitaminy_url": product["nasevitaminy_url"],
            "recoverable_fields": product["cross_source_recoverable_fields"],
        })
    return rows


def brand_role(brand):
    roles = {
        "Vitar": "Premium hero / legacy functional brand",
        "Maxi Vita Essentials": "Top-tier modern lifestyle range",
        "Maxi Vita": "Mass-market core vitamin/mineral range",
        "Revital": "Legacy/value effervescent range; migration decision needed",
        "Revital Botanicals": "Botanical sub-line; candidate for VITAR Botanicals story",
        "Predator": "Seasonal protection micro-brand",
        "Energit": "Energy/dextrose micro-brand",
        "Capri-Sun": "Drinks/distribution portfolio, not supplement core",
        "Irbis": "Sweetener/food portfolio",
        "Vitar Kids": "Kids target-group portfolio",
        "Vitar Eko": "Eco/natural positioning",
        "Vitar Veterinae": "Separate veterinary BU",
        "Enervit": "VITAR Sport SBU",
        "ROYAL BAY": "VITAR Sport SBU",
    }
    return roles.get(brand, "Portfolio brand / needs role confirmation")


def build_brand_portfolio(governance):
    by_brand = defaultdict(list)
    for row in governance:
        by_brand[row["brand"]].append(row)
    rows = []
    for brand, items in sorted(by_brand.items(), key=lambda kv: len(kv[1]), reverse=True):
        rows.append({
            "brand": brand,
            "products": len(items),
            "role": brand_role(brand),
            "owners": dict(Counter(i["governance_owner"] for i in items)),
            "categories": dict(Counter(i["category"] for i in items).most_common(5)),
            "readiness": dict(Counter(i["readiness"] for i in items)),
        })
    return rows


def readiness_score(product_qa, group_pages):
    ready = product_qa["qa_status_counts"].get("ready", 0)
    total = product_qa["master_products"]
    product_score = round(ready / total * 100)
    clean_main = product_qa["proposed_main_keep_count"]
    current_main = product_qa["main_products_current"]
    assortment_score = round(clean_main / current_main * 100)
    group_p0 = group_pages["counts"]["by_priority"].get("P0", 0)
    group_total = group_pages["pages"]
    content_score = round((group_total - group_p0) / group_total * 100)
    return {
        "product_pim_readiness_pct": product_score,
        "assortment_decision_readiness_pct": assortment_score,
        "group_content_migration_readiness_pct": content_score,
        "overall_readiness_pct": round((product_score * 0.4) + (assortment_score * 0.35) + (content_score * 0.25)),
    }


def build_payload():
    product_qa = load_json(PRODUCT_QA)
    pim_master = load_json(PIM_MASTER)
    group_pages = load_json(GROUP_PAGES)
    content_pages = load_json(CONTENT_PAGES)
    governance = build_governance(product_qa["products"])
    brand_portfolio = build_brand_portfolio(governance)
    backlog = sorted(BACKLOG, key=lambda x: ({"P0": 0, "P1": 1, "P2": 2}.get(x["priority"], 9), x["epic"], x["task"]))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "master_products": product_qa["master_products"],
            "main_current": product_qa["main_products_current"],
            "main_keep_recommended": product_qa["proposed_main_keep_count"],
            "veterina_separate": product_qa["recommended_action_counts"].get("separate_veterinae", 0),
            "sport_review": product_qa["recommended_action_counts"].get("separate_vitar_sport_review", 0),
            "blocked_or_excluded": product_qa["recommended_action_counts"].get("exclude_from_main_or_accessories", 0),
            "both_source_products": product_qa["both_source_products"],
            "recoverable_missing_info_products": product_qa["recoverable_missing_info_products"],
            "group_pages": group_pages["pages"],
            "content_pages": len(content_pages["pages"]),
            "categories_current": len(pim_master["categories"]),
            "brands_current": len(pim_master["brands"]),
        },
        "readiness": readiness_score(product_qa, group_pages),
        "governance_counts": {
            "by_owner": dict(Counter(row["governance_owner"] for row in governance)),
            "by_platform": dict(Counter(row["platform_destination"] for row in governance)),
            "by_readiness": dict(Counter(row["readiness"] for row in governance)),
        },
        "brand_portfolio": brand_portfolio,
        "pim_attribute_model": PIM_ATTRIBUTE_MODEL,
        "backlog": backlog,
        "governance_matrix": governance,
    }


def write_json(payload):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    (PROCESSED / "strategic-readiness.json").write_text(text, encoding="utf-8")
    (PUBLIC_DATA / "strategic-readiness.json").write_text(text, encoding="utf-8")


def write_csv(payload):
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    governance_fields = [
        "governance_owner", "platform_destination", "readiness", "qa_status", "readiness_score",
        "recommended_action", "brand", "current_brand", "category", "name", "sku", "ean",
        "recoverable_fields", "vitar_url", "nasevitaminy_url",
    ]
    for path in [PROCESSED / "assortment-governance.csv", PUBLIC_DATA / "assortment-governance.csv"]:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=governance_fields)
            writer.writeheader()
            for row in payload["governance_matrix"]:
                flat = dict(row)
                flat["recoverable_fields"] = ", ".join(flat["recoverable_fields"])
                writer.writerow({field: flat.get(field, "") for field in governance_fields})

    backlog_fields = ["priority", "status", "epic", "task", "owner", "deliverable"]
    for path in [PROCESSED / "strategic-backlog.csv", PUBLIC_DATA / "strategic-backlog.csv"]:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=backlog_fields)
            writer.writeheader()
            writer.writerows(payload["backlog"])


def md_table(rows, fields):
    def cell(value):
        if isinstance(value, dict):
            value = ", ".join(f"{k}: {v}" for k, v in value.items())
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        return str(value or "").replace("|", "\\|")
    lines = [
        "| " + " | ".join(label for label, _ in fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(row.get(key)) for _, key in fields) + " |")
    return lines


def write_report(payload):
    REPORTS.mkdir(parents=True, exist_ok=True)
    s = payload["summary"]
    r = payload["readiness"]
    lines = [
        "# VITAR strategic e-commerce readiness",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Executive View",
        "",
        f"- Overall strategic readiness: {r['overall_readiness_pct']}%",
        f"- Product/PIM readiness: {r['product_pim_readiness_pct']}%",
        f"- Assortment decision readiness: {r['assortment_decision_readiness_pct']}%",
        f"- Group content migration readiness: {r['group_content_migration_readiness_pct']}%",
        "",
        "## Strategic Counts",
        "",
        f"- Master products: {s['master_products']}",
        f"- Current main VITAR.cz assortment: {s['main_current']}",
        f"- Recommended main keep assortment after QA: {s['main_keep_recommended']}",
        f"- VITAR Veterina separate: {s['veterina_separate']}",
        f"- VITAR Sport review: {s['sport_review']}",
        f"- Blocked/exclude/accessory decisions: {s['blocked_or_excluded']}",
        f"- Products available on both source websites: {s['both_source_products']}",
        f"- Products with recoverable missing info from second source: {s['recoverable_missing_info_products']}",
        f"- VITAR Group pages planned: {s['group_pages']}",
        "",
        "## Governance Counts",
        "",
        "### By Owner",
        "",
    ]
    for key, count in payload["governance_counts"]["by_owner"].items():
        lines.append(f"- {key}: {count}")
    lines.extend([
        "",
        "### By Platform Destination",
        "",
    ])
    for key, count in payload["governance_counts"]["by_platform"].items():
        lines.append(f"- {key}: {count}")

    lines.extend([
        "",
        "## Brand Portfolio Map",
        "",
    ])
    lines.extend(md_table(payload["brand_portfolio"], [
        ("Brand", "brand"),
        ("Products", "products"),
        ("Strategic role", "role"),
        ("Owners", "owners"),
        ("Top categories", "categories"),
        ("Readiness", "readiness"),
    ]))

    lines.extend([
        "",
        "## PIM Attribute Model",
        "",
    ])
    lines.extend(md_table(payload["pim_attribute_model"], [
        ("Priority", "priority"),
        ("Group", "group"),
        ("Field", "field"),
        ("Owner", "owner"),
        ("Source", "source"),
        ("Note", "note"),
    ]))

    lines.extend([
        "",
        "## Strategic Backlog",
        "",
    ])
    lines.extend(md_table(payload["backlog"], [
        ("Priority", "priority"),
        ("Status", "status"),
        ("Epic", "epic"),
        ("Task", "task"),
        ("Owner", "owner"),
        ("Deliverable", "deliverable"),
    ]))

    lines.extend([
        "",
        "## Immediate Management Decisions",
        "",
        "1. Confirm final SBU ownership for every SKU before platform import.",
        "2. Approve the PIM attribute model and regulatory approval workflow.",
        "3. Lock the VITAR.cz category tree v2 and SEO/noindex rulebook.",
        "4. Approve VITAR Group vs VITAR.cz content destination matrix.",
        "5. Decide platform shortlist against PIM, SEO, B2B, ERP and CRM/Vitar Klub needs.",
    ])
    (REPORTS / "strategic-readiness-plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload):
    HTML.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VITAR Strategic Readiness</title>
<style>
:root {{ --bg:#f6f7f9; --panel:#fff; --line:#dfe3e8; --text:#1d2430; --muted:#667085; --green:#27704a; --blue:#235f9e; --amber:#b45309; --red:#b42318; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); }}
header {{ position:sticky; top:0; z-index:5; background:var(--panel); border-bottom:1px solid var(--line); padding:14px 20px; display:flex; justify-content:space-between; gap:12px; align-items:center; }}
h1 {{ margin:0; font-size:18px; }}
.btn {{ border:1px solid var(--line); background:#f2f4f7; border-radius:6px; padding:7px 10px; color:var(--text); text-decoration:none; }}
.btn.primary {{ background:var(--green); border-color:var(--green); color:white; }}
.wrap {{ padding:16px; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:10px; margin-bottom:14px; }}
.stat {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px; min-height:82px; }}
.stat b {{ display:block; font-size:26px; }}
.stat span {{ color:var(--muted); font-size:12px; }}
.tabs {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px; }}
button {{ font:inherit; }}
.tab {{ border:1px solid var(--line); background:var(--panel); border-radius:6px; padding:8px 11px; cursor:pointer; }}
.tab.active {{ background:var(--blue); border-color:var(--blue); color:white; }}
.panel {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px; margin-bottom:12px; }}
.panel h2 {{ margin:0 0 8px; font-size:16px; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line); }}
th,td {{ border-bottom:1px solid var(--line); padding:8px 9px; text-align:left; vertical-align:top; font-size:12px; }}
th {{ background:#f2f4f7; color:#475467; position:sticky; top:56px; }}
.pill {{ display:inline-block; border-radius:999px; padding:2px 7px; font-size:11px; background:#eef2ff; margin:1px; white-space:nowrap; }}
.P0 {{ background:#fee2e2; color:#991b1b; }}
.P1 {{ background:#fef3c7; color:#92400e; }}
.P2 {{ background:#dbeafe; color:#1d4ed8; }}
.muted {{ color:var(--muted); }}
a {{ color:var(--blue); }}
</style>
</head>
<body>
<header>
  <h1>VITAR <span style="color:var(--green)">Strategic Readiness</span></h1>
  <div>
    <a class="btn" href="../data/strategic-readiness.json">JSON</a>
    <a class="btn" href="../data/strategic-backlog.csv">Backlog CSV</a>
    <a class="btn" href="../data/assortment-governance.csv">Governance CSV</a>
    <a class="btn primary" href="../reports/strategic-readiness-plan.md">Report</a>
  </div>
</header>
<div class="wrap">
  <div class="stats" id="stats"></div>
  <div class="tabs">
    <button class="tab active" data-tab="overview" onclick="setTab('overview')">Overview</button>
    <button class="tab" data-tab="governance" onclick="setTab('governance')">Governance</button>
    <button class="tab" data-tab="brands" onclick="setTab('brands')">Brands</button>
    <button class="tab" data-tab="pim" onclick="setTab('pim')">PIM Model</button>
    <button class="tab" data-tab="backlog" onclick="setTab('backlog')">Backlog</button>
  </div>
  <div id="view"></div>
</div>
<script>
const DATA = {data};
let tab = 'overview';
function pill(v, cls='') {{ return `<span class="pill ${{cls}}">${{v}}</span>`; }}
function dict(v) {{ return Object.entries(v || {{}}).map(([k,n]) => `${{k}} (${{n}})`).join(', '); }}
function stats() {{
  const s = DATA.summary, r = DATA.readiness;
  const cards = [
    ['Overall readiness', r.overall_readiness_pct + '%'],
    ['Product/PIM readiness', r.product_pim_readiness_pct + '%'],
    ['Main keep assortment', s.main_keep_recommended + ' / ' + s.main_current],
    ['Veterina separate', s.veterina_separate],
    ['Sport review', s.sport_review],
    ['Recoverable source info', s.recoverable_missing_info_products],
    ['Group pages', s.group_pages],
    ['Backlog items', DATA.backlog.length],
  ];
  document.getElementById('stats').innerHTML = cards.map(([label,value]) => `<div class="stat"><b>${{value}}</b><span>${{label}}</span></div>`).join('');
}}
function setTab(next) {{
  tab = next;
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x.dataset.tab === tab));
  render();
}}
function overview() {{
  return `<div class="panel"><h2>Immediate management decisions</h2><ol><li>Confirm final SBU ownership for every SKU.</li><li>Approve launch PIM attribute model and regulatory workflow.</li><li>Lock VITAR.cz category tree v2 and SEO/noindex rulebook.</li><li>Approve VITAR Group vs VITAR.cz content split.</li><li>Run platform decision against PIM, SEO, B2B, ERP and CRM needs.</li></ol></div>
  <table><thead><tr><th>Owner</th><th>Products</th></tr></thead><tbody>${{Object.entries(DATA.governance_counts.by_owner).map(([k,n])=>`<tr><td>${{k}}</td><td>${{n}}</td></tr>`).join('')}}</tbody></table>`;
}}
function governance() {{
  return `<table><thead><tr><th>Owner</th><th>Destination</th><th>Readiness</th><th>Brand</th><th>Category</th><th>Product</th><th>Sources</th></tr></thead><tbody>${{DATA.governance_matrix.map(r => `<tr><td>${{r.governance_owner}}</td><td>${{r.platform_destination}}</td><td>${{r.readiness}}</td><td>${{r.brand}}</td><td>${{r.category}}</td><td>${{r.name}}</td><td>${{r.vitar_url ? '<a target="_blank" href="'+r.vitar_url+'">vitar</a> ' : ''}}${{r.nasevitaminy_url ? '<a target="_blank" href="'+r.nasevitaminy_url+'">nase</a>' : ''}}</td></tr>`).join('')}}</tbody></table>`;
}}
function brands() {{
  return `<table><thead><tr><th>Brand</th><th>Products</th><th>Role</th><th>Owners</th><th>Top categories</th><th>Readiness</th></tr></thead><tbody>${{DATA.brand_portfolio.map(b => `<tr><td><b>${{b.brand}}</b></td><td>${{b.products}}</td><td>${{b.role}}</td><td>${{dict(b.owners)}}</td><td>${{dict(b.categories)}}</td><td>${{dict(b.readiness)}}</td></tr>`).join('')}}</tbody></table>`;
}}
function pim() {{
  return `<table><thead><tr><th>Priority</th><th>Group</th><th>Field</th><th>Owner</th><th>Source</th><th>Note</th></tr></thead><tbody>${{DATA.pim_attribute_model.map(f => `<tr><td>${{pill(f.priority, f.priority)}}</td><td>${{f.group}}</td><td><code>${{f.field}}</code></td><td>${{f.owner}}</td><td>${{f.source}}</td><td>${{f.note}}</td></tr>`).join('')}}</tbody></table>`;
}}
function backlog() {{
  return `<table><thead><tr><th>Priority</th><th>Status</th><th>Epic</th><th>Task</th><th>Owner</th><th>Deliverable</th></tr></thead><tbody>${{DATA.backlog.map(b => `<tr><td>${{pill(b.priority, b.priority)}}</td><td>${{b.status}}</td><td>${{b.epic}}</td><td>${{b.task}}</td><td>${{b.owner}}</td><td>${{b.deliverable}}</td></tr>`).join('')}}</tbody></table>`;
}}
function render() {{
  if (tab === 'overview') document.getElementById('view').innerHTML = overview();
  if (tab === 'governance') document.getElementById('view').innerHTML = governance();
  if (tab === 'brands') document.getElementById('view').innerHTML = brands();
  if (tab === 'pim') document.getElementById('view').innerHTML = pim();
  if (tab === 'backlog') document.getElementById('view').innerHTML = backlog();
}}
stats();
render();
</script>
</body>
</html>
"""
    (HTML / "strategic-readiness-dashboard.html").write_text(html, encoding="utf-8")


def main():
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_report(payload)
    write_html(payload)
    print(json.dumps({
        "overall_readiness_pct": payload["readiness"]["overall_readiness_pct"],
        "governance_owners": payload["governance_counts"]["by_owner"],
        "backlog_items": len(payload["backlog"]),
        "html": str(HTML / "strategic-readiness-dashboard.html"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
