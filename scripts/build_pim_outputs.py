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
    {"field": "brand", "label": "Značka / produktová řada", "source": "scraped brand detection", "priority": "P0"},
    {"field": "category_recommendation", "label": "Hlavní potřeba", "source": "PIM managed taxonomy", "priority": "P0"},
    {"field": "form", "label": "Forma", "source": "PIM attribute", "priority": "P0"},
    {"field": "active_ingredients", "label": "Aktivní látky", "source": "manual/PIM enrichment", "priority": "P0"},
    {"field": "target_group", "label": "Cílová skupina", "source": "manual/PIM enrichment", "priority": "P0"},
    {"field": "age_group", "label": "Věk", "source": "manual/PIM enrichment", "priority": "P1"},
    {"field": "diet_flags", "label": "Bez cukru / vegan / gluten-free / lactose-free", "source": "manual/PIM enrichment", "priority": "P1"},
    {"field": "pack_size", "label": "Velikost balení", "source": "scraped attributes", "priority": "P1"},
    {"field": "flavour", "label": "Příchuť", "source": "manual/extracted from name", "priority": "P1"},
    {"field": "price_per_unit", "label": "Cena za dávku / kus", "source": "commerce calculation", "priority": "P2"},
    {"field": "quality_claims", "label": "Certifikace/testování/kvalita", "source": "manual/PIM enrichment", "priority": "P2"},
]


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))["products"]


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
        primary["pim_recommendation"] = {
            "master_key": key,
            "import_priority": "P0" if primary["category_recommendation"]["label"] in {"Imunita a nachlazení", "Hořčík a minerály", "Děti", "Krása, vlasy, pleť"} else "P1",
            "canonical_source": "nasevitaminy.cz for price/availability, vitar.cz for brand/category content",
            "needs_manual_enrichment": missing_enrichment(primary),
        }
        masters.append(primary)
    return sorted(masters, key=lambda x: (x["category_recommendation"]["label"], x["brand"], x["name"]))


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


