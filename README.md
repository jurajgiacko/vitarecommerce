# Vitar Ecommerce

Project workspace for `jurajgiacko/vitarecommerce`.

## Onboarding & briefs (live)

- **E-commerce & Digital onboarding briefing** (internal): https://jurajgiacko.github.io/vitarecommerce/onboarding/
- **Developer brief — Vitar.cz e-shop** (for build/pricing): https://jurajgiacko.github.io/vitarecommerce/onboarding/dev-brief.html

Both live under `outputs/onboarding/`. Update = edit the HTML + push (Pages rebuilds, same URL).

### Target architecture (summary)

- **Two worlds:** static **VITAR Group** (corporate/B2B/OEM/careers, no cart, outside DC) + **e-com world** (transactional, via DC).
- **vitar.cz = product marketplace** (multi-brand, premium, new lines) — not a single-brand shop.
- **nasevitaminy.cz = retail** (classics, volume) — permanently separate, not merged/redirected into vitar.cz.
- **Shopify** storefront (leaving FastCentrik) · **Pohoda** ERP (one entity per company; QAD stays production/master-data only, outside fulfillment) · **one WMS + one shared DC**.
- Dataset scope: **548 scraped URLs → 333 master products** (271 vitar.cz / 39 Veterina separate / 17 Sport / 6 exclude), 16 brands, ~15 categories, 12 filters (with SEO index rules), 22-attribute PIM model, 238 content + 57 group pages. Overall readiness ~67% (assortment 92%, PIM 49%).

## PIM discovery outputs

This workspace contains a first-pass scrape and category-management preparation for:

- `vitar.cz`
- `nasevitaminy.cz`

Main deliverables:

- `data/processed/products.json` - raw normalized product records from both sources.
- `data/processed/products.csv` - spreadsheet-friendly product export.
- `data/processed/pim-master.json` - deduplicated master products for development/PIM planning.
- `data/processed/product-qa.json` - product QA, readiness scoring and recommended PIM actions.
- `data/processed/product-qa.csv` - spreadsheet-friendly QA review sheet for manual category/PIM cleanup.
- `data/processed/strategic-readiness.json` - strategic readiness, governance, PIM model and backlog payload.
- `data/processed/assortment-governance.csv` - SKU-level SBU/platform ownership recommendation.
- `data/processed/strategic-backlog.csv` - next-step backlog for VITAR GROUP, VITAR.cz, PIM and platform work.
- `data/processed/content-pages.json` - content, brand, category and corporate page inventory for migration.
- `data/processed/vitar-group-pages.json` - group-only content inventory for `vitar-group.cz`.
- `outputs/reports/pim-category-management-report.md` - category, filter, SEO and competitor recommendations.
- `outputs/reports/product-qa-report.md` - product count validation, blocked products, separate SBU candidates and category fix list.
- `outputs/reports/strategic-readiness-plan.md` - management-level readiness, governance, PIM model and strategic backlog.
- `outputs/reports/content-migration-inventory.md` - critical build-readiness and URL/content migration recommendation.
- `outputs/reports/vitar-group-content-plan.md` - sitemap and migration plan for the standalone VITAR Group website.
- `outputs/html/vitar-category-planner.html` - interactive local category planner.
- `outputs/html/product-qa-dashboard.html` - interactive product QA dashboard.
- `outputs/html/strategic-readiness-dashboard.html` - strategic readiness, governance and backlog dashboard.
- `outputs/html/vitar-group-content-planner.html` - interactive VITAR Group content planner.
- `outputs/pim-product-cards/*.md` - one markdown card per scraped product record.
- `outputs/content-pages/*.md` - one markdown card per scraped content/landing page.

GitHub Pages publishes the `outputs/` directory. After Pages is enabled for this
repository, the planner URL should be:

```text
https://jurajgiacko.github.io/vitarecommerce/
```

Run the pipeline:

```bash
python3 scripts/scrape_products.py --site all --refresh
python3 scripts/scrape_content_pages.py --site all
python3 scripts/build_pim_outputs.py
python3 scripts/build_product_qa.py
python3 scripts/build_strategy_outputs.py
python3 scripts/build_group_outputs.py
```

`data/raw/` is intentionally ignored because it contains the downloaded HTML cache.
