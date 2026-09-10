#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import io
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "workbench" / "src" / "data" / "catalog.json"
OUTPUTS = ROOT / "outputs"
DATA_DIR = OUTPUTS / "data"
HTML_DIR = OUTPUTS / "html"
REPORTS_DIR = OUTPUTS / "reports"

VITAR_ONLY_BRANDS = {
    "Vitar",
    "Vitar Kids",
    "Vitar Kings",
    "Vitar Origin",
}
OFFLINE_BRANDS = {"Capri-Sun", "Predator"}
WIP_SUMMARY = {"total": 36, "VITAR UNITY": 19, "VITAR NEO": 17}


def targets_for(brand: str) -> list[str]:
    if brand == "Vitar Veterinae" or brand in OFFLINE_BRANDS:
        return ["outside"]
    if brand == "Maxi Vita Essentials":
        return ["vitar", "nase"]
    if brand in VITAR_ONLY_BRANDS:
        return ["vitar"]
    return ["nase"]


def assignment_for(brand: str) -> str:
    if brand == "Vitar Veterinae":
        return "Samostatná VITAR Veterina"
    if brand in OFFLINE_BRANDS:
        return "Mimo e-shopy / retail"
    if brand == "Maxi Vita Essentials":
        return "Oba e-shopy"
    if brand in VITAR_ONLY_BRANDS:
        return "Jen VITAR.cz"
    return "Jen NašeVitamíny.cz"


def public_product(product: dict) -> dict:
    urls = {source["source_key"]: source["url"] for source in product.get("sources", [])}
    return {
        "id": product["id"],
        "name": product["name"],
        "brand": product["brand"],
        "sku": product.get("sku", ""),
        "ean": product.get("ean", ""),
        "category": product["category"]["label"],
        "category_key": product["category"]["key"],
        "form": product["form"]["label"],
        "image": product.get("image", ""),
        "targets": targets_for(product["brand"]),
        "assignment": assignment_for(product["brand"]),
        "source_urls": {
            "vitar.cz": urls.get("vitar", ""),
            "nasevitaminy.cz": urls.get("nasevitaminy", ""),
            "ceske-vitaminy.cz": urls.get("ceskevitaminy", ""),
        },
    }


def category_summary(products: list[dict], target: str) -> list[dict]:
    rows = [product for product in products if target in product["targets"]]
    categories = Counter(product["category"] for product in rows)
    return [
        {
            "category": category,
            "count": count,
            "brands": Counter(product["brand"] for product in rows if product["category"] == category).most_common(),
        }
        for category, count in sorted(categories.items(), key=lambda item: (-item[1], item[0]))
    ]


def brand_summary(products: list[dict], target: str) -> list[dict]:
    brands = Counter(product["brand"] for product in products if target in product["targets"])
    return [{"brand": brand, "count": count} for brand, count in brands.most_common()]


def build_payload() -> dict:
    source = json.loads(CATALOG.read_text(encoding="utf-8"))
    products = [public_product(product) for product in source["products"]]
    products.sort(key=lambda product: (product["brand"].casefold(), product["name"].casefold()))
    counts = {target: sum(target in product["targets"] for product in products) for target in ("vitar", "nase", "outside")}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalog_generated_at": source["summary"]["generated_at"],
        "decision_date": "2026-09-03",
        "decision_source": "Tomáš Červinka, CEO; potvrzeno na týmovém setkání 3. 9. 2026",
        "rules": [
            "VITAR.cz: kompletní současná řada VITAR, VITAR NEO, VITAR UNITY a Maxi Vita Essentials.",
            "NašeVitamíny.cz: ostatní produktové portfolio a Maxi Vita Essentials.",
            "Maxi Vita Essentials je jediná značka na obou e-shopech.",
            "Capri-Sun a Predator nejsou zařazeny do obou e-shopů; zůstávají pro retail, marketplace nebo samostatné landing pages.",
            "VITAR Veterina je samostatná značka a samostatný e-shop.",
            "Revital a Revitalon jsou nyní na NašeVitamíny.cz; Revitalon se přesune až po redesignu.",
        ],
        "counts": {
            "current_products": len(products),
            "vitar_current": counts["vitar"],
            "nase_current": counts["nase"],
            "both_current": sum(product["targets"] == ["vitar", "nase"] for product in products),
            "outside_current": counts["outside"],
        },
        "wip": {
            **WIP_SUMMARY,
            "target": "vitar",
            "visibility": "Detail je dostupný pouze v interním Assortment Workbenchi.",
        },
        "shops": {
            target: {
                "brands": brand_summary(products, target),
                "categories": category_summary(products, target),
            }
            for target in ("vitar", "nase", "outside")
        },
        "products": products,
    }


