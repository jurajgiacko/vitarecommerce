#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "processed" / "pim-master.json"
RAW_PRODUCTS = ROOT / "data" / "processed" / "products.json"
OUT = ROOT / "outputs"
PROCESSED = ROOT / "data" / "processed"
PUBLIC_DATA = OUT / "data"
REPORTS = OUT / "reports"
HTML = OUT / "html"


FORM_RULES = [
    ("effervescent_tablets", "Šumivé tablety", ["šumiv", "sumiv", "eff", "20 eff"]),
    ("tablets", "Tablety", ["tablet", "tablety", "tbl", "želé", "zele", "pastil", "hroznový cukr", "hroznovy cukr"]),
    ("capsules", "Kapsle", ["kaps", "cps", "kapsle"]),
    ("stick_pack", "Stick pack", ["stick"]),
    ("syrup", "Sirup / elixír", ["sirup", "elix"]),
    ("powder", "Prášek / sypká směs", ["práš", "pras", "sypk", "směs", "smes"]),
    ("drink", "Nápoj", ["nápoj", "napoj", "0,2", "0.2", "0,33", "0.33", "330 ml", "200 ml"]),
    ("oil", "Olej", ["olej"]),
    ("cosmetic", "Kosmetika", ["šampon", "sampon", "sérum", "serum", "vazel", "gel"]),
    ("accessory", "Doplněk / merchandising", ["batoh", "taška", "taska", "láhev", "lahev", "osuška", "osuska", "dávkovač léků", "davkovac leku"]),
    ("sports_wear", "Sportovní textil / komprese", ["kompres", "návlek", "navlek", "podkolen", "ponož", "ponoz", "kraťas", "kratas", "bandáž", "bandaz"]),
]

CATEGORY_OVERRIDES = [
    ("sport_sbu", "Sport / VITAR Sport SBU", ["enervit", "royal bay", "energetické gely", "energeticke gely", "proteinové tyčinky", "proteinove tycinky", "kompres", "sportovní ponožky", "sportovni ponozky"]),
    ("accessories", "Doplňky a merchandising", ["batoh", "taška", "taska", "láhev", "lahev", "osuška", "osuska", "dávkovač léků", "davkovac leku"]),
    ("capri_drinks", "Nápoje a pitný režim", ["capri-sun", "capri sun"]),
    ("ca_mg", "Hořčík a minerály", ["ca+mg", "ca mg", "vápník-hořčík", "vapnik-horcik"]),
    ("b_vitamins", "Energie, stres, spánek", ["b12", "b2", "b-komplex", "vitamin b"]),
    ("drainage_weight", "Trávení a detox", ["odvodnění", "odvodneni", "super linie"]),
    ("throat", "Imunita a nachlazení", ["herbavox", "lišejník", "lisejnik"]),
    ("iron", "Hořčík a minerály", ["železo", "zelezo", "kyselina listová", "kyselina listova"]),
    ("multivitamin", "Imunita a nachlazení", ["multivitamin"]),
]

INGREDIENT_RULES = [
    ("vitamin C", ["vitamin c", "vit. c", "acerola"]),
    ("hořčík", ["hořčík", "horcik", "magnézium", "magnezium", "magnesium"]),
    ("zinek", ["zinek"]),
    ("vápník", ["vápník", "vapnik", "calcium"]),
    ("vitamin D3", ["vitamin d3", "d3"]),
    ("vitamin K2", ["vitamin k2", "k2"]),
    ("omega-3", ["omega 3", "omega-3", "rybí olej", "rybi olej"]),
    ("kolagen", ["kolagen"]),
    ("rakytník", ["rakytn", "rakytník"]),
    ("betaglukan", ["betaglukan", "beta glukan"]),
    ("echinacea", ["echinacea"]),
    ("brusinky", ["brusink"]),
    ("koenzym Q10", ["q10", "koenzym"]),
    ("železo", ["železo", "zelezo"]),
    ("ashwagandha", ["ashwagandha"]),
    ("ginkgo", ["ginkgo"]),
    ("lutein", ["lutein"]),
    ("probiotika", ["probiotik"]),
]

