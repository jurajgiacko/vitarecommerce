#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "outputs"
REPORTS = OUT / "reports"
HTML = OUT / "html"
PUBLIC_DATA = OUT / "data"

CONTENT_JSON = PROCESSED / "content-pages.json"


GROUP_FAMILIES = {"corporate_group", "career", "article_or_knowledge"}
GROUP_ACTIONS = {"move_to_group_web"}


def load_pages():
    return json.loads(CONTENT_JSON.read_text(encoding="utf-8"))["pages"]


def is_group_page(page):
    return page["migration"]["action"] in GROUP_ACTIONS or page["family"] in GROUP_FAMILIES


def section_for(page):
    slug = page["slug"].lower()
    title = (page["h1"] or page["title"]).lower()
    if page["family"] == "career" or slug.startswith("kariera"):
        if "volna-mista" in slug:
            return "Kariéra / otevřené pozice"
        if "oddeleni" in slug:
            return "Kariéra / oddělení"
        return "Kariéra"
    if any(x in slug for x in ["spoluprace", "lekarny", "retail", "export", "smluvni-vyroba", "prodej-do-firem"]):
        return "B2B / OEM / partneři"
    if any(x in slug for x in ["certifikaty", "udrzitelnost", "eticky-kodex", "whistleblowing", "kontrola"]):
        return "Trust / compliance / kvalita"
    if any(x in slug for x in ["pro-media", "pomahame", "spolupracujeme", "reference"]):
        return "PR / partnerství / CSR"
    if page["family"] == "article_or_knowledge":
        return "Expertise / edukace"
    if any(x in slug for x in ["historie", "pribeh", "management", "dcerine", "kdo-jsme", "o-spolecnosti"]):
        return "O skupině"
    if page["source_site"] == "nasevitaminy.cz":
        return "Legacy NašeVitamíny"
    if "vitar" in title:
        return "Homepage / positioning"
    return "O skupině"


def target_path_for(page):
    section = section_for(page)
    slug = page["slug"].strip("/")
    if section == "Homepage / positioning":
        return "/"
    if section.startswith("Kariéra"):
        if "volna-mista" in slug:
            return "/kariera/volna-mista/" + slug.split("/")[-1]
        if "oddeleni" in slug:
            return "/kariera/oddeleni/" + slug.split("/")[-1]
        return "/kariera"
    if section == "B2B / OEM / partneři":
        if "smluvni-vyroba" in slug:
            return "/b2b/smluvni-vyroba"
        if "export" in slug:
            return "/b2b/export"
        if "retail" in slug:
            return "/b2b/retail"
        if "lekarny" in slug:
            return "/b2b/farmacie"
        if "prodej-do-firem" in slug:
            return "/b2b/prodej-do-firem"
        return "/b2b"
    if section == "Trust / compliance / kvalita":
        return "/kvalita/" + slug.split("/")[-1]
    if section == "PR / partnerství / CSR":
        return "/media-a-csr/" + slug.split("/")[-1]
    if section == "Expertise / edukace":
        return "/expertise/" + slug.split("/")[-1]
    if section == "Legacy NašeVitamíny":
        return "/o-skupine"
    return "/o-skupine/" + slug.split("/")[-1]


def priority_for(page):
    section = section_for(page)
    slug = page["slug"].lower()
    if section in {"Homepage / positioning", "O skupině", "B2B / OEM / partneři", "Trust / compliance / kvalita"}:
        return "P0"
    if section.startswith("Kariéra"):
        return "P1"
    if section in {"PR / partnerství / CSR", "Expertise / edukace"}:
        return "P2"
    if "e-commerce-development-lead" in slug:
        return "Archive"
    return "P2"


def make_group_pages(pages):
    rows = []
    seen = set()
    for page in pages:
        if not is_group_page(page):
            continue
        key = (page["source_site"], page["url"])
        if key in seen:
            continue
        seen.add(key)
        row = dict(page)
        row["group_section"] = section_for(page)
        row["target_domain"] = "vitar-group.cz"
        row["target_path"] = target_path_for(page)
        row["target_url"] = "https://vitar-group.cz" + row["target_path"]
        row["migration_priority"] = priority_for(page)
        row["owner"] = owner_for(row)
        row["rewrite_need"] = rewrite_need(row)
        rows.append(row)
    return sorted(rows, key=lambda p: (priority_sort(p["migration_priority"]), p["group_section"], p["target_path"], p["url"]))


def priority_sort(priority):
    return {"P0": 0, "P1": 1, "P2": 2, "Archive": 3}.get(priority, 9)


def owner_for(page):
    section = page["group_section"]
    if section.startswith("Kariéra"):
        return "HR + Central marketing"
    if section == "B2B / OEM / partneři":
        return "B2B/OEM export + Central marketing"
    if section == "Trust / compliance / kvalita":
        return "Quality/legal + Central marketing"
    if section == "PR / partnerství / CSR":
        return "PR/CMO"
    if section == "Expertise / edukace":
        return "CMO + expert/medical review"
    return "Central marketing / VITAR GROUP"


