# VITAR ecommerce PIM preparation

Generated: 2026-06-01T10:40:50.097722+00:00

## Executive Summary

- Scraped raw product records: 548
- Recommended master products after SKU/EAN dedupe: 333
- Cross-site duplicate records merged: 215
- Recommended source strategy: NašeVitamíny for commerce fields, VITAR.cz for brand/content enrichment.

## Category Management Recommendation

The new e-shop should not mirror the old brand-first navigation. Use a hybrid model: primary navigation by customer need, secondary filters by brand/line, form, active ingredient and target group.

| Category | Products | Top brands | Top forms | SEO title |
|---|---:|---|---|---|
| Hořčík a minerály | 57 | Maxi Vita (18), Vitar (13), Revital (8), Maxi Vita Essentials (7), Revital Botanicals (3) | Neurčeno (36), Šumivé tablety (17), Nápoj (2), Tablety (1), Prášek / sypká směs (1) | Hořčík, zinek, vápník a minerály \| Vitar |
| Imunita a nachlazení | 54 | Maxi Vita (22), Revital (9), Vitar (8), Energit (4), Revital Botanicals (4) | Neurčeno (32), Šumivé tablety (14), Sirup / elixír (3), Tablety (2), Nápoj (2) | Vitamíny na imunitu a nachlazení \| Vitar |
| Veterinae a zvířata | 29 | Vitar Veterinae (28), Maxi Vita (1) | Neurčeno (15), Prášek / sypká směs (8), Nápoj (4), Sirup / elixír (2) | Veterinae a zvířata \| Vitar |
| Nápoje a pitný režim | 23 | Capri-Sun (13), Vitar (6), OvoCé (3), Maxi Vita (1) | Nápoj (11), Neurčeno (6), Prášek / sypká směs (4), Šumivé tablety (2) | Nápoje a pitný režim \| Vitar |
| Ostatní / nezařazeno | 23 | Vitar (12), Maxi Vita (11) | Neurčeno (16), Šumivé tablety (5), Tablety (1), Kosmetika (1) | Ostatní / nezařazeno \| Vitar |
| Krása, vlasy, pleť | 22 | Maxi Vita (8), Vitar (8), Revitalon (5), Maxi Vita Essentials (1) | Neurčeno (9), Kosmetika (6), Kapsle (3), Tablety (3), Nápoj (1) | Kolagen, biotin a péče o vlasy, nehty a pleť \| Vitar |
| Repelenty a paraziti | 20 | Predator (20) | Neurčeno (15), Kosmetika (3), Nápoj (2) | Repelenty a paraziti \| Vitar |
| Klouby a pohyb | 18 | Vitar Veterinae (11), Maxi Vita (3), Maxi Vita Essentials (2), Vitar (1), Vitar Eko (1) | Neurčeno (8), Sirup / elixír (6), Prášek / sypká směs (4) | Klouby a pohyb \| Vitar |
| Močové cesty | 17 | Maxi Vita (10), Vitar (5), Energit (1), Revital (1) | Neurčeno (9), Sirup / elixír (5), Nápoj (1), Prášek / sypká směs (1), Tablety (1) | Močové cesty \| Vitar |
| Energie, stres, spánek | 15 | Energit (6), Maxi Vita Essentials (5), Revital Botanicals (2), Revital (1), Vitar (1) | Neurčeno (10), Šumivé tablety (3), Tablety (2) | Doplňky pro energii, stres a klidný spánek \| Vitar |
| Děti | 13 | Vitar Kids (6), Maxi Vita (4), Capri-Sun (2), Energit (1) | Neurčeno (7), Nápoj (2), Stick pack (2), Sirup / elixír (1), Tablety (1) | Vitamíny a doplňky pro děti \| Vitar Kids a Maxi Vita Kids |
| Sladidla | 12 | Irbis (10), Vitar (2) | Tablety (7), Prášek / sypká směs (3), Šumivé tablety (2) | Sladidla \| Vitar |
| Trávení a detox | 11 | Vitar Eko (6), Maxi Vita (5) | Neurčeno (7), Šumivé tablety (2), Kapsle (2) | Trávení a detox \| Vitar |
| Srdce a oběh | 8 | Maxi Vita (3), Vitar (2), Vitar Kings (2), eMVe (1) | Neurčeno (5), Šumivé tablety (1), Kapsle (1), Stick pack (1) | Srdce a oběh \| Vitar |
| Zrak | 8 | Maxi Vita (5), Capri-Sun (1), Energit (1), Maxi Vita Essentials (1) | Neurčeno (7), Sirup / elixír (1) | Zrak \| Vitar |
| Vyprošťovák | 3 | Vyprošťovák (3) | Šumivé tablety (2), Neurčeno (1) | Vyprošťovák \| Vitar |

## Filter Model for PIM

| Priority | Filter | PIM field | Source |
|---|---|---|---|
| P0 | Značka / produktová řada | `brand` | scraped brand detection |
| P0 | Hlavní potřeba | `category_recommendation` | PIM managed taxonomy |
| P0 | Forma | `form` | PIM attribute |
| P0 | Aktivní látky | `active_ingredients` | manual/PIM enrichment |
| P0 | Cílová skupina | `target_group` | manual/PIM enrichment |
| P1 | Věk | `age_group` | manual/PIM enrichment |
| P1 | Bez cukru / vegan / gluten-free / lactose-free | `diet_flags` | manual/PIM enrichment |
| P1 | Velikost balení | `pack_size` | scraped attributes |
| P1 | Příchuť | `flavour` | manual/extracted from name |
| P2 | Cena za dávku / kus | `price_per_unit` | commerce calculation |
| P2 | Certifikace/testování/kvalita | `quality_claims` | manual/PIM enrichment |

## SEO Setup

- Build one indexable landing page per customer need: immunity, magnesium/minerals, kids, beauty, joints, digestion/detox, energy/stress/sleep, eyes, heart, urinary, repellents, pets, drinks, sweeteners.
- Keep brand pages indexable for Maxi Vita, Vitar, Revital, Predator, Energit, Capri-Sun, Veterinae and Essentials, but do not make brand the only navigation path.
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
- Active ingredients, dosage, health claims and contraindications require manual or NLP-assisted enrichment before final PIM import.
- Some VITAR content is richer than NašeVitamíny product text; merge descriptions deliberately instead of overwriting.

## Development Handoff

- Use `data/processed/pim-master.json` as the development seed.
- Use `data/processed/products.csv` for quick spreadsheet review.
- Use `outputs/pim-product-cards/*.md` for per-product editorial review.
- Use `outputs/html/vitar-category-planner.html` as the interactive category-management view.