TARGET_RULES = [
    ("děti", ["kids", "děti", "deti", "pro děti", "pro deti", "kolostrum"]),
    ("muži", ["alphamale", "muž", "muz", "erektor", "kings"]),
    ("ženy", ["fembalance", "goddess", "hormonal", "vlasy", "pleť", "plet", "nehty"]),
    ("senioři", ["pro babi", "pro dědu", "pro dedu"]),
    ("sport", ["sport", "enervit", "energy", "dextróza", "dextroza", "kompres"]),
    ("zvířata", ["veterinae", "pes", "kočka", "kocka", "zvíř", "zvir"]),
]

DIET_RULES = [
    ("bez cukru", ["bez cukru", "zero"]),
    ("eko/natural", ["eko", "natural", "bio"]),
    ("vegan-check-needed", ["vegan"]),
]


def norm(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def master_key(product):
    return product.get("ean") or product.get("sku") or product.get("product_id")


def load_raw_index():
    payload = json.loads(RAW_PRODUCTS.read_text(encoding="utf-8"))
    index = defaultdict(list)
    for product in payload["products"]:
        index[master_key(product)].append(product)
    return index


def haystack(product):
    pieces = [
        product.get("name"),
        product.get("slug"),
        product.get("description"),
        product.get("brand"),
        json.dumps(product.get("attributes", {}), ensure_ascii=False),
        " ".join(product.get("breadcrumbs") or []),
    ]
    return norm(" ".join(p for p in pieces if p)).lower()


def match_rules(text, rules):
    found = []
    for value, words in rules:
        if any(word in text for word in words):
            found.append(value)
    return found


def field_present(record, field):
    value = record.get(field)
    if field == "form":
        return bool(value and value.get("key") != "unknown")
    if field == "content_sections":
        return bool(value)
    if field == "attributes":
        return bool(value)
    if isinstance(value, str):
        return bool(norm(value))
    return value is not None and value != []


def preview_value(value):
    if isinstance(value, dict):
        if "label" in value:
            return norm(value["label"])
        return ", ".join(list(value.keys())[:5])
    if isinstance(value, list):
        return ", ".join(norm(v) for v in value[:5])
    return norm(value)[:160]


def source_analysis(product, raw_records):
    by_site = {}
    for record in raw_records:
        site = record["source_site"]
        current = by_site.get(site)
        if not current or len(record.get("description") or "") > len(current.get("description") or ""):
            by_site[site] = record

    fields = ["sku", "ean", "price_czk", "availability", "description", "image", "form", "attributes", "content_sections"]
    coverage = {}
    links = {}
    for site in ["vitar.cz", "nasevitaminy.cz"]:
        record = by_site.get(site)
        links[site] = record.get("url") if record else ""
        coverage[site] = {field: field_present(record, field) if record else False for field in fields}

    recoverable = []
    for field in fields:
        if field_present(product, field):
            continue
        for site, record in by_site.items():
            if field_present(record, field):
                recoverable.append({
                    "field": field,
                    "source_site": site,
                    "value_preview": preview_value(record.get(field)),
                    "url": record.get("url"),
                })
                break

    complements = []
    for field in fields:
        sites = [site for site in ["vitar.cz", "nasevitaminy.cz"] if coverage[site][field]]
        if len(sites) == 1:
            complements.append({"field": field, "available_on": sites[0]})

    return {
        "source_count": len(raw_records),
        "source_sites": sorted(by_site.keys()),
        "has_both_sources": "vitar.cz" in by_site and "nasevitaminy.cz" in by_site,
        "links": links,
        "coverage": coverage,
        "recoverable_missing_fields": recoverable,
        "source_complements": complements,
    }


def infer_form(product):
    current = product.get("form", {})
    if current.get("key") and current.get("key") != "unknown":
        return {
            "key": current["key"],
            "label": current.get("label", current["key"]),
            "confidence": "high",
            "source": "scraped_or_existing_attribute",
        }
    text = haystack(product)
    for key, label, words in FORM_RULES:
        if any(word in text for word in words):
            return {
                "key": key,
                "label": label,
                "confidence": "medium",
                "source": "qa_name_inference",
            }
    return {
        "key": "unknown",
        "label": "Neurčeno",
        "confidence": "low",
        "source": "missing",
    }


def proposed_category(product):
    current = product.get("category_recommendation", {})
    text = haystack(product)
    for key, label, words in CATEGORY_OVERRIDES:
        if any(word in text for word in words):
            return {
                "key": key,
                "label": label,
                "confidence": "medium",
                "source": "qa_override_rule",
                "changed": label != current.get("label"),
            }
    score = current.get("score", 0)
    if current.get("key") == "other":
        confidence = "low"
    elif score >= 2:
        confidence = "high"
    else:
        confidence = "medium"
    return {
        "key": current.get("key", "other"),
        "label": current.get("label", "Ostatní / nezařazeno"),
        "confidence": confidence,
        "source": "current_taxonomy",
        "changed": False,
    }


def proposed_brand(product):
    text = haystack(product)
    if "enervit" in text:
        return {"label": "Enervit", "confidence": "high", "changed": product.get("brand") != "Enervit"}
    if "royal bay" in text:
        return {"label": "ROYAL BAY", "confidence": "high", "changed": product.get("brand") != "ROYAL BAY"}
    if "vedici" in text or "védici" in text:
        return {"label": "Vedici", "confidence": "high", "changed": product.get("brand") != "Vedici"}
    return {"label": product.get("brand") or "Unknown", "confidence": "current", "changed": False}


def recommended_action(product, form, category, brand):
    scope = product.get("assortment_scope", {}).get("key")
    text = haystack(product)
    if scope == "separate_veterinary":
        return "separate_veterinae"
    if category["key"] == "sport_sbu" or brand["label"] in {"Enervit", "ROYAL BAY", "Vedici"}:
        return "separate_vitar_sport_review"
    if category["key"] == "accessories" or form["key"] in {"accessory", "sports_wear"}:
        return "exclude_from_main_or_accessories"
    if "capri-sun" in text and form["key"] == "drink":
        return "keep_as_drinks_portfolio_review"
    return "keep_in_main_pim"


def qa_flags(product, form, category, action):
    flags = []
    critical = []
    warnings = []

    if not product.get("sku"):
        critical.append("missing_sku")
    if not product.get("image"):
        critical.append("missing_image")
    if not product.get("description"):
        critical.append("missing_description")
    if category["key"] == "other":
        critical.append("category_unassigned")
    if action in {"separate_vitar_sport_review", "exclude_from_main_or_accessories"}:
        critical.append(action)

    if not product.get("ean"):
        warnings.append("missing_ean")
    if not product.get("price_czk"):
        warnings.append("missing_price")
    if form["key"] == "unknown":
        warnings.append("missing_form")
    if category["confidence"] == "low":
        warnings.append("low_category_confidence")
    if form["confidence"] == "medium":
        warnings.append("form_inferred_needs_check")
    if category.get("changed"):
        warnings.append("category_recommended_change")
    if not product.get("need_states"):
        warnings.append("missing_need_states")

    flags.extend(critical)
    flags.extend(warnings)
    return flags, critical, warnings


def readiness(product, form, category, critical, warnings, action):
    score = 100
    penalties = {
        "missing_sku": 35,
        "missing_image": 30,
        "missing_description": 25,
        "category_unassigned": 30,
        "separate_vitar_sport_review": 20,
        "exclude_from_main_or_accessories": 25,
        "missing_ean": 10,
        "missing_price": 6,
        "missing_form": 15,
        "low_category_confidence": 15,
        "form_inferred_needs_check": 5,
        "category_recommended_change": 8,
        "missing_need_states": 4,
        "missing_info_available_on_other_source": 2,
    }
    for flag in critical + warnings:
        score -= penalties.get(flag, 3)
    if product.get("assortment_scope", {}).get("key") == "separate_veterinary":
        score = min(score, 75)
    score = max(0, score)
    if critical:
        status = "blocked"
    elif score >= 85 and form["key"] != "unknown" and category["confidence"] != "low":
        status = "ready"
    else:
        status = "review"
    if action in {"separate_veterinae", "separate_vitar_sport_review"}:
        status = "separate_review"
    return score, status


def qa_product(product, raw_records):
    text = haystack(product)
    form = infer_form(product)
    category = proposed_category(product)
    brand = proposed_brand(product)
    ingredients = match_rules(text, INGREDIENT_RULES)
    targets = match_rules(text, TARGET_RULES)
    diet_flags = match_rules(text, DIET_RULES)
    action = recommended_action(product, form, category, brand)
    sources = source_analysis(product, raw_records)
    flags, critical, warnings = qa_flags(product, form, category, action)
    if sources["recoverable_missing_fields"]:
        warnings.append("missing_info_available_on_other_source")
        flags.append("missing_info_available_on_other_source")
    score, status = readiness(product, form, category, critical, warnings, action)
    return {
        "master_key": product.get("pim_recommendation", {}).get("master_key"),
        "name": product.get("name"),
        "current_brand": product.get("brand"),
        "proposed_brand": brand["label"],
        "brand_changed": brand["changed"],
        "sku": product.get("sku"),
        "ean": product.get("ean"),
        "price_czk": product.get("price_czk"),
        "source_site": product.get("source_site"),
        "url": product.get("url"),
        "image": product.get("image"),
        "assortment_scope": product.get("assortment_scope", {}).get("key"),
        "current_category": product.get("category_recommendation", {}).get("label"),
        "proposed_category": category["label"],
        "category_confidence": category["confidence"],
        "category_changed": category["changed"],
        "current_form": product.get("form", {}).get("label"),
        "proposed_form": form["label"],
        "form_confidence": form["confidence"],
        "active_ingredients_suggested": ingredients,
        "target_groups_suggested": targets,
        "diet_flags_suggested": diet_flags,
        "recommended_action": action,
        "qa_status": status,
        "readiness_score": score,
        "critical_issues": critical,
        "warnings": warnings,
        "flags": flags,
        "source_records": product.get("source_records", []),
        "source_analysis": sources,
        "vitar_url": sources["links"].get("vitar.cz", ""),
        "nasevitaminy_url": sources["links"].get("nasevitaminy.cz", ""),
        "cross_source_recoverable_fields": [item["field"] for item in sources["recoverable_missing_fields"]],
    }


def summarize(rows, master_payload):
    main = [r for r in rows if r["assortment_scope"] == "main_vitar"]
    main_keep = [r for r in main if r["recommended_action"] in {"keep_in_main_pim", "keep_as_drinks_portfolio_review"}]
    categories = Counter(r["proposed_category"] for r in main_keep)
    both_sources = sum(1 for r in rows if r["source_analysis"]["has_both_sources"])
    recoverable_rows = [r for r in rows if r["cross_source_recoverable_fields"]]
    source_field_counts = defaultdict(Counter)
    for row in rows:
        for site, coverage in row["source_analysis"]["coverage"].items():
            for field, present in coverage.items():
                if present:
                    source_field_counts[site][field] += 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "master_products": len(rows),
        "raw_records": master_payload["raw_records"],
        "main_products_current": master_payload["main_products"],
        "separate_products_current": master_payload["separate_products"],
        "qa_status_counts": dict(Counter(r["qa_status"] for r in rows)),
        "recommended_action_counts": dict(Counter(r["recommended_action"] for r in rows)),
        "critical_issue_counts": dict(Counter(i for r in rows for i in r["critical_issues"])),
        "warning_counts": dict(Counter(i for r in rows for i in r["warnings"])),
        "proposed_category_counts_main_keep": dict(categories.most_common()),
        "current_category_count_sum": sum(c["count"] for c in master_payload["categories"]),
        "proposed_main_keep_count": len(main_keep),
        "current_counts_match": sum(c["count"] for c in master_payload["categories"]) == master_payload["main_products"],
        "both_source_products": both_sources,
        "single_source_products": len(rows) - both_sources,
        "recoverable_missing_info_products": len(recoverable_rows),
        "recoverable_missing_field_counts": dict(Counter(field for r in rows for field in r["cross_source_recoverable_fields"])),
        "source_field_counts": {site: dict(counts) for site, counts in source_field_counts.items()},
        "products": rows,
    }