def rewrite_need(page):
    if page["migration_priority"] == "Archive":
        return "Do not migrate as public evergreen content; keep for historical/archive review."
    if page["group_section"] == "Homepage / positioning":
        return "Rewrite strongly for new VITAR GROUP positioning, SBU model and trust proof."
    if page["group_section"].startswith("Kariéra"):
        return "Keep facts, rewrite tone for employer branding and current hiring."
    if page["group_section"] == "B2B / OEM / partneři":
        return "Rewrite into lead-gen pages with clear forms, proof points and production capabilities."
    if page["group_section"] == "Expertise / edukace":
        return "Keep only after claims/legal review; avoid medical overclaiming."
    return "Light rewrite and design/content QA before migration."


def section_summary(rows):
    by_section = defaultdict(list)
    for row in rows:
        by_section[row["group_section"]].append(row)
    summary = []
    for section, items in sorted(by_section.items(), key=lambda kv: (min(priority_sort(i["migration_priority"]) for i in kv[1]), kv[0])):
        summary.append({
            "section": section,
            "count": len(items),
            "priorities": dict(Counter(i["migration_priority"] for i in items)),
            "owners": dict(Counter(i["owner"] for i in items)),
            "example_targets": [i["target_path"] for i in items[:6]],
        })
    return summary


def write_json(rows, summary):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domain": "vitar-group.cz",
        "positioning": "Corporate/group website for VITAR GROUP: brand trust, employer branding, B2B/OEM lead generation, quality proof, media and shared services.",
        "pages": len(rows),
        "counts": {
            "by_section": dict(Counter(r["group_section"] for r in rows)),
            "by_priority": dict(Counter(r["migration_priority"] for r in rows)),
            "by_owner": dict(Counter(r["owner"] for r in rows)),
            "by_source": dict(Counter(r["source_site"] for r in rows)),
        },
        "sections": summary,
        "pages_inventory": rows,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    (PROCESSED / "vitar-group-pages.json").write_text(text, encoding="utf-8")
    (PUBLIC_DATA / "vitar-group-pages.json").write_text(text, encoding="utf-8")
    return payload


