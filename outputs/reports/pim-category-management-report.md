# VITAR ecommerce PIM preparation

Generated: 2026-06-01T11:06:14.893010+00:00

## Executive Summary

- Scraped raw product records: 548
- Recommended master products after SKU/EAN dedupe: 333
- Main VITAR human supplement assortment: 293 master products
- Separate/non-main assortment: 40 master products
- Cross-site duplicate records merged: 215
- Recommended source strategy: NašeVitamíny for commerce fields, VITAR.cz for brand/content enrichment.

## Portfolio Structure

Recommended navigation order: separate portfolios first for governance visibility, then brand-led entry points, then customer-need categories. Veterinary products should be present in PIM and reporting, but excluded from the main VITAR human supplement taxonomy.

| Separate portfolio | Products | Recommendation | Top forms |
|---|---:|---|---|
| Veterinae - samostatný sortiment | 40 | Zobrazit jako separátní sekci/portfolio mimo hlavní VITAR strom pro lidské doplňky. V PIM ponechat stejné produktové atributy, ale navigačně a SEO oddělit. | Neurčeno (16), Prášek / sypká směs (12), Sirup / elixír (8), Nápoj (4) |

### Brand Navigation

| Brand | Products | Role | Top categories | Top forms |
|---|---:|---|---|---|
| Maxi Vita | 90 | Core vitamin/mineral umbrella; primary brand landing. | Imunita a nachlazení (22), Hořčík a minerály (18), Ostatní / nezařazeno (11), Močové cesty (10) | Neurčeno (53), Šumivé tablety (21), Sirup / elixír (10), Nápoj (3) |
| Vitar | 58 | Functional legacy products and pharmacy staples. | Hořčík a minerály (13), Ostatní / nezařazeno (12), Imunita a nachlazení (8), Krása, vlasy, pleť (8) | Neurčeno (30), Šumivé tablety (8), Kosmetika (6), Tablety (5) |
| Maxi Vita Essentials | 16 | Modern premium/lifestyle sub-brand; strong for segmented landings. | Hořčík a minerály (7), Energie, stres, spánek (5), Klouby a pohyb (2), Krása, vlasy, pleť (1) | Neurčeno (16) |
| Revital | 19 | Effervescent/value vitamin line. | Imunita a nachlazení (9), Hořčík a minerály (8), Energie, stres, spánek (1), Močové cesty (1) | Neurčeno (11), Šumivé tablety (8) |
| Revital Botanicals | 9 | Botanical/effervescent sub-line; use as brand plus format story. | Imunita a nachlazení (4), Hořčík a minerály (3), Energie, stres, spánek (2) | Šumivé tablety (9) |
| Energit | 15 | Energy/glucose/dextrose; separate sport/energy intent. | Energie, stres, spánek (6), Imunita a nachlazení (4), Hořčík a minerály (2), Děti (1) | Neurčeno (12), Tablety (3) |
| Predator | 20 | Repellents and parasite protection; seasonal separate cluster. | Repelenty a paraziti (20) | Neurčeno (15), Kosmetika (3), Nápoj (2) |
| Capri-Sun | 16 | Beverage/distribution portfolio; keep outside supplement taxonomy where needed. | Nápoje a pitný režim (13), Děti (2), Zrak (1) | Nápoj (9), Neurčeno (7) |
| Vitar Kids | 8 | Kids portfolio; brand and target-group landing. | Děti (6), Hořčík a minerály (1), Imunita a nachlazení (1) | Neurčeno (4), Tablety (2), Stick pack (1), Nápoj (1) |
| Vitar Eko | 12 | Eco/natural positioning; support with quality and ingredient filters. | Trávení a detox (6), Imunita a nachlazení (3), Hořčík a minerály (2), Klouby a pohyb (1) | Neurčeno (10), Kapsle (2) |
| Revitalon | 5 | Hair/beauty line; beauty category + brand landing. | Krása, vlasy, pleť (5) | Kapsle (2), Nápoj (1), Neurčeno (1), Kosmetika (1) |
| Irbis | 10 | Sweeteners; separate food/sweetener cluster. | Sladidla (10) | Tablety (7), Prášek / sypká směs (3) |
| eMVe | 7 | Value vitamin line; brand filter, lower SEO priority. | Hořčík a minerály (3), Imunita a nachlazení (3), Srdce a oběh (1) | Neurčeno (7) |
| OvoCé | 3 | Powdered drink range; drinks/pitný režim. | Nápoje a pitný režim (3) | Prášek / sypká směs (3) |
| Vyprošťovák | 3 | Hangover micro-brand; campaign/seasonal landing. | Vyprošťovák (3) | Šumivé tablety (2), Neurčeno (1) |
| Vitar Kings | 2 | Male/lifestyle line; target group male. | Srdce a oběh (2) | Kapsle (1), Stick pack (1) |