def write_outputs(payload):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    HTML.mkdir(parents=True, exist_ok=True)

    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    (PROCESSED / "product-qa.json").write_text(json_text, encoding="utf-8")
    (PUBLIC_DATA / "product-qa.json").write_text(json_text, encoding="utf-8")

    csv_fields = [
        "qa_status", "readiness_score", "recommended_action", "name", "current_brand", "proposed_brand",
        "sku", "ean", "price_czk", "current_category", "proposed_category", "category_confidence",
        "current_form", "proposed_form", "form_confidence", "active_ingredients_suggested",
        "target_groups_suggested", "diet_flags_suggested", "critical_issues", "warnings",
        "vitar_url", "nasevitaminy_url", "cross_source_recoverable_fields", "url",
    ]
    for csv_path in [PROCESSED / "product-qa.csv", PUBLIC_DATA / "product-qa.csv"]:
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=csv_fields)
            writer.writeheader()
            for row in payload["products"]:
                flat = dict(row)
                for key in ["active_ingredients_suggested", "target_groups_suggested", "diet_flags_suggested", "critical_issues", "warnings", "cross_source_recoverable_fields"]:
                    flat[key] = ", ".join(flat.get(key) or [])
                writer.writerow({field: flat.get(field, "") for field in csv_fields})

    write_report(payload)
    write_html(payload)