def write_csv(rows):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "migration_priority", "group_section", "owner", "source_site", "url", "target_url",
        "h1", "title", "meta_description", "text_length", "rewrite_need",
    ]
    for path in [PROCESSED / "vitar-group-pages.csv", PUBLIC_DATA / "vitar-group-pages.csv"]:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_report(payload):
    REPORTS.mkdir(parents=True, exist_ok=True)
    rows = payload["pages_inventory"]
    lines = [
        "# VITAR Group content plan",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Critical View",
        "",
        "VITAR Group can be specified now, but should not be built by copy-pasting the old pages. The scrape is a migration seed: it preserves topics, proof points and URLs, but the new `vitar-group.cz` needs a rewritten information architecture around group trust, B2B/OEM lead generation and employer branding.",
        "",
        "`vitar.cz` should stay product-led. Corporate story, history, management, certificates, career, export, retail, pharmacy, private label/OEM, media and CSR should move to `vitar-group.cz`.",
        "",
        "## Proposed Sitemap",
        "",
        "- `/` - VITAR GROUP positioning, 35+ years, production footprint, quality proof, SBU model.",
        "- `/o-skupine` - who we are, history, management, group companies.",
        "- `/b2b` - B2B/OEM lead generation: retail, pharmacy, export, private labels, production capacity.",
        "- `/kvalita` - certificates, quality, supplement control, sustainability, ethics, whistleblowing.",
        "- `/kariera` - employer brand, departments, open roles, candidate GDPR.",
        "- `/media-a-csr` - media, partnerships, CSR/helping, references.",
        "- `/expertise` - seminars, ambassadors and education after claims/legal review.",
        "",
        "## Counts",
        "",
    ]
    for key, value in payload["counts"]["by_section"].items():
        lines.append(f"- {key}: {value}")
    lines.extend([
        "",
        "## Section Plan",
        "",
        "| Section | Pages | Priorities | Owner | Example target paths |",
        "|---|---:|---|---|---|",
    ])
    def cell(value):
        return str(value).replace("|", "\\|")
    for section in payload["sections"]:
        priorities = ", ".join(f"{k}: {v}" for k, v in section["priorities"].items())
        owners = ", ".join(section["owners"].keys())
        targets = ", ".join(section["example_targets"])
        lines.append(f"| {cell(section['section'])} | {section['count']} | {cell(priorities)} | {cell(owners)} | {cell(targets)} |")
    lines.extend([
        "",
        "## Page Inventory",
        "",
        "| Priority | Section | Source URL | Target URL | H1 / Title | Rewrite need |",
        "|---|---|---|---|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| {row['migration_priority']} | {cell(row['group_section'])} | [{row['source_site']}]({row['url']}) | {cell(row['target_url'])} | {cell(row['h1'] or row['title'])} | {cell(row['rewrite_need'])} |"
        )
    lines.extend([
        "",
        "## Build Readiness",
        "",
        "- Ready for: IA, sitemap, content audit, copy deck, Webflow/CMS modelling, redirect planning.",
        "- Not ready for: final copy freeze, legal/compliance sign-off, production launch.",
        "- Next required step: decide target page owners and mark each row as `migrate`, `merge`, `rewrite`, or `archive`.",
    ])
    (REPORTS / "vitar-group-content-plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload):
    HTML.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VITAR Group Content Planner</title>
<style>
body {{ margin:0; font-family:Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:#f6f7f9; color:#1d2430; }}
header {{ background:#fff; border-bottom:1px solid #dfe3e8; padding:18px 22px; position:sticky; top:0; z-index:2; }}
h1 {{ margin:0; font-size:20px; }}
main {{ padding:18px; }}
.stats {{ display:flex; gap:14px; flex-wrap:wrap; color:#667085; margin-top:8px; }}
.stats b {{ color:#1d2430; }}
.toolbar {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px; }}
input, select {{ border:1px solid #dfe3e8; border-radius:6px; padding:8px 10px; min-width:220px; background:#fff; }}
table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid #dfe3e8; }}
th, td {{ text-align:left; padding:9px 10px; border-bottom:1px solid #dfe3e8; font-size:13px; vertical-align:top; }}
th {{ background:#f2f4f7; color:#475467; }}
.pill {{ display:inline-block; border-radius:999px; padding:2px 7px; background:#eef2ff; font-size:11px; }}
.p0 {{ background:#dcfce7; color:#166534; }}
.p1 {{ background:#e0f2fe; color:#075985; }}
.p2 {{ background:#fef3c7; color:#92400e; }}
.archive {{ background:#fee2e2; color:#991b1b; }}
a {{ color:#235f9e; }}
</style>
</head>
<body>
<header>
  <h1>VITAR Group Content Planner</h1>
  <div class="stats" id="stats"></div>
</header>
<main>
  <div class="toolbar">
    <input id="q" placeholder="Search URL, title, section..." oninput="render()">
    <select id="section" onchange="render()"></select>
    <select id="priority" onchange="render()"></select>
  </div>
  <div id="table"></div>
</main>
<script>
const DATA = {data};
const pages = DATA.pages_inventory;
const sectionSelect = document.getElementById('section');
const prioritySelect = document.getElementById('priority');
sectionSelect.innerHTML = ['all', ...Object.keys(DATA.counts.by_section)].map(x => `<option value="${{x}}">${{x === 'all' ? 'All sections' : x}}</option>`).join('');
prioritySelect.innerHTML = ['all', ...Object.keys(DATA.counts.by_priority)].map(x => `<option value="${{x}}">${{x === 'all' ? 'All priorities' : x}}</option>`).join('');
function cls(p) {{ return p === 'P0' ? 'p0' : p === 'P1' ? 'p1' : p === 'P2' ? 'p2' : 'archive'; }}
function filtered() {{
  const q = document.getElementById('q').value.toLowerCase();
  const s = sectionSelect.value;
  const p = prioritySelect.value;
  return pages.filter(x =>
    (s === 'all' || x.group_section === s) &&
    (p === 'all' || x.migration_priority === p) &&
    (!q || [x.url, x.target_url, x.h1, x.title, x.group_section, x.owner].join(' ').toLowerCase().includes(q))
  );
}}
function render() {{
  const rows = filtered();
  document.getElementById('stats').innerHTML = `
    <span><b>${{DATA.pages}}</b> pages</span>
    <span><b>${{DATA.domain}}</b></span>
    <span><b>${{rows.length}}</b> visible</span>`;
  document.getElementById('table').innerHTML = `<table><thead><tr><th>Priority</th><th>Section</th><th>Source</th><th>Target</th><th>Title</th><th>Owner</th><th>Rewrite need</th></tr></thead><tbody>${{rows.map(x => `<tr><td><span class="pill ${{cls(x.migration_priority)}}">${{x.migration_priority}}</span></td><td>${{x.group_section}}</td><td><a href="${{x.url}}" target="_blank">${{x.source_site}}</a></td><td>${{x.target_url}}</td><td><b>${{x.h1 || x.title}}</b></td><td>${{x.owner}}</td><td>${{x.rewrite_need}}</td></tr>`).join('')}}</tbody></table>`;
}}
render();
</script>
</body>
</html>
"""
    (HTML / "vitar-group-content-planner.html").write_text(html, encoding="utf-8")


def main():
    pages = load_pages()
    rows = make_group_pages(pages)
    summary = section_summary(rows)
    payload = write_json(rows, summary)
    write_csv(rows)
    write_report(payload)
    write_html(payload)
    print(json.dumps({
        "domain": payload["domain"],
        "pages": payload["pages"],
        "sections": len(payload["sections"]),
        "report": str(REPORTS / "vitar-group-content-plan.md"),
        "html": str(HTML / "vitar-group-content-planner.html"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