## Category Management Recommendation

Use a hybrid model: top-level brand entry points for recognisable VITAR lines, then main category navigation by customer need. Keep brands indexable where they carry demand, but let filters and category pages solve shopping intent.

| Category | Products | Top brands | Top forms | SEO title |
|---|---:|---|---|---|
| Hořčík a minerály | 57 | Maxi Vita (18), Vitar (13), Revital (8), Maxi Vita Essentials (7), Revital Botanicals (3) | Neurčeno (36), Šumivé tablety (17), Nápoj (2), Tablety (1), Prášek / sypká směs (1) | Hořčík, zinek, vápník a minerály \| Vitar |
| Imunita a nachlazení | 54 | Maxi Vita (22), Revital (9), Vitar (8), Energit (4), Revital Botanicals (4) | Neurčeno (32), Šumivé tablety (14), Sirup / elixír (3), Tablety (2), Nápoj (2) | Vitamíny na imunitu a nachlazení \| Vitar |
| Nápoje a pitný režim | 23 | Capri-Sun (13), Vitar (6), OvoCé (3), Maxi Vita (1) | Nápoj (11), Neurčeno (6), Prášek / sypká směs (4), Šumivé tablety (2) | Nápoje a pitný režim \| Vitar |
| Ostatní / nezařazeno | 23 | Vitar (12), Maxi Vita (11) | Neurčeno (16), Šumivé tablety (5), Tablety (1), Kosmetika (1) | Ostatní / nezařazeno \| Vitar |
| Krása, vlasy, pleť | 22 | Maxi Vita (8), Vitar (8), Revitalon (5), Maxi Vita Essentials (1) | Neurčeno (9), Kosmetika (6), Kapsle (3), Tablety (3), Nápoj (1) | Kolagen, biotin a péče o vlasy, nehty a pleť \| Vitar |
| Repelenty a paraziti | 20 | Predator (20) | Neurčeno (15), Kosmetika (3), Nápoj (2) | Repelenty a paraziti \| Vitar |
| Močové cesty | 17 | Maxi Vita (10), Vitar (5), Energit (1), Revital (1) | Neurčeno (9), Sirup / elixír (5), Nápoj (1), Prášek / sypká směs (1), Tablety (1) | Močové cesty \| Vitar |
| Energie, stres, spánek | 15 | Energit (6), Maxi Vita Essentials (5), Revital Botanicals (2), Revital (1), Vitar (1) | Neurčeno (10), Šumivé tablety (3), Tablety (2) | Doplňky pro energii, stres a klidný spánek \| Vitar |
| Děti | 13 | Vitar Kids (6), Maxi Vita (4), Capri-Sun (2), Energit (1) | Neurčeno (7), Nápoj (2), Stick pack (2), Sirup / elixír (1), Tablety (1) | Vitamíny a doplňky pro děti \| Vitar Kids a Maxi Vita Kids |
| Sladidla | 12 | Irbis (10), Vitar (2) | Tablety (7), Prášek / sypká směs (3), Šumivé tablety (2) | Sladidla \| Vitar |
| Trávení a detox | 11 | Vitar Eko (6), Maxi Vita (5) | Neurčeno (7), Šumivé tablety (2), Kapsle (2) | Trávení a detox \| Vitar |
| Zrak | 8 | Maxi Vita (5), Capri-Sun (1), Energit (1), Maxi Vita Essentials (1) | Neurčeno (7), Sirup / elixír (1) | Zrak \| Vitar |
| Srdce a oběh | 8 | Maxi Vita (3), Vitar (2), Vitar Kings (2), eMVe (1) | Neurčeno (5), Šumivé tablety (1), Kapsle (1), Stick pack (1) | Srdce a oběh \| Vitar |
| Klouby a pohyb | 7 | Maxi Vita (3), Maxi Vita Essentials (2), Vitar (1), Vitar Eko (1) | Neurčeno (7) | Klouby a pohyb \| Vitar |
| Vyprošťovák | 3 | Vyprošťovák (3) | Šumivé tablety (2), Neurčeno (1) | Vyprošťovák \| Vitar |

## Filter Model for PIM

