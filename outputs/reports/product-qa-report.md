# VITAR product QA and PIM readiness

Generated: 2026-06-01T19:09:17.998809+00:00

## Verdict

This is now a QA workbench, not only a scraped product list. Category counts are internally consistent, but final PIM import still requires manual decisions for blocked, separate-review and inferred-field products.

## Count Control

- Raw scraped records: 548
- Master products: 333
- Current main VITAR count: 293
- Current separate count: 40
- Current category count sum: 293 (OK)
- Proposed main keep count after QA actions: 270

## QA Status

- review: 108
- blocked: 6
- ready: 162
- separate_review: 57

## Recommended Actions

- keep_as_drinks_portfolio_review: 12
- exclude_from_main_or_accessories: 6
- keep_in_main_pim: 258
- separate_vitar_sport_review: 17
- separate_veterinae: 40

## Proposed Category Counts for Main Keep Assortment

| Category | Products |
|---|---:|
| Imunita a nachlazení | 69 |
| Hořčík a minerály | 46 |
| Energie, stres, spánek | 28 |
| Krása, vlasy, pleť | 22 |
| Repelenty a paraziti | 20 |
| Nápoje a pitný režim | 18 |
| Močové cesty | 16 |
| Trávení a detox | 12 |
| Sladidla | 11 |
| Zrak | 7 |
| Děti | 6 |
| Klouby a pohyb | 6 |
| Srdce a oběh | 6 |
| Vyprošťovák | 3 |

## Critical Issue Counts

- exclude_from_main_or_accessories: 6
- separate_vitar_sport_review: 17

## Warning Counts

- missing_price: 44
- category_recommended_change: 66
- missing_need_states: 184
- missing_ean: 40
- form_inferred_needs_check: 97
- missing_form: 86

## Blocked Products

These should not go into the final import without a decision.

| Product | Brand | Action | Proposed category | Issues | URL |
| --- | --- | --- | --- | --- | --- |
| Capri-Sun Dětský batoh pejsek | Capri-Sun | exclude_from_main_or_accessories | Doplňky a merchandising | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/capri-sun-detsky-batoh |
| Capri-Sun láhev | Capri-Sun | exclude_from_main_or_accessories | Doplňky a merchandising | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/capri-sun-lahev |
| Capri-Sun taška | Capri-Sun | exclude_from_main_or_accessories | Doplňky a merchandising | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/capri-sun-taska |
| Capri-Sun osuška | Capri-Sun | exclude_from_main_or_accessories | Doplňky a merchandising | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/capri-sun-osuska |
| Maxi Vita dávkovač léků denní | Maxi Vita | exclude_from_main_or_accessories | Doplňky a merchandising | exclude_from_main_or_accessories | https://www.vitar.cz/maxi-vita-davkovac-leku-denni-1417/ |
| Maxi Vita dávkovač léků týdenní | Maxi Vita | exclude_from_main_or_accessories | Doplňky a merchandising | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/maxi-vita-davkovac-leku-tydenni |

## Separate Review

These products belong in a separate portfolio or SBU decision path.