def write_json(products, masters, categories):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_records": len(products),
        "master_products": len(masters),
        "duplicate_raw_records": len(products) - len(masters),
        "categories": categories,
        "filters": FILTER_MODEL,
        "competitor_notes": COMPETITOR_NOTES,
        "products": masters,
    }
    (PROCESSED / "pim-master.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def write_report(payload):
    REPORTS.mkdir(parents=True, exist_ok=True)
    products = payload["products"]
    lines = [
        "# VITAR ecommerce PIM preparation",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Executive Summary",
        "",
        f"- Scraped raw product records: {payload['raw_records']}",
        f"- Recommended master products after SKU/EAN dedupe: {payload['master_products']}",
        f"- Cross-site duplicate records merged: {payload['duplicate_raw_records']}",
        "- Recommended source strategy: NašeVitamíny for commerce fields, VITAR.cz for brand/content enrichment.",
        "",
        "## Category Management Recommendation",
        "",
        "The new e-shop should not mirror the old brand-first navigation. Use a hybrid model: primary navigation by customer need, secondary filters by brand/line, form, active ingredient and target group.",
        "",
        "| Category | Products | Top brands | Top forms | SEO title |",
        "|---|---:|---|---|---|",
    ]
    def cell(value):
        return str(value).replace("|", "\\|")

    for row in payload["categories"]:
        brands = ", ".join(f"{b} ({c})" for b, c in row["brands"])
        forms = ", ".join(f"{b} ({c})" for b, c in row["forms"])
        lines.append(f"| {cell(row['category'])} | {row['count']} | {cell(brands)} | {cell(forms)} | {cell(row['seo']['title'])} |")
    lines.extend([
        "",
        "## Filter Model for PIM",
        "",
        "| Priority | Filter | PIM field | Source |",
        "|---|---|---|---|",
    ])
    for f in payload["filters"]:
        lines.append(f"| {f['priority']} | {f['label']} | `{f['field']}` | {f['source']} |")
    lines.extend([
        "",
        "## SEO Setup",
        "",
        "- Build one indexable landing page per customer need: immunity, magnesium/minerals, kids, beauty, joints, digestion/detox, energy/stress/sleep, eyes, heart, urinary, repellents, pets, drinks, sweeteners.",
        "- Keep brand pages indexable for Maxi Vita, Vitar, Revital, Predator, Energit, Capri-Sun, Veterinae and Essentials, but do not make brand the only navigation path.",
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
    <div class="section-title">Categories</div>
    <div id="cats"></div>
    <div class="section-title">Brands</div>
    <div id="brands"></div>
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
    (category === 'all' || p.category_recommendation.label === category) &&
    (brand === 'all' || p.brand === brand) &&
    (!query || (p.name + ' ' + p.sku + ' ' + p.ean + ' ' + p.description).toLowerCase().includes(query.toLowerCase()))
  );
}}
function renderStats() {{
  document.getElementById('stats').innerHTML = `
    <span><b>${{DATA.master_products}}</b> master products</span>
    <span><b>${{DATA.raw_records}}</b> raw records</span>
    <span><b>${{DATA.duplicate_raw_records}}</b> merged duplicates</span>
    <span><b>${{DATA.categories.length}}</b> recommended categories</span>
    <span><b>${{DATA.filters.length}}</b> PIM filters</span>`;
}}
function renderSide() {{
  const cats = [['all', DATA.master_products], ...DATA.categories.map(c => [c.category, c.count])];
  document.getElementById('cats').innerHTML = cats.map(([c,n]) => `<div class="cat ${{category===c?'active':''}}" onclick="category='${{c}}';renderAll()"><span>${{c==='all'?'All products':c}}</span><span class="count">${{n}}</span></div>`).join('');
  const brands = [['all', DATA.master_products], ...countBy(DATA.products, p => p.brand)];
  document.getElementById('brands').innerHTML = brands.map(([b,n]) => `<div class="cat ${{brand===b?'active':''}}" onclick="brand='${{b}}';renderAll()"><span>${{b==='all'?'All brands':b}}</span><span class="count">${{n}}</span></div>`).join('');
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
        <span class="pill">${{p.duplicate_count}} source${{p.duplicate_count>1?'s':''}}</span>
        ${{miss.map(m => `<span class="pill warn">${{m}}</span>`).join('')}}
      </div>
    </div>
  </article>`;
}}
function renderProducts() {{
  const list = filtered();
  return `<div class="toolbar">
    <input placeholder="Search name, SKU, EAN..." value="${{query}}" oninput="query=this.value;renderView()">
    <select onchange="category=this.value;renderAll()">${{['all',...DATA.categories.map(c=>c.category)].map(c=>`<option ${{category===c?'selected':''}} value="${{c}}">${{c==='all'?'All categories':c}}</option>`).join('')}}</select>
    <select onchange="brand=this.value;renderAll()">${{['all',...countBy(DATA.products,p=>p.brand).map(x=>x[0])].map(b=>`<option ${{brand===b?'selected':''}} value="${{b}}">${{b==='all'?'All brands':b}}</option>`).join('')}}</select>
  </div><div class="meta" style="margin-bottom:10px">${{list.length}} visible products</div><div class="grid">${{list.map(productCard).join('')}}</div>`;
}}
function renderTaxonomy() {{
  return `<table><thead><tr><th>Category</th><th>Products</th><th>Top brands</th><th>Top forms</th><th>SEO H1</th></tr></thead><tbody>${{DATA.categories.map(c => `<tr><td><b>${{c.category}}</b></td><td>${{c.count}}</td><td>${{c.brands.map(x=>x[0]+' ('+x[1]+')').join(', ')}}</td><td>${{c.forms.map(x=>x[0]+' ('+x[1]+')').join(', ')}}</td><td>${{c.seo.h1}}</td></tr>`).join('')}}</tbody></table>`;
}}
function renderFilters() {{
  return `<table><thead><tr><th>Priority</th><th>Filter</th><th>Field</th><th>Source</th></tr></thead><tbody>${{DATA.filters.map(f => `<tr><td>${{f.priority}}</td><td>${{f.label}}</td><td><code>${{f.field}}</code></td><td>${{f.source}}</td></tr>`).join('')}}</tbody></table>`;
}}
function renderSeo() {{
  return DATA.categories.map(c => `<div class="panel"><h2>${{c.category}}</h2><div class="meta"><b>Title:</b> ${{c.seo.title}}<br><b>Meta:</b> ${{c.seo.description}}</div></div>`).join('');
}}
function renderCompetitors() {{
  return DATA.competitor_notes.map(n => `<div class="panel"><h2><a href="${{n.url}}" target="_blank">${{n.name}}</a></h2><div class="meta">${{n.takeaway}}</div></div>`).join('');
}}
function exportData(format) {{
  setTab('export');
  const out = document.getElementById('exportBox');
  if (!out) return;
  out.value = format === 'json' ? JSON.stringify(DATA, null, 2) : DATA.categories.map(c => `## ${{c.category}}\\n- Products: ${{c.count}}\\n- SEO title: ${{c.seo.title}}\\n- Meta: ${{c.seo.description}}`).join('\\n\\n');
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
    payload = write_json(products, masters, categories)
    write_report(payload)
    write_html(payload)
    print(json.dumps({
        "raw_records": payload["raw_records"],
        "master_products": payload["master_products"],
        "categories": len(payload["categories"]),
        "html": str(HTML / "vitar-category-planner.html"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