def write_json(payload: dict) -> None:
    (DATA_DIR / "final-shop-split.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv(payload: dict) -> None:
    buffer = io.StringIO()
    columns = ["product_id", "name", "brand", "sku", "ean", "category", "form", "assignment", "targets", "vitar_url", "nasevitaminy_url", "ceskevitaminy_url"]
    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader()
    for product in payload["products"]:
        writer.writerow({
            "product_id": product["id"],
            "name": product["name"],
            "brand": product["brand"],
            "sku": product["sku"],
            "ean": product["ean"],
            "category": product["category"],
            "form": product["form"],
            "assignment": product["assignment"],
            "targets": " | ".join(product["targets"]),
            "vitar_url": product["source_urls"]["vitar.cz"],
            "nasevitaminy_url": product["source_urls"]["nasevitaminy.cz"],
            "ceskevitaminy_url": product["source_urls"]["ceske-vitaminy.cz"],
        })
    (DATA_DIR / "final-shop-split.csv").write_text("\ufeff" + buffer.getvalue(), encoding="utf-8")


def write_markdown(payload: dict) -> None:
    counts = payload["counts"]
    lines = [
        "# Finální rozdělení portfolia VITAR",
        "",
        f"- Rozhodnutí: {payload['decision_date']}",
        f"- Zdroj rozhodnutí: {payload['decision_source']}",
        f"- Současných master produktů: {counts['current_products']}",
        f"- VITAR.cz: {counts['vitar_current']} současných + {payload['wip']['total']} WIP placeholderů",
        f"- NašeVitamíny.cz: {counts['nase_current']} současných",
        f"- Oba e-shopy: {counts['both_current']} produktů Maxi Vita Essentials",
        f"- Mimo oba e-shopy: {counts['outside_current']} současných produktů",
        "",
        "## Pravidla",
        "",
        *[f"- {rule}" for rule in payload["rules"]],
    ]
    for target, title in (("vitar", "VITAR.cz"), ("nase", "NašeVitamíny.cz"), ("outside", "Mimo e-shopy")):
        products = [product for product in payload["products"] if target in product["targets"]]
        lines.extend(["", f"## {title}", "", "| Produkt | Značka | Kategorie | SKU | EAN | Zařazení |", "| --- | --- | --- | --- | --- | --- |"])
        for product in products:
            values = [product["name"], product["brand"], product["category"], product["sku"], product["ean"], product["assignment"]]
            lines.append("| " + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    (REPORTS_DIR / "final-shop-split.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def pixel_mark() -> str:
    pattern = ["n.....n", "v.....v", "v.....v", ".v...v.", ".v...v.", "..v.v..", "...v..."]
    return "".join(f'<i class="{("node" if cell == "n" else "core" if cell == "v" else "")}"></i>' for row in pattern for cell in row)


def write_html(payload: dict) -> None:
    embedded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    document = f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<link rel="icon" href="data:,">
<title>VITAR | Finální rozdělení portfolia</title>
<style>
:root{{--bg:#f3f5f4;--surface:#fff;--soft:#f8faf9;--ink:#17221e;--muted:#64706b;--line:#dce2df;--green:#167a5a;--green-soft:#e8f3ee;--blue:#2d63b8;--blue-soft:#eaf0fa;--gold:#9b6416;--gold-soft:#fbf1df;--sidebar:#17221f}}
*{{box-sizing:border-box;letter-spacing:0}}html,body{{margin:0;min-height:100%;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--ink)}}button,input,select{{font:inherit;color:inherit}}button,select{{cursor:pointer}}a{{color:inherit;text-decoration:none}}h1,h2,p{{margin:0}}.top{{position:sticky;top:0;z-index:20;height:64px;background:var(--sidebar);color:#fff;display:flex;align-items:center;gap:12px;padding:0 18px;border-bottom:1px solid #314039}}.mark{{display:grid;grid-template-columns:repeat(7,3px);grid-template-rows:repeat(7,3px);gap:1px;padding:5px;border:1px solid #4b7668;width:39px;height:39px}}.mark i{{background:#21372f}}.mark .core{{background:#fff}}.mark .node{{background:#59d6a9}}.brand{{display:grid;gap:2px}}.brand strong{{font-size:14px}}.brand small{{font-size:10px;color:#aabbb5}}.top nav{{display:flex;gap:7px;margin-left:auto}}.top nav a{{border:1px solid #41534c;padding:7px 9px;font-size:11px}}.top nav a:hover{{background:#263832}}.shell{{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:calc(100vh - 64px)}}aside{{position:sticky;top:64px;height:calc(100vh - 64px);overflow:auto;background:var(--surface);border-right:1px solid var(--line);padding:14px}}aside h2{{font-size:11px;text-transform:uppercase;color:var(--muted);margin:13px 0 7px}}.category-list{{display:grid;gap:2px}}.category-list button{{border:0;background:transparent;display:flex;justify-content:space-between;text-align:left;padding:8px;border-radius:4px;font-size:12px}}.category-list button:hover,.category-list button.active{{background:var(--green-soft);color:#0e5c42;font-weight:700}}.category-list b{{font-size:10px;color:var(--muted)}}main{{min-width:0;padding:18px;display:grid;gap:15px;align-content:start}}.heading{{display:flex;justify-content:space-between;align-items:flex-end;gap:16px}}.eyebrow{{color:var(--green);font-size:10px;font-weight:800;text-transform:uppercase}}.heading h1{{font-size:26px;margin:4px 0}}.heading p{{font-size:12px;color:var(--muted)}}.decision{{background:#18362d;color:#fff;padding:13px 15px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center}}.decision strong{{display:block;font-size:13px}}.decision p{{color:#bad0c7;font-size:11px;margin-top:4px;line-height:1.45}}.decision time{{font-size:11px;color:#bad0c7}}.segments{{background:var(--surface);border:1px solid var(--line);padding:4px;display:grid;grid-template-columns:repeat(3,1fr)}}.segments button{{border:0;background:transparent;min-height:42px;padding:0 11px;display:flex;align-items:center;justify-content:space-between}}.segments button+button{{border-left:1px solid var(--line)}}.segments button.active{{background:var(--green-soft);color:#0e5c42;font-weight:800}}.segments b{{font-size:10px;border:1px solid var(--line);border-radius:999px;padding:3px 7px}}.segments button.active b{{background:var(--green);border-color:var(--green);color:#fff}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);background:var(--surface);border:1px solid var(--line)}}.metric{{padding:11px 13px;border-right:1px solid var(--line);display:grid;gap:2px}}.metric:last-child{{border-right:0}}.metric small{{font-size:9px;text-transform:uppercase;color:var(--muted)}}.metric strong{{font-size:18px}}.brands{{background:var(--surface);border:1px solid var(--line);padding:11px}}.brands header{{display:flex;gap:7px;align-items:baseline;margin-bottom:8px}}.brands header strong{{font-size:12px}}.brands header small{{font-size:10px;color:var(--muted)}}.brand-buttons{{display:flex;gap:5px;overflow-x:auto}}.brand-buttons button{{flex:0 0 auto;min-height:34px;border:1px solid var(--line);background:var(--soft);padding:0 9px;font-size:11px}}.brand-buttons button.active{{background:var(--ink);border-color:var(--ink);color:#fff}}.toolbar{{display:grid;grid-template-columns:minmax(240px,1fr) minmax(180px,260px);gap:8px}}.toolbar label{{display:flex;align-items:center;background:var(--surface);border:1px solid var(--line);padding:0 10px;min-height:40px}}.toolbar input{{border:0;outline:0;background:transparent;width:100%}}.toolbar select{{border:1px solid var(--line);background:var(--surface);padding:0 9px}}.mobile-category{{display:none}}.result{{font-size:11px;color:var(--muted)}}.result strong{{color:var(--ink)}}.wip{{display:none;background:var(--gold-soft);border:1px solid #e8d2ad;padding:12px;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:10px}}.wip.visible{{display:grid}}.wip strong{{font-size:13px}}.wip p{{font-size:10px;color:#76511d;margin-top:3px}}.wip a{{background:#76511d;color:#fff;padding:8px 10px;font-size:11px}}.groups{{display:grid;gap:16px}}.group{{display:grid;gap:8px}}.group>header{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1px solid #c7d0cc;padding-bottom:7px}}.group h2{{font-size:16px;margin-top:2px}}.group>header>b{{font-size:11px;color:var(--muted)}}.cards{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}}.card{{background:var(--surface);border:1px solid var(--line);border-radius:6px;display:grid;grid-template-columns:54px minmax(0,1fr);gap:10px;padding:8px;min-height:82px}}.image{{width:54px;height:54px;background:var(--soft);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:10px}}.image img{{width:100%;height:100%;object-fit:contain;padding:3px}}.copy{{min-width:0;display:grid;gap:3px;align-content:start}}.copy small{{color:var(--green);font-size:9px;text-transform:uppercase;font-weight:800}}.copy strong{{font-size:12px;line-height:1.3}}.copy span{{font-size:9px;color:var(--muted)}}.pills{{display:flex;gap:4px;flex-wrap:wrap;margin-top:2px}}.pill{{font-size:8px;text-transform:uppercase;font-weight:800;background:var(--blue-soft);color:var(--blue);padding:2px 5px;border-radius:999px}}.pill.both{{background:var(--green-soft);color:#0e5c42}}.pill.out{{background:var(--gold-soft);color:var(--gold)}}.sources{{display:flex;gap:5px;margin-left:auto}}.sources a{{font-size:9px;text-decoration:underline;color:var(--blue)}}.empty{{padding:50px 20px;text-align:center;background:var(--surface);border:1px solid var(--line);color:var(--muted)}}
@media(max-width:900px){{.shell{{grid-template-columns:1fr}}aside{{display:none}}.mobile-category{{display:block}}.cards{{grid-template-columns:1fr}}}}
@media(max-width:640px){{.top{{padding:0 10px}}.top nav a:first-child{{display:none}}main{{padding:12px}}.heading{{align-items:flex-start;flex-direction:column}}.heading h1{{font-size:22px}}.decision{{grid-template-columns:1fr}}.segments{{grid-template-columns:1fr}}.segments button+button{{border-left:0;border-top:1px solid var(--line)}}.metrics{{grid-template-columns:1fr 1fr}}.metric:nth-child(2){{border-right:0}}.metric:nth-child(-n+2){{border-bottom:1px solid var(--line)}}.toolbar{{grid-template-columns:1fr}}.wip{{grid-template-columns:1fr}}.card{{grid-template-columns:48px minmax(0,1fr)}}.image{{width:48px;height:48px}}}}
</style>
</head>
<body>
<header class="top"><span class="mark">{pixel_mark()}</span><span class="brand"><strong>VITAR</strong><small>Finální rozdělení portfolia</small></span><nav><a href="../index.html">Rozcestník</a><a href="../data/final-shop-split.json" download>JSON</a><a href="../reports/final-shop-split.md" download>MD</a><a href="../data/final-shop-split.csv" download>CSV</a></nav></header>
<div class="shell"><aside><h2>Kategorie</h2><div class="category-list" id="categoryList"></div></aside><main>
<header class="heading"><div><p class="eyebrow">SCHVÁLENÉ ROZDĚLENÍ</p><h1>Portfolio pro jednotlivé e-shopy</h1><p>Současný sortiment ze tří zdrojových webů, sjednocený na 324 master produktů.</p></div></header>
<section class="decision"><div><strong>Rozhodnutí vedení</strong><p>VITAR.cz staví na značce VITAR, nových řadách NEO a UNITY a Maxi Vita Essentials. Ostatní portfolio patří na NašeVitamíny.cz. Essentials je jediný překryv.</p></div><time>3. 9. 2026</time></section>
<div class="segments" id="segments"></div><div class="metrics" id="metrics"></div>
<section class="wip" id="wip"><div><strong>36 připravovaných produktů: 19 UNITY + 17 NEO</strong><p>Interní názvy a vývojové podklady nejsou publikovány na veřejném GitHub Pages.</p></div><a href="https://vitar-assortment-workbench.vercel.app/">Otevřít interní WIP</a></section>
<section class="brands"><header><strong>Značky</strong><small>První úroveň navigace</small></header><div class="brand-buttons" id="brands"></div></section>
<div class="toolbar"><label><input id="search" type="search" placeholder="Hledat produkt, značku, SKU nebo EAN"></label><select class="mobile-category" id="categorySelect"></select></div>
<p class="result" id="result"></p><div class="groups" id="groups"></div>
</main></div>
<script>
const DATA={embedded};
const TABS=[['vitar','VITAR.cz'],['nase','NašeVitamíny.cz'],['outside','Mimo e-shopy']];
let shop='vitar',brand='all',category='all',query='';
const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
const rows=()=>DATA.products.filter(product=>product.targets.includes(shop));
function categories(){{const counts=new Map();rows().filter(product=>brand==='all'||product.brand===brand).forEach(product=>counts.set(product.category,(counts.get(product.category)||0)+1));return [...counts].sort((a,b)=>a[0].localeCompare(b[0],'cs'));}}
function visible(){{const needle=query.trim().toLocaleLowerCase('cs');return rows().filter(product=>(brand==='all'||product.brand===brand)&&(category==='all'||product.category===category)&&(!needle||`${{product.name}} ${{product.brand}} ${{product.sku}} ${{product.ean}}`.toLocaleLowerCase('cs').includes(needle)));}}
function setShop(next){{shop=next;brand='all';category='all';query='';document.getElementById('search').value='';render();}}
function setBrand(next){{brand=next;category='all';render();}}
function setCategory(next){{category=next;render();}}
function sourceLinks(product){{return Object.entries(product.source_urls).filter(([,url])=>url).map(([label,url])=>`<a href="${{esc(url)}}" target="_blank" rel="noreferrer">${{esc(label.replace('.cz',''))}}</a>`).join('');}}
function card(product){{const cls=product.assignment==='Oba e-shopy'?'both':product.targets.includes('outside')?'out':'';return `<article class="card"><span class="image">${{product.image?`<img src="${{esc(product.image)}}" alt="">`:'Bez foto'}}</span><span class="copy"><small>${{esc(product.brand)}}</small><strong>${{esc(product.name)}}</strong><span>${{esc(product.form)}}${{product.sku?` · SKU ${{esc(product.sku)}}`:''}}</span><span class="pills"><b class="pill ${{cls}}">${{esc(product.assignment)}}</b><span class="sources">${{sourceLinks(product)}}</span></span></span></article>`;}}
function render(){{
 const shopRows=rows(),shown=visible(),cats=categories(),brandCounts=new Map();shopRows.forEach(product=>brandCounts.set(product.brand,(brandCounts.get(product.brand)||0)+1));
 document.getElementById('segments').innerHTML=TABS.map(([key,label])=>`<button class="${{shop===key?'active':''}}" onclick="setShop('${{key}}')"><span>${{label}}</span><b>${{DATA.counts[key==='vitar'?'vitar_current':key==='nase'?'nase_current':'outside_current']}}</b></button>`).join('');
 document.getElementById('metrics').innerHTML=`<span class="metric"><small>Produkty</small><strong>${{shopRows.length}}</strong></span><span class="metric"><small>Značky</small><strong>${{brandCounts.size}}</strong></span><span class="metric"><small>Kategorie</small><strong>${{new Set(shopRows.map(product=>product.category)).size}}</strong></span><span class="metric"><small>WIP v interním PIM</small><strong>${{shop==='vitar'?DATA.wip.total:0}}</strong></span>`;
 document.getElementById('wip').classList.toggle('visible',shop==='vitar');
 document.getElementById('brands').innerHTML=`<button class="${{brand==='all'?'active':''}}" onclick="setBrand('all')">Všechny · ${{shopRows.length}}</button>`+[...brandCounts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'cs')).map(([label,count])=>`<button class="${{brand===label?'active':''}}" onclick='setBrand(${{JSON.stringify(label)}})'>${{esc(label)}} · ${{count}}</button>`).join('');
 const categoryRows=[['all',shown.length],...cats];document.getElementById('categoryList').innerHTML=categoryRows.map(([label,count])=>`<button class="${{category===label?'active':''}}" onclick='setCategory(${{JSON.stringify(label)}})'><span>${{label==='all'?'Všechny kategorie':esc(label)}}</span><b>${{count}}</b></button>`).join('');
 document.getElementById('categorySelect').innerHTML=categoryRows.map(([label,count])=>`<option value="${{esc(label)}}" ${{category===label?'selected':''}}>${{label==='all'?'Všechny kategorie':esc(label)}} (${{count}})</option>`).join('');
 document.getElementById('result').innerHTML=`Zobrazeno <strong>${{shown.length}}</strong> produktů`;
 const grouped=new Map();shown.forEach(product=>{{const list=grouped.get(product.category)||[];list.push(product);grouped.set(product.category,list)}});document.getElementById('groups').innerHTML=grouped.size?[...grouped].sort((a,b)=>a[0].localeCompare(b[0],'cs')).map(([label,items])=>`<section class="group"><header><div><p class="eyebrow">KATEGORIE</p><h2>${{esc(label)}}</h2></div><b>${{items.length}}</b></header><div class="cards">${{items.map(card).join('')}}</div></section>`).join(''):`<div class="empty">Žádné produkty pro zvolený filtr.</div>`;
}}
document.getElementById('search').addEventListener('input',event=>{{query=event.target.value;render()}});document.getElementById('categorySelect').addEventListener('change',event=>setCategory(event.target.value));render();
</script>
</body>
</html>"""
    (HTML_DIR / "vitar-category-planner.html").write_text(document, encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_html(payload)
    print(json.dumps({"counts": payload["counts"], "wip": payload["wip"], "html": str(HTML_DIR / "vitar-category-planner.html")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