| Priority | Filter | PIM field | UI behavior | SEO behavior | Source |
|---|---|---|---|---|---|
| P0 | Značka / produktová řada | `brand` | top navigation + filter | indexable brand pages | Vitar portfolio + GymBeam/BrainMarket brand navigation pattern |
| P0 | Hlavní potřeba | `category_recommendation` | main navigation after brands | indexable category landings | GymBeam and BrainMarket goal-based navigation |
| P0 | Forma | `form` | facet filter | noindex, selected curated landings only | PIM attribute, visible competitor pattern |
| P0 | Aktivní látky | `active_ingredients` | facet filter + search synonyms | curated landings for vitamin C, magnesium, collagen, omega-3, D3/K2 | manual/PIM enrichment, common supplement shopping behavior |
| P0 | Cílová skupina | `target_group` | facet filter | curated landings for děti, ženy, muži, senioři | iHerb/BrainMarket segment navigation |
| P1 | Věk | `age_group` | facet filter | noindex except selected child/senior pages | children/senior supplement segmentation |
| P1 | Bez cukru / vegan / gluten-free / lactose-free | `diet_flags` | facet filter | noindex | Vilgain lifestyle filters |
| P1 | Velikost balení | `pack_size` | facet filter or product comparison only | noindex | scraped attributes |
| P1 | Příchuť | `flavour` | facet filter for drinks/effervescent only | noindex | name extraction + PIM enrichment |
| P1 | Skladem / dostupnost | `availability` | toggle | noindex | NašeVitamíny commerce data + iHerb available items pattern |
| P2 | Cena za dávku / kus | `price_per_unit` | sort/comparison, not a primary facet | noindex | commerce calculation |
| P2 | Certifikace/testování/kvalita | `quality_claims` | trust badge + facet only when data exists | supporting content, not filter SEO | iHerb iTested trust pattern |

### Filters to suppress or keep out

| Filter / URL pattern | Why remove or suppress |
|---|---|
| Výrobce jako samostatný e-shop filter | Většina portfolia je VITAR, s.r.o.; používat raději značku/produktovou řadu. |
| Interní SKU/EAN jako facet | Patří do search/admin view, ne do zákaznické filtrace. |
| Cena jako rozsahový slider | U doplňků s nízkou cenovou disperzí má menší hodnotu než cena za dávku a řazení. |
| Duplicitní kombinace brand + potřeba jako indexované URL | Riziko thin/duplicate SEO. Indexovat jen ručně vybrané landing pages. |
| Veterinae v hlavní Vitar kategorii | Jiný shopper intent; držet jako oddělený sortiment mimo hlavní lidské doplňky. |

## SEO Setup

- Build indexable brand pages first for core demand: Maxi Vita, Vitar, Revital, Energit, Predator, Vitar Kids, Maxi Vita Essentials and selected micro-brands.
- Build one indexable landing page per customer need in the main assortment: immunity, magnesium/minerals, kids, beauty, joints, digestion/detox, energy/stress/sleep, eyes, heart, urinary, drinks and sweeteners.
- Keep Veterinae/Veterinary as a separate portfolio. It can have its own landing and product URLs, but it should not appear in the main VITAR human supplement category tree.
- Use noindex/follow for combinatorial filter URLs, except curated SEO landings such as `vitamin-c`, `horcik`, `kolagen`, `vitaminy-pro-deti`, `repelenty-pro-deti`.
- Product pages need structured data: Product, Offer, Brand, AggregateRating where available, BreadcrumbList and FAQ for claims/dosage questions.

## Competitor Patterns Used

- [GymBeam](https://gymbeam.cz/vitaminy/bez-prichuti): Hloubková navigace podle typu látky i cíle: imunita, spánek, vlasy/nehty/pokožka, stres, trávení, játra, nootropika.
- [Vilgain](https://vilgain.com/essential-vitamins-and-minerals/brand/vilgain): Používá kombinaci produktových a lifestyle filtrů: sale, new, in stock, vegan, gluten-free, caffeine-free, lactose-free.
- [iHerb](https://www.iherb.com/c/Multivitamins): Silná dôvera cez kvalitu: iTested, nezávislé laboratóriá, heavy metals/microbial testing a kategórie podľa segmentu.
- [BrainMarket](https://www.brainmarket.cz/doplnky-stravy/?pv462=5214): Navigácia delí doplnky podľa cieľa, typu vitamínu a segmentu: deti, muži, ženy, imunita, omega, probiotiká.

## Data Quality Risks

- Missing EAN: 40/333 master products.
- Unknown form: 183/333 master products.
- Main taxonomy excludes 40 separate products by design; keep them visible in admin/PIM QA.
- Active ingredients, dosage, health claims and contraindications require manual or NLP-assisted enrichment before final PIM import.
- Some VITAR content is richer than NašeVitamíny product text; merge descriptions deliberately instead of overwriting.

## Development Handoff

- Use `data/processed/pim-master.json` as the development seed.
- Use `data/processed/products.csv` for quick spreadsheet review.
- Use `outputs/pim-product-cards/*.md` for per-product editorial review.
- Use `outputs/html/vitar-category-planner.html` as the interactive category-management view.