| Product | Current brand | Proposed brand | Action | Proposed category | URL |
| --- | --- | --- | --- | --- | --- |
| Energetické tablety | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/energeticke-tablety/ |
| PRE Sport | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/enervit-pre-sport/ |
| Energetické nápoje | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/energeticke-napoje/ |
| Iontový nápoj | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/iontovy-napoj/ |
| Proteinové nápoje | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/proteinove-napoje/ |
| Regenerační nápoje | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/regeneracni-napoje/ |
| Aminokyseliny | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/aminokyseliny-enervit/ |
| Energetické gely | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/energeticke-gely/ |
| Energetické tyčinky | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/energeticke-tycinky/ |
| Kompresní bandáže | Vitar | Vitar | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/kompresni-bandaze/ |
| Kompresní kraťasy | Vitar | Vitar | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/kompresni-kratasy/ |
| Kompresní lýtkové návleky | Vitar | ROYAL BAY | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/kompresni-lytkove-navleky/ |
| Kompresní pažní návleky | Vitar | ROYAL BAY | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/kompresni-pazni-navleky/ |
| Kompresní podkolenky | Vitar | ROYAL BAY | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/kompresni-podkolenky/ |
| Kompresní stehenní návleky | Vitar | Vitar | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/kompresni-stehenni-navleky/ |
| Proteinové tyčinky | Vitar | Enervit | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/proteinove-tycinky-enervit/ |
| Sportovní ponožky | Vitar | ROYAL BAY | separate_vitar_sport_review | Sport / VITAR Sport SBU | https://www.vitar.cz/sportovni-ponozky/ |
| Maxi Vita Herbal Kurkuma | Maxi Vita | Maxi Vita | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/maxi-vita-herbal-kurkuma |
| VITAR Veterinae ArtiVit Pegas Forte 7 | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/vitar-veterinae-artivit-pegas-forte-7-700g |
| VITAR Veterinae Artivit sirup 1000 ml | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/vitar-veterinae-artivit-sirup-1000ml |
| VITAR Veterinae Artivit sirup 200 ml | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/vitar-veterinae-artivit-sirup-200-ml-2 |
| VITAR Veterinae Balíček ArtiVit sirup 500 ml + cestovní miska ZDARMA | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/balicek-artivit-sir-500-ml-cestovni-miska-2 |
| VITAR Veterinae balíček Artivit sirup + DentOn + Lososový olej | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/balicek-artivit-sir-1000-ml-denton100g-losos-olej-2 |
| VITAR Veterinae balíček Artivit sirup 200 ml + DentOn 50 g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/balicek-artivit-sirup-200-denton-50 |
| VITAR Veterinae balíček Artivit sirup 500 ml + Lososový olej 200 ml | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/balicek-artivit-sirup500-ml-lososovy-olej-200-ml |
| Vitar Veterinae ArtiVit Pegas MSM | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/vitar-veterinae-artivit-pegas-msm-smes-720g |
| Vitar Veterinae Artivit Forte sypká směs / 70 g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/vitar-veterinae-artivit-forte-sypka-smes-70-g |
| Vitar Veterinae Artivit Forte sypká směs /400g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/vitar-veterinae-artivit-forte-sypka-smes-400g |
| Vitar Veterinae Artivit Forte sypká směs/600g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Klouby a pohyb | https://www.nasevitaminy.cz/vitar-veterinae-artivit-forte-sypka-smes-600g |
| VITAR Veterinae Artivit sirup 500 ml | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-artivit-sirup-500-ml-2 |
| VITAR Veterinae DentON sypká směs 100 g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-denton-sypka-smes-100g |
| VITAR Veterinae DentON sypká směs 50 g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-denton-sypka-smes-50g |
| VITAR Veterinae GasterON SYMBIO | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-gasteron-symbio-28-g-doza |
| VITAR Veterinae Konopný olej | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.vitar.cz/vitar-veterinae-konopny-olej/ |
| VITAR Veterinae Konopný olej (1000 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-konopny-olej-1000-ml |
| VITAR Veterinae Konopný olej (200 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-konopny-olej-200-ml |
| VITAR Veterinae Konopný olej (500 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-konopny-olej-500-ml |
| VITAR Veterinae Lněný olej | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.vitar.cz/vitar-veterinae-lneny-olej/ |
| VITAR Veterinae Lněný olej (1000 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-lneny-olej-1000-ml |
| VITAR Veterinae Lněný olej (200 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-lneny-olej-200-ml |
| VITAR Veterinae Lněný olej (500 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-lneny-olej-500-ml |
| VITAR Veterinae Lososový olej | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.vitar.cz/vitar-veterinae-lososovy-olej/ |
| VITAR Veterinae Lososový olej (1000 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-lososovy-olej-1000-ml |
| VITAR Veterinae Lososový olej (200 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-lososovy-olej-200-ml |
| VITAR Veterinae Lososový olej (500 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-lososovy-olej-500-ml |
| VITAR Veterinae Mineral Forte sypká směs 500 g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-mineral-forte-sypka-smes-500g |
| VITAR Veterinae Mineral Forte sypká směs 80 g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-mineral-forte-sypka-smes-80g |
| VITAR Veterinae Minerál Forte sypká směs 800 g | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-mineral-forte-sypka-smes-800g |
| VITAR Veterinae Multivit Forte želé | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-multivit-forte-zele-40ks |
| VITAR Veterinae Ostropestřec olej | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.vitar.cz/vitar-veterinae-ostropestrec-olej/ |
| VITAR Veterinae Ostropestřec olej (1000 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-ostropestrec-olej-1000-ml |
| VITAR Veterinae Ostropestřec olej (200 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-ostropestrec-olej-200-ml |
| VITAR Veterinae Ostropestřec olej (500 ml) | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.nasevitaminy.cz/vitar-veterinae-ostropestrec-olej-500-ml |
| Vitar Veterinae ArtiVit Forte prášek | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.vitar.cz/vitar-veterinae-artivit-forte-prasek/ |
| Vitar Veterinae ArtiVit sirup | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.vitar.cz/vitar-veterinae-artivit-sirup/ |
| Vitar Veterinae DentON | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.vitar.cz/vitar-veterinae-denton/ |
| Vitar Veterinae Mineral Forte | Vitar Veterinae | Vitar Veterinae | separate_veterinae | Veterinae a zvířata | https://www.vitar.cz/vitar-veterinae-mineral-forte/ |

## Category Fix Candidates

| Product | Current | Proposed | Confidence | Action | URL |
| --- | --- | --- | --- | --- | --- |
| Capri-Sun Multivitamin 0,33 l | Děti | Nápoje a pitný režim | medium | keep_as_drinks_portfolio_review | https://www.vitar.cz/capri-sun-multivitamin-0-33-l/ |
| Capri-Sun Pomeranč + broskev 0,33 l | Děti | Nápoje a pitný režim | medium | keep_as_drinks_portfolio_review | https://www.vitar.cz/capri-sun-pomeranc-broskev-0-33-l/ |
| Capri-Sun Dětský batoh pejsek | Nápoje a pitný režim | Doplňky a merchandising | medium | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/capri-sun-detsky-batoh |
| Capri-Sun láhev | Nápoje a pitný režim | Doplňky a merchandising | medium | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/capri-sun-lahev |
| Capri-Sun taška | Nápoje a pitný režim | Doplňky a merchandising | medium | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/capri-sun-taska |
| Capri-Sun osuška | Zrak | Doplňky a merchandising | medium | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/capri-sun-osuska |
| Energit Hroznový cukr multivitamin | Energie, stres, spánek | Imunita a nachlazení | medium | keep_in_main_pim | https://www.vitar.cz/energit-hroznovy-cukr-multivitamin/ |
| Energit Hroznový cukr multivitamin - citron | Energie, stres, spánek | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/energit-hroznovy-cukr-multivitamin-pomeranc |
| Energit Hroznový cukr multivitamin - jahoda | Energie, stres, spánek | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/energit-hroznovy-cukr-multivitamin-jahoda |
| Energit Hroznový cukr multivitamin - třešeň | Energie, stres, spánek | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/energit-hroznovy-cukr-multivitamin-tresen |
| Maxi Vita Kids Multivitamin + kolostrum | Děti | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-kids-multivitamin-kolostrum |
| Maxi Vita Exclusive Magnézium - šumivé tablety | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-exclusive-magnezium |
| Maxi Vita Hořčík + vitaminy B6, B12 a biotin \| Volba spotřebitelů - Nejlepší novinka 2025 | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-magnesium-20-eff-tbl |
| Maxi Vita Kids Multivitamin Bob a Bobek | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-multivit-kids-bob-a-bobek-20-eff-tbl |
| Maxi Vita Kids Multivitamin želé | Hořčík a minerály | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-kids-multivitamin-zele |
| Maxi Vita Magnézium 400 mg + B komplex + vitamin C | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-magnezium-400-mg-b-komplex-vitamin-c |
| Maxi Vita B-komplex forte + vitamin C | Imunita a nachlazení | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-b-komplex-forte-vitamin-c |
| Maxi Vita Železo + vitamin C kyselina listová | Imunita a nachlazení | Hořčík a minerály | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-zelezo-20-eff-tbl |
| Maxi Vita B12 + B2 | Ostatní / nezařazeno | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-b12-b2-20-eff-tbl |
| Maxi Vita Exclusive Odvodnění | Ostatní / nezařazeno | Trávení a detox | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-exclusive-odvodneni-20-eff-tbl |
| Maxi Vita HerbaVOX - lišejník islandský | Ostatní / nezařazeno | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-herbavox-lisejnik-islandsky |
| Maxi Vita HerbaVOX - med a citron | Ostatní / nezařazeno | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-herbavox-med-a-citron |
| Maxi Vita Premium Ca+Mg+ vit. D3, C | Ostatní / nezařazeno | Hořčík a minerály | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-premium-ca-mg-vit-d3-c-20-eff-tbl |
| Maxi Vita Premium Multivitamin | Ostatní / nezařazeno | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-premium-multivitamin-20-eff |
| Maxi Vita Premium Super linie | Ostatní / nezařazeno | Trávení a detox | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-premium-super-linie |
| Maxi Vita dávkovač léků denní | Ostatní / nezařazeno | Doplňky a merchandising | medium | exclude_from_main_or_accessories | https://www.vitar.cz/maxi-vita-davkovac-leku-denni-1417/ |
| Maxi Vita dávkovač léků týdenní | Ostatní / nezařazeno | Doplňky a merchandising | medium | exclude_from_main_or_accessories | https://www.nasevitaminy.cz/maxi-vita-davkovac-leku-tydenni |
| Maxi Vita Železo + kyselina listová | Ostatní / nezařazeno | Hořčík a minerály | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxi-vita-zelezo-kyselina-listova |
| MaxiVita Herbal HerbaVOX zázvor | Ostatní / nezařazeno | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/maxivita-herbal-herbavox-zazvor-24-tbl-blistr |
| Revital Ferrodyn - šumivé tablety | Energie, stres, spánek | Hořčík a minerály | medium | keep_in_main_pim | https://www.nasevitaminy.cz/revital-ferrodyn |
| Revital Hořčík + vitamin B6 | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.vitar.cz/revital-horcik-vitamin-b6/ |
| Revital Hořčík + vitamin B6 - grep | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/revital-horcik-vitamin-b6-grep |
| Revital Hořčík + vitamin B6 - černý rybíz | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/revital-horcik-vitamin-b6-cerny-rybiz |
| Revital Tripple pack 3 x 20 tablet | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/revital-tripple-pack-3-x-20-eff-3-prichute |
| Revital L-Tryptofan forte | Močové cesty | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-l-tryptofan-forte |
| Revital Botanicals Multivitamín + Minerály \| Šumivé tablety s extrakty | Hořčík a minerály | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/revital-botanicals-multivitamin-mineraly |
| Energetické tablety | Hořčík a minerály | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/energeticke-tablety/ |
| Vitar Magnézium 400 mg + vitamin B6 + vitamin C | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.vitar.cz/vitar-magnezium-400-mg-vitamin-b6-vitamin-c-1734/ |
| Vitar Magnézium 400 mg + vitamin B6 + vitamin C - grep | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-magnezium-400-mg-vitamin-b6-vitamin-c-grep |
| Vitar Magnézium 400 mg + vitamin B6 + vitamin C - mango | Hořčík a minerály | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-magnezium-400-mg-vitamin-b6-vitamin-c-mango |
| PRE Sport | Klouby a pohyb | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/enervit-pre-sport/ |
| Energetické nápoje | Nápoje a pitný režim | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/energeticke-napoje/ |
| Iontový nápoj | Nápoje a pitný režim | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/iontovy-napoj/ |
| Proteinové nápoje | Nápoje a pitný režim | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/proteinove-napoje/ |
| Regenerační nápoje | Nápoje a pitný režim | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/regeneracni-napoje/ |
| Aminokyseliny | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/aminokyseliny-enervit/ |
| Energetické gely | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/energeticke-gely/ |
| Energetické tyčinky | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/energeticke-tycinky/ |
| Kompresní bandáže | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/kompresni-bandaze/ |
| Kompresní kraťasy | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/kompresni-kratasy/ |
| Kompresní lýtkové návleky | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/kompresni-lytkove-navleky/ |
| Kompresní pažní návleky | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/kompresni-pazni-navleky/ |
| Kompresní podkolenky | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/kompresni-podkolenky/ |
| Kompresní stehenní návleky | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/kompresni-stehenni-navleky/ |
| Proteinové tyčinky | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/proteinove-tycinky-enervit/ |
| Sportovní ponožky | Ostatní / nezařazeno | Sport / VITAR Sport SBU | medium | separate_vitar_sport_review | https://www.vitar.cz/sportovni-ponozky/ |
| Vitamin B12 - bez cukru | Ostatní / nezařazeno | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitamin-b12-bez-cukru-20-4-eff-tbl |
| Multivitamin - bez cukru - šumivé tablety | Sladidla | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/multivitamin-bez-cukru |
| Vitar EKO B-komplex forte | Trávení a detox | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-eko-b-komplex-forte |
| Vitar Kids Multi želé DUOPACK | Děti | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-kids-multi-zele-duopack-2-x-50-zele |
| Vitar Kids Multivitamin | Děti | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-kids-multivitamin |
| Vitar Kids Multivitamin + kolostrum | Děti | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-kids-multivitamin-kolostrum |
| Vitar Kids Multivitamin + kolostrum DUOPACK | Děti | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-kids-multi-kolostr-um-duopack-2-x-45-tbl |
| Vitar Kids Multivitamin želé | Hořčík a minerály | Imunita a nachlazení | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-kids-multivitamin-zele |
| Vitar Kings LIPOMAGNE + B komplex | Srdce a oběh | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-kings-lipomagne-b-komplex-60-cps-blistr |
| Vitar Kings LIPOMAGNE + B komplex sypká směs | Srdce a oběh | Energie, stres, spánek | medium | keep_in_main_pim | https://www.nasevitaminy.cz/vitar-kings-lipomagne-b-komplex-20-stick |

## Brand Fix Candidates

| Product | Current brand | Proposed brand | Action | URL |
| --- | --- | --- | --- | --- |
| Energetické tablety | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/energeticke-tablety/ |
| PRE Sport | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/enervit-pre-sport/ |
| Energetické nápoje | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/energeticke-napoje/ |
| Iontový nápoj | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/iontovy-napoj/ |
| Proteinové nápoje | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/proteinove-napoje/ |
| Regenerační nápoje | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/regeneracni-napoje/ |
| Aminokyseliny | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/aminokyseliny-enervit/ |
| Energetické gely | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/energeticke-gely/ |
| Energetické tyčinky | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/energeticke-tycinky/ |
| Kompresní lýtkové návleky | Vitar | ROYAL BAY | separate_vitar_sport_review | https://www.vitar.cz/kompresni-lytkove-navleky/ |
| Kompresní pažní návleky | Vitar | ROYAL BAY | separate_vitar_sport_review | https://www.vitar.cz/kompresni-pazni-navleky/ |
| Kompresní podkolenky | Vitar | ROYAL BAY | separate_vitar_sport_review | https://www.vitar.cz/kompresni-podkolenky/ |
| Proteinové tyčinky | Vitar | Enervit | separate_vitar_sport_review | https://www.vitar.cz/proteinove-tycinky-enervit/ |
| Sportovní ponožky | Vitar | ROYAL BAY | separate_vitar_sport_review | https://www.vitar.cz/sportovni-ponozky/ |

## Ready / Review Split

- Ready now: 162
- Needs review/enrichment: 108
- Blocked: 6
- Separate review: 57

Recommended next move: use `outputs/data/product-qa.csv` as the client/PIM review sheet, resolve blocked and separate-review items first, then lock the final category tree.