def md_table(rows, columns):
    def cell(value):
        if isinstance(value, list):
            value = ", ".join(value)
        return norm(value).replace("|", "\\|")
    lines = [
        "| " + " | ".join(label for label, _ in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(row.get(key, "")) for _, key in columns) + " |")
    return lines


def write_report(payload):
    rows = payload["products"]
    blocked = [r for r in rows if r["qa_status"] == "blocked"]
    separate = [r for r in rows if r["qa_status"] == "separate_review"]
    review = [r for r in rows if r["qa_status"] == "review"]
    ready = [r for r in rows if r["qa_status"] == "ready"]
    unassigned = [r for r in rows if "category_unassigned" in r["critical_issues"]]
    changed_categories = [r for r in rows if r["category_changed"]]
    brand_changes = [r for r in rows if r["brand_changed"]]
    recoverable = [r for r in rows if r["cross_source_recoverable_fields"]]

    lines = [
        "# VITAR product QA and PIM readiness",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Verdict",
        "",
        "This is now a QA workbench, not only a scraped product list. Category counts are internally consistent, but final PIM import still requires manual decisions for blocked, separate-review and inferred-field products.",
        "",
        "## Count Control",
        "",
        f"- Raw scraped records: {payload['raw_records']}",
        f"- Master products: {payload['master_products']}",
        f"- Current main VITAR count: {payload['main_products_current']}",
        f"- Current separate count: {payload['separate_products_current']}",
        f"- Current category count sum: {payload['current_category_count_sum']} ({'OK' if payload['current_counts_match'] else 'MISMATCH'})",
        f"- Proposed main keep count after QA actions: {payload['proposed_main_keep_count']}",
        f"- Products found on both `vitar.cz` and `nasevitaminy.cz`: {payload['both_source_products']}",
        f"- Products found on one source only: {payload['single_source_products']}",
        f"- Products with missing fields recoverable from the other source: {payload['recoverable_missing_info_products']}",
        "",
        "## QA Status",
        "",
    ]
    for key, count in payload["qa_status_counts"].items():
        lines.append(f"- {key}: {count}")
    lines.extend([
        "",
        "## Recommended Actions",
        "",
    ])
    for key, count in payload["recommended_action_counts"].items():
        lines.append(f"- {key}: {count}")
    lines.extend([
        "",
        "## Proposed Category Counts for Main Keep Assortment",
        "",
        "| Category | Products |",
        "|---|---:|",
    ])
    for category, count in payload["proposed_category_counts_main_keep"].items():
        lines.append(f"| {category} | {count} |")

    lines.extend([
        "",
        "## Critical Issue Counts",
        "",
    ])
    for key, count in payload["critical_issue_counts"].items():
        lines.append(f"- {key}: {count}")
    lines.extend([
        "",
        "## Warning Counts",
        "",
    ])
    for key, count in payload["warning_counts"].items():
        lines.append(f"- {key}: {count}")

    lines.extend([
        "",
        "## Cross-source Field Coverage",
        "",
        "| Source | SKU | EAN | Price | Availability | Description | Image | Form | Attributes | Content sections |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for site in ["vitar.cz", "nasevitaminy.cz"]:
        counts = payload["source_field_counts"].get(site, {})
        lines.append(
            f"| {site} | {counts.get('sku', 0)} | {counts.get('ean', 0)} | {counts.get('price_czk', 0)} | "
            f"{counts.get('availability', 0)} | {counts.get('description', 0)} | {counts.get('image', 0)} | "
            f"{counts.get('form', 0)} | {counts.get('attributes', 0)} | {counts.get('content_sections', 0)} |"
        )

    lines.extend([
        "",
        "## Missing Info Recoverable From Other Source",
        "",
        "These are records where the selected master view misses a field, but another scraped source has it.",
        "",
    ])
    lines.extend(md_table(recoverable[:100], [
        ("Product", "name"),
        ("Missing/recoverable fields", "cross_source_recoverable_fields"),
        ("VITAR URL", "vitar_url"),
        ("NašeVitamíny URL", "nasevitaminy_url"),
    ]))

    lines.extend([
        "",
        "## Blocked Products",
        "",
        "These should not go into the final import without a decision.",
        "",
    ])
    lines.extend(md_table(blocked[:80], [
        ("Product", "name"),
        ("Brand", "current_brand"),
        ("Action", "recommended_action"),
        ("Proposed category", "proposed_category"),
        ("Issues", "critical_issues"),
        ("URL", "url"),
    ]))

    lines.extend([
        "",
        "## Separate Review",
        "",
        "These products belong in a separate portfolio or SBU decision path.",
        "",
    ])
    lines.extend(md_table(separate[:80], [
        ("Product", "name"),
        ("Current brand", "current_brand"),
        ("Proposed brand", "proposed_brand"),
        ("Action", "recommended_action"),
        ("Proposed category", "proposed_category"),
        ("URL", "url"),
    ]))

    lines.extend([
        "",
        "## Category Fix Candidates",
        "",
    ])
    lines.extend(md_table((unassigned + changed_categories)[:100], [
        ("Product", "name"),
        ("Current", "current_category"),
        ("Proposed", "proposed_category"),
        ("Confidence", "category_confidence"),
        ("Action", "recommended_action"),
        ("URL", "url"),
    ]))

    lines.extend([
        "",
        "## Brand Fix Candidates",
        "",
    ])
    lines.extend(md_table(brand_changes[:80], [
        ("Product", "name"),
        ("Current brand", "current_brand"),
        ("Proposed brand", "proposed_brand"),
        ("Action", "recommended_action"),
        ("URL", "url"),
    ]))

    lines.extend([
        "",
        "## Ready / Review Split",
        "",
        f"- Ready now: {len(ready)}",
        f"- Needs review/enrichment: {len(review)}",
        f"- Blocked: {len(blocked)}",
        f"- Separate review: {len(separate)}",
        "",
        "Recommended next move: use `outputs/data/product-qa.csv` as the client/PIM review sheet, resolve blocked and separate-review items first, then lock the final category tree.",
    ])
    (REPORTS / "product-qa-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload):
    data = json.dumps(payload, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VITAR Product QA Dashboard</title>
<style>
:root {{ --bg:#f6f7f9; --panel:#fff; --line:#dfe3e8; --text:#1d2430; --muted:#667085; --green:#27704a; --blue:#235f9e; --amber:#b45309; --red:#b42318; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); }}
header {{ position:sticky; top:0; z-index:4; background:var(--panel); border-bottom:1px solid var(--line); padding:14px 20px; display:flex; justify-content:space-between; gap:12px; align-items:center; }}
h1 {{ margin:0; font-size:18px; }}
button, input, select {{ font:inherit; }}
.btn {{ border:1px solid var(--line); background:#f2f4f7; border-radius:6px; padding:7px 10px; cursor:pointer; color:var(--text); text-decoration:none; }}
.btn.primary {{ background:var(--green); border-color:var(--green); color:white; }}
.wrap {{ padding:16px; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin-bottom:14px; }}
.stat {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px; }}
.stat b {{ display:block; font-size:24px; }}
.stat span {{ color:var(--muted); font-size:12px; }}
.toolbar {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px; }}
.toolbar input, .toolbar select {{ border:1px solid var(--line); border-radius:6px; padding:8px 10px; background:white; min-width:180px; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line); }}
th, td {{ border-bottom:1px solid var(--line); padding:8px 9px; text-align:left; vertical-align:top; font-size:12px; }}
th {{ position:sticky; top:56px; background:#f2f4f7; z-index:3; color:#475467; }}
.pill {{ display:inline-block; border-radius:999px; padding:2px 7px; font-size:11px; background:#eef2ff; margin:1px; white-space:nowrap; }}
.ready {{ background:#dcfce7; color:#166534; }}
.review {{ background:#fef3c7; color:#92400e; }}
.blocked {{ background:#fee2e2; color:#991b1b; }}
.separate_review {{ background:#dbeafe; color:#1d4ed8; }}
.muted {{ color:var(--muted); }}
.name {{ font-weight:650; min-width:260px; }}
a {{ color:var(--blue); }}
</style>
</head>
<body>
<header>
  <h1>VITAR <span style="color:var(--green)">Product QA Dashboard</span></h1>
  <div>
    <a class="btn" href="../data/product-qa.csv">CSV</a>
    <a class="btn" href="../data/product-qa.json">JSON</a>
    <a class="btn primary" href="../reports/product-qa-report.md">Report</a>
  </div>
</header>
<div class="wrap">
  <div class="stats" id="stats"></div>
  <div class="toolbar">
    <input id="q" placeholder="Search product, SKU, EAN..." oninput="render()">
    <select id="status" onchange="render()"></select>
    <select id="action" onchange="render()"></select>
    <select id="category" onchange="render()"></select>
  </div>
  <table>
    <thead><tr><th>Status</th><th>Score</th><th>Product</th><th>Action</th><th>Brand</th><th>Category</th><th>Form</th><th>Ingredients</th><th>Issues</th><th>Source</th></tr></thead>
    <tbody id="rows"></tbody>
  </table>
</div>
<script>
const DATA = {data};
const products = DATA.products;
function counts(key) {{
  const out = new Map();
  products.forEach(p => out.set(p[key], (out.get(p[key]) || 0) + 1));
  return [...out.entries()].sort((a,b) => b[1]-a[1]);
}}
function optionList(id, label, values) {{
  const el = document.getElementById(id);
  el.innerHTML = `<option value="">${{label}}</option>` + values.map(([v,n]) => `<option value="${{v}}">${{v}} (${{n}})</option>`).join('');
}}
function init() {{
  optionList('status', 'All statuses', counts('qa_status'));
  optionList('action', 'All actions', counts('recommended_action'));
  optionList('category', 'All proposed categories', counts('proposed_category'));
  document.getElementById('stats').innerHTML = [
    ['Master products', DATA.master_products],
    ['Current main', DATA.main_products_current],
    ['Current separate', DATA.separate_products_current],
    ['Current count check', DATA.current_counts_match ? 'OK' : 'Mismatch'],
    ['Proposed main keep', DATA.proposed_main_keep_count],
    ['Ready', DATA.qa_status_counts.ready || 0],
    ['Review', DATA.qa_status_counts.review || 0],
    ['Blocked', DATA.qa_status_counts.blocked || 0],
    ['On both sources', DATA.both_source_products],
    ['Recoverable info', DATA.recoverable_missing_info_products],
  ].map(([label,value]) => `<div class="stat"><b>${{value}}</b><span>${{label}}</span></div>`).join('');
}}
function pill(value, cls='') {{ return `<span class="pill ${{cls}}">${{value}}</span>`; }}
function sourceLinks(p) {{
  const links = [];
  if (p.vitar_url) links.push(`<a href="${{p.vitar_url}}" target="_blank">vitar.cz</a>`);
  if (p.nasevitaminy_url) links.push(`<a href="${{p.nasevitaminy_url}}" target="_blank">nasevitaminy.cz</a>`);
  const recoverable = (p.cross_source_recoverable_fields || []).map(x => pill('can fill '+x, 'review')).join('');
  return links.join('<br>') + (recoverable ? `<div>${{recoverable}}</div>` : '');
}}
function render() {{
  const q = document.getElementById('q').value.toLowerCase();
  const status = document.getElementById('status').value;
  const action = document.getElementById('action').value;
  const category = document.getElementById('category').value;
  const rows = products.filter(p =>
    (!q || [p.name,p.sku,p.ean,p.current_brand,p.proposed_brand].join(' ').toLowerCase().includes(q)) &&
    (!status || p.qa_status === status) &&
    (!action || p.recommended_action === action) &&
    (!category || p.proposed_category === category)
  );
  document.getElementById('rows').innerHTML = rows.map(p => `<tr>
    <td>${{pill(p.qa_status, p.qa_status)}}</td>
    <td><b>${{p.readiness_score}}</b></td>
    <td class="name">${{p.name}}<div class="muted">SKU ${{p.sku || '-'}} · EAN ${{p.ean || '-'}}</div></td>
    <td>${{p.recommended_action}}</td>
    <td>${{p.current_brand}}${{p.brand_changed ? '<br><b>→ '+p.proposed_brand+'</b>' : ''}}</td>
    <td>${{p.current_category}}${{p.category_changed ? '<br><b>→ '+p.proposed_category+'</b>' : ''}}<div class="muted">${{p.category_confidence}}</div></td>
    <td>${{p.current_form}}${{p.current_form !== p.proposed_form ? '<br><b>→ '+p.proposed_form+'</b>' : ''}}<div class="muted">${{p.form_confidence}}</div></td>
    <td>${{(p.active_ingredients_suggested || []).map(x => pill(x)).join('')}}</td>
    <td>${{[...(p.critical_issues || []), ...(p.warnings || [])].map(x => pill(x, p.critical_issues.includes(x) ? 'blocked' : 'review')).join('')}}</td>
    <td>${{sourceLinks(p)}}</td>
  </tr>`).join('');
}}
init();
render();
</script>
</body>
</html>
"""
    (HTML / "product-qa-dashboard.html").write_text(html, encoding="utf-8")


def main():
    master_payload = json.loads(MASTER.read_text(encoding="utf-8"))
    raw_index = load_raw_index()
    rows = [qa_product(product, raw_index.get(master_key(product), [])) for product in master_payload["products"]]
    payload = summarize(rows, master_payload)
    write_outputs(payload)
    print(json.dumps({
        "master_products": payload["master_products"],
        "qa_status_counts": payload["qa_status_counts"],
        "recommended_action_counts": payload["recommended_action_counts"],
        "current_counts_match": payload["current_counts_match"],
        "proposed_main_keep_count": payload["proposed_main_keep_count"],
        "both_source_products": payload["both_source_products"],
        "recoverable_missing_info_products": payload["recoverable_missing_info_products"],
        "html": str(HTML / "product-qa-dashboard.html"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
