# Vitar Ecommerce

Project workspace for `jurajgiacko/vitarecommerce`.

## PIM discovery outputs

This workspace contains a first-pass scrape and category-management preparation for:

- `vitar.cz`
- `nasevitaminy.cz`

Main deliverables:

- `data/processed/products.json` - raw normalized product records from both sources.
- `data/processed/products.csv` - spreadsheet-friendly product export.
- `data/processed/pim-master.json` - deduplicated master products for development/PIM planning.
- `outputs/reports/pim-category-management-report.md` - category, filter, SEO and competitor recommendations.
- `outputs/html/vitar-category-planner.html` - interactive local category planner.
- `outputs/pim-product-cards/*.md` - one markdown card per scraped product record.

Run the pipeline:

```bash
python3 scripts/scrape_products.py --site all --refresh
python3 scripts/build_pim_outputs.py
```

`data/raw/` is intentionally ignored because it contains the downloaded HTML cache.
