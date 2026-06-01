# VITAR product QA and PIM readiness

Generated: 2026-06-01T19:20:35.888351+00:00

## Verdict

This is now a QA workbench, not only a scraped product list. Category counts are internally consistent, but final PIM import still requires manual decisions for blocked, separate-review and inferred-field products.

## Count Control

- Raw scraped records: 548
- Master products: 333
- Current main VITAR count: 293
- Current separate count: 40
- Current category count sum: 293 (OK)
- Proposed main keep count after QA actions: 270
- Products found on both `vitar.cz` and `nasevitaminy.cz`: 214
- Products found on one source only: 119
- Products with missing fields recoverable from the other source: 114

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
- missing_info_available_on_other_source: 114
- missing_form: 86

## Cross-source Field Coverage

| Source | SKU | EAN | Price | Availability | Description | Image | Form | Attributes | Content sections |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| vitar.cz | 258 | 218 | 0 | 0 | 258 | 258 | 222 | 258 | 258 |
| nasevitaminy.cz | 289 | 289 | 289 | 289 | 289 | 289 | 122 | 289 | 289 |

## Missing Info Recoverable From Other Source

These are records where the selected master view misses a field, but another scraped source has it.

| Product | Missing/recoverable fields | VITAR URL | NašeVitamíny URL |
| --- | --- | --- | --- |
| Capri-Sun Mango + maracuja | form | https://www.vitar.cz/capri-sun-mango-maracuja-0-33-l/ | https://www.nasevitaminy.cz/capri-sun-mango-maracuja-0-33-l |
| Capri-Sun Višeň + granátové jablko | form | https://www.vitar.cz/capri-sun-visen-and-granatove-jablko-0-33-l/ | https://www.nasevitaminy.cz/capri-sun-visen-granatove-jablko-0-33-l |
| Energit Pro děti | form | https://www.vitar.cz/energit-pro-deti/ | https://www.nasevitaminy.cz/energit-pro-deti |
| Energit Pro řidiče | form | https://www.vitar.cz/energit-pro-ridice/ | https://www.nasevitaminy.cz/energit-pro-ridice |
| Energit Dextróza sport | form | https://www.vitar.cz/energit-dextroza-sport-magnezium-b6/ | https://www.nasevitaminy.cz/energit-dextroza-sport-magnezium-b6 |
| Energit Magnézium | form | https://www.vitar.cz/energit-magnezium/ | https://www.nasevitaminy.cz/energit-magnezium |
| Energit Imunita | form | https://www.vitar.cz/energit-imunita/ | https://www.nasevitaminy.cz/energit-imunita |
| Energit Multivitamin | form | https://www.vitar.cz/energit-multivitamin/ | https://www.nasevitaminy.cz/energit-multivitamin |
| Energit Vitamin D3 + acerola | form | https://www.vitar.cz/energit-vitamin-d3-acerola/ | https://www.nasevitaminy.cz/energit-vitamin-d3-acerola |
| Energit Pro oči | form | https://www.vitar.cz/energit-pro-oci/ | https://www.nasevitaminy.cz/energit-pro-oci |
| Maxi Vita Kids Multivitamin + kolostrum | form | https://www.vitar.cz/maxivita-kids-multivitamin-kolostrum/ | https://www.nasevitaminy.cz/maxi-vita-kids-multivitamin-kolostrum |
| Maxi Vita Kids Omega 3 + vitaminy D a E | form | https://www.vitar.cz/maxivita-kids-omega-3-vitaminy-d-a-e/ | https://www.nasevitaminy.cz/maxi-vita-kids-omega-3-vitaminy-d-a-e |
| Maxi Vita Exclusive Magnézium forte+ | form | https://www.vitar.cz/maxivita-exclusive-magnezium-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-magnezium-forte |
| Maxi Vita Exclusive Vápník–hořčík–zinek forte+ | form | https://www.vitar.cz/maxivita-exclusive-vapnik-horcik-zinek-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-vapnik-horcik-zinek-forte |
| Maxi Vita Hořčík + B6 | form | https://www.vitar.cz/maxivita-horcik-b6-1770/ | https://www.nasevitaminy.cz/maxi-vita-horcik-b6-2 |
| Maxi Vita Magnézium 400 mg + B komplex + vitamin C | form | https://www.vitar.cz/maxivita-magnezium-400-mg-b-komplex-vitamin-c/ | https://www.nasevitaminy.cz/maxi-vita-magnezium-400-mg-b-komplex-vitamin-c |
| Maxi Vita Premium Magnézium + aminokyseliny | form | https://www.vitar.cz/maxi-vita-premium-magnezium-aminokyseliny/ | https://www.nasevitaminy.cz/maxi-vita-premium-magnezium-aminokyseliny |
| Maxi Vita Selen + zinek + vitamin C a E | form | https://www.vitar.cz/maxivita-selen-zinek-vitamin-c-a-e/ | https://www.nasevitaminy.cz/maxi-vita-selen-zinek-vitamin-c-a-e |
| Maxi Vita Vitamin D3 1000 IU | form | https://www.vitar.cz/maxivita-vitamin-d3-1000-iu/ | https://www.nasevitaminy.cz/maxi-vita-vitamin-d3-1000-iu |
| Maxi Vita Vitamin D3 800 IU | form | https://www.vitar.cz/maxivita-vitamin-d3-800-iu/ | https://www.nasevitaminy.cz/maxi-vita-vitamin-d3-800-iu |
| Maxi Vita Vitamin K2 + D3 | form | https://www.vitar.cz/maxi-vita-exclusive-vitamin-k2-d3-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-vitamin-k2-d3-forte |
| Maxi Vita Vápník-hořčík-zinek | form | https://www.vitar.cz/maxivita-vapnik-horcik-zinek/ | https://www.nasevitaminy.cz/maxi-vita-vapnik-horcik-zinek |
| Maxi Vita Zinek 15 mg | form | https://www.vitar.cz/maxivita-zinek-15-mg/ | https://www.nasevitaminy.cz/maxi-vita-zinek-15-mg |
| Maxi Vita B-komplex forte + vitamin C | form | https://www.vitar.cz/maxivita-b-komplex-forte-vitamin-c/ | https://www.nasevitaminy.cz/maxi-vita-b-komplex-forte-vitamin-c |
| Maxi Vita Exclusive Posílení imunity forte+ | form | https://www.vitar.cz/maxivita-exclusive-posileni-imunity-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-posileni-imunity-forte |
| Maxi Vita Exclusive Rakytník forte+ | form | https://www.vitar.cz/maxivita-exclusive-rakytnik-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-rakytnik-forte |
| Maxi Vita Exclusive Vitamin C 800 mg forte+ | form | https://www.vitar.cz/maxivita-exclusive-vitamin-c-800-mg-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-vitamin-c-800-mg-forte |
| Maxi Vita Herbal Hlíva ústřičná | form | https://www.vitar.cz/maxivita-herbal-hliva-ustricna/ | https://www.nasevitaminy.cz/maxi-vita-herbal-hliva-ustricna |
| Maxi Vita Herbal Vitamin C + rakytník | form | https://www.vitar.cz/maxivita-herbal-vitamin-c-rakytnik/ | https://www.nasevitaminy.cz/maxi-vita-herbal-vitamin-c-rakytnik |
| Maxi Vita Kids Betaglukany + D3 | form | https://www.vitar.cz/maxi-vita-kids-betaglukan-multivitamin/ | https://www.nasevitaminy.cz/maxi-vita-kids-betaglukan-d3 |
| Maxi Vita Premium Probiotika + vitamin C | form | https://www.vitar.cz/maxi-vita-premium-probiotika-vitamin-c/ | https://www.nasevitaminy.cz/maxi-vita-premium-probiotika-vitamin-c |
| Maxi Vita Vitamin C + zinek | form | https://www.vitar.cz/maxivita-vitamin-c-zinek/ | https://www.nasevitaminy.cz/maxi-vita-vitamin-c-zinek |
| Maxi Vita Vitamin C komplex + acerola + šípek + zinek | form | https://www.vitar.cz/maxivita-vitamin-c-komplex-acerola-sipek-zinek/ | https://www.nasevitaminy.cz/maxi-vita-vitamin-c-komplex-acerola-sipek-zinek |
| Maxi Vita Exclusive Kloubní výživa | form | https://www.vitar.cz/maxivita-exclusive-kloubni-vyziva/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-kloubni-vyziva |
| Maxi Vita Exclusive Kolagen forte+ | form | https://www.vitar.cz/maxivita-exclusive-kolagen-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-kolagen-forte |
| Maxi Vita Premium Kloubní výživa | form | https://www.vitar.cz/maxivita-premium-kloubni-vyziva/ | https://www.nasevitaminy.cz/maxi-vita-premium-kloubni-vyziva |
| Maxi Vita Beauty Kyselina hyaluronová 100 mg + koenzym Q10 | form | https://www.vitar.cz/maxi-vita-beauty-kyselina-hyaluronova-100-mg-koenzym-q10/ | https://www.nasevitaminy.cz/maxi-vita-beauty-kyselina-hyaluronova-100-mg-koenzym-q10 |
| Maxi Vita Beauty Mořský kolagen | form | https://www.vitar.cz/maxivita-beauty-morsky-kolagen/ | https://www.nasevitaminy.cz/maxi-vita-beauty-morsky-kolagen |
| Maxi Vita Beta karoten | form | https://www.vitar.cz/maxivita-beta-karoten/ | https://www.nasevitaminy.cz/maxi-vita-beta-karoten |
| Maxi Vita Exclusive Beta-karoten forte+ | form | https://www.vitar.cz/maxivita-exclusive-beta-karoten-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-beta-karoten-forte |
| Maxi Vita Exclusive Krásné vlasy, nehty a pleť | form | https://www.vitar.cz/maxivita-exclusive-krasne-vlasy-nehty-a-plet/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-krasne-vlasy-nehty-a-plet |
| Maxi Vita Premium Zdravá pleť | form | https://www.vitar.cz/maxivita-premium-zdrava-plet/ | https://www.nasevitaminy.cz/maxi-vita-premium-zdrava-plet |
| Maxi Vita Premium Zdravé vlasy, nehty a pokožka | form | https://www.vitar.cz/maxivita-premium-zdrave-vlasy-nehty-a-pokozka/ | https://www.nasevitaminy.cz/maxi-vita-premium-zdrave-vlasy-nehty-a-pokozka |
| Maxi Vita Energy Power | form | https://www.vitar.cz/maxivita-energy-power/ | https://www.nasevitaminy.cz/maxi-vita-energy-power |
| Maxi Vita Herbal Ginkgo biloba | form | https://www.vitar.cz/maxivita-herbal-ginkgo-biloba/ | https://www.nasevitaminy.cz/maxi-vita-herbal-ginkgo-biloba |
| Maxi Vita Herbal Maxi brusinky | form | https://www.vitar.cz/maxivita-herbal-maxi-brusinky/ | https://www.nasevitaminy.cz/maxi-vita-herbal-maxi-brusinky |
| Maxi Vita Premium Probiotika s vlákninou a vitaminem C | form | https://www.vitar.cz/maxivita-premium-probiotika-s-vlakninou-a-vitaminem-c/ | https://www.nasevitaminy.cz/maxi-vita-premium-probiotika-s-vlakninou-a-vitaminem-c |
| Maxi Vita Premium Super linie | form | https://www.vitar.cz/maxivita-premium-super-linie/ | https://www.nasevitaminy.cz/maxi-vita-premium-super-linie |
| Maxi Vita Železo + kyselina listová | form | https://www.vitar.cz/maxivita-zelezo-kyselina-listova/ | https://www.nasevitaminy.cz/maxi-vita-zelezo-kyselina-listova |
| Maxi Vita Koenzym Q10 30 mg + vitamin C | form | https://www.vitar.cz/maxivita-koenzym-q10-30-mg-vitamin-c/ | https://www.nasevitaminy.cz/maxi-vita-koenzym-q10-30-mg-vitamin-c |
| Maxi Vita Omega 3 - rybí olej | form | https://www.vitar.cz/maxivita-omega-3-rybi-olej/ | https://www.nasevitaminy.cz/maxi-vita-omega-3-rybi-olej |
| Maxi Vita Chrom + garcinia cambogia | form | https://www.vitar.cz/maxivita-chrom-garcinia-cambogia/ | https://www.nasevitaminy.cz/maxi-vita-chrom-garcinia-cambogia |
| Maxi Vita Exclusive Erektor | form | https://www.vitar.cz/maxivita-exclusive-erektor/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-erektor |
| Maxi Vita Herbal Klidná střeva | form | https://www.vitar.cz/maxivita-herbal-klidna-streva/ | https://www.nasevitaminy.cz/maxi-vita-herbal-klidna-streva |
| Maxi Vita Exclusive Lutein forte+ | form | https://www.vitar.cz/maxivita-exclusive-lutein-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-lutein-forte |
| Maxi Vita Exclusive Omega 3 forte+ | form | https://www.vitar.cz/maxivita-exclusive-omega-3-forte/ | https://www.nasevitaminy.cz/maxi-vita-exclusive-omega-3-forte |
| Maxi Vita Herbal Očista jater | form | https://www.vitar.cz/maxivita-herbal-ocista-jater/ | https://www.nasevitaminy.cz/maxi-vita-herbal-ocista-jater |
| Maxi Vita Premium Zdravé oči | form | https://www.vitar.cz/maxivita-premium-zdrave-oci/ | https://www.nasevitaminy.cz/maxi-vita-premium-zdrave-oci |
| Maxi Vita Essentials AlphaMale<sup>®</sup> | form | https://www.vitar.cz/maxi-vita-essentials-alphamale/ | https://www.nasevitaminy.cz/maxi-vita-essentials-alphamale |
| Maxi Vita Essentials Ashwagandha | form | https://www.vitar.cz/maxi-vita-essentials-ashwagandha/ | https://www.nasevitaminy.cz/maxi-vita-essentials-ashwagandha-30 |
| Maxi Vita Essentials Ashwagandha | form | https://www.vitar.cz/maxi-vita-essentials-ashwagandha-60-kapsli/ | https://www.nasevitaminy.cz/maxi-vita-essentials-ashwagandha-60 |
| Maxi Vita Essentials Klidný spánek | form | https://www.vitar.cz/maxi-vita-essentials-klidny-spanek/ | https://www.nasevitaminy.cz/maxi-vita-essentials-klidny-spanek |
| Maxi Vita Essentials Mužská vitalita | form | https://www.vitar.cz/maxi-vita-essentials-muzska-vitalita/ | https://www.nasevitaminy.cz/maxi-vita-essentials-muzska-vitalita |
| Maxi Vita Essentials FemBalance<sup>®</sup> | form | https://www.vitar.cz/maxi-vita-essentials-fembalance/ | https://www.nasevitaminy.cz/maxi-vita-essentials-fembalance |
| Maxi Vita Essentials Goddess | form | https://www.vitar.cz/maxi-vita-essentials-goddess/ | https://www.nasevitaminy.cz/maxi-vita-essentials-goddess |
| Maxi Vita Essentials Hormonální pohoda | form | https://www.vitar.cz/maxi-vita-essentials-hormonalni-pohoda/ | https://www.nasevitaminy.cz/maxi-vita-essentials-hormon-pohoda |
| Maxi Vita Essentials Magnesium Bisglycinate | form | https://www.vitar.cz/maxi-vita-essentials-magnesium-bisglycinate/ | https://www.nasevitaminy.cz/maxi-vita-essentials-magnesium-bisglycinate |
| Maxi Vita Essentials Magnesium Malate | form | https://www.vitar.cz/maxi-vita-essentials-magnesium-malate/ | https://www.nasevitaminy.cz/maxi-vita-essentials-magnesium-malate |
| Maxi Vita Essentials Ranní energie | form | https://www.vitar.cz/maxi-vita-essentials-ranni-energie/ | https://www.nasevitaminy.cz/maxi-vita-essentials-ranni-energie |
| Maxi Vita Essentials Večerní pohoda | form | https://www.vitar.cz/maxi-vita-essentials-vecerni-pohoda/ | https://www.nasevitaminy.cz/maxi-vita-essentials-vecerni-pohoda |
| Maxi Vita Essentials Kloubní výživa | form | https://www.vitar.cz/maxi-vita-essentials-kloubni-vyziva/ | https://www.nasevitaminy.cz/maxi-vita-essentials-kloubni-vyziva |
| Maxi Vita Essentials Motion+ | form | https://www.vitar.cz/maxi-vita-essentials-motion/ | https://www.nasevitaminy.cz/maxi-vita-essentials-motion |
| Maxi Vita Essentials Krásná pleť | form | https://www.vitar.cz/maxi-vita-essentials-krasna-plet/ | https://www.nasevitaminy.cz/maxi-vita-essentials-krasna-plet |
| Maxi Vita Essentials RegenSleep<sup>®</sup> | form | https://www.vitar.cz/maxi-vita-essentials-regensleep/ | https://www.nasevitaminy.cz/maxi-vita-essentials-regensleep |
| Revital L-Tryptofan forte | form | https://www.vitar.cz/vitar-l-tryptofan-forte/ | https://www.nasevitaminy.cz/vitar-l-tryptofan-forte |
| Revitalon Revitalon Mořský kolagen DRINK 4 000 mg | form | https://www.vitar.cz/revitalon-morsky-kolagen-drink-4-000-mg/ | https://www.nasevitaminy.cz/revitalon-morsky-kolagen-drink-4-000-mg |
| Vitar Klidný spánek | form | https://www.vitar.cz/vitar-klidny-spanek/ | https://www.nasevitaminy.cz/vitar-klidny-spanek |
| Vitar Vitamin D3 Forte 1000 IU | form | https://www.vitar.cz/vitar-vitamin-d3-forte-1000-iu/ | https://www.nasevitaminy.cz/vitar-vitamin-d3-forte-1000-iu |
| Vitar Zinek 15 mg | form | https://www.vitar.cz/vitar-zinek-15-mg/ | https://www.nasevitaminy.cz/vitar-zinek-15-mg |
| Vitar Betaglukan 150 mg | form | https://www.vitar.cz/vitar-betaglukan/ | https://www.nasevitaminy.cz/vitar-betaglukan-150-mg |
| Vitar Probiotika pomeranč | form | https://www.vitar.cz/vitar-probiotika-pomeranc/ | https://www.nasevitaminy.cz/vitar-probiotika-pomeranc |
| Vitar Vitamin C | form | https://www.vitar.cz/vitar-vitamin-c/ | https://www.nasevitaminy.cz/vitar-vitamin-c |
| Vitar Vitamin C + zinek | form | https://www.vitar.cz/vitar-vitamin-c-zinek/ | https://www.nasevitaminy.cz/vitar-vitamin-c-zinek |
| Vitar Vitamin C + zinek + echinacea a šípek | form | https://www.vitar.cz/vitar-vitamin-c-zinek-echinacea-a-sipek/ | https://www.nasevitaminy.cz/vitar-vitamin-c-zinek-echinacea-a-sipek |
| Vitar Vitamin C 1000 mg s rakytníkem | form | https://www.vitar.cz/vitar-vitamin-c-1000-mg-s-rakytnikem/ | https://www.nasevitaminy.cz/vitar-vitamin-c-1000-mg-s-rakytnikem |
| Vitar Vitamin C 500 mg s rakytníkem | form | https://www.vitar.cz/vitar-vitamin-c-500-mg-s-rakytnikem/ | https://www.nasevitaminy.cz/vitar-vitamin-c-500-mg-s-rakytnikem |
| Vitar Ginkgo Biloba | form | https://www.vitar.cz/vitar-ginkgo-biloba-forte/ | https://www.nasevitaminy.cz/vitar-ginkgo-biloba-forte |
| Vitar Kanadské brusinky AKUT 500 mg | form | https://www.vitar.cz/vitar-kanadske-brusinky-akut-500-mg/ | https://www.nasevitaminy.cz/vitar-kanadske-brusinky-akut-500-mg |
| Vitar Vitamin K2 + D3 + B1 | form | https://www.vitar.cz/vitar-vitamin-k2-d3-forte/ | https://www.nasevitaminy.cz/vitar-vitamin-k2-d3-forte |
| Vitar Koenzym Q10 (100 mg) + vitamin E + selen + thiamin | form | https://www.vitar.cz/vitar-koenzym-q10-100-mg-vitamin-e-selen-thiamin/ | https://www.nasevitaminy.cz/vitar-koenzym-q10-100-mg-vitamin-e-selen-thiamin |
| Vitar Koenzym Q10 (60 mg) + vitamin E + selen + thiamin | form | https://www.vitar.cz/vitar-koenzym-q10-60-mg-vitamin-e-selen-thiamin/ | https://www.nasevitaminy.cz/vitar-koenzym-q10-60-mg-vitamin-e-selen-thiamin |
| Vitar EKO Hořčík Aquamin Mg | form | https://www.vitar.cz/vitar-eko-horcik-aquamin-mg/ | https://www.nasevitaminy.cz/vitar-eko-horcik-aquamin-mg |
| Vitar EKO Vitamin D3 1000 IU | form | https://www.vitar.cz/vitar-eko-vitamin-d3/ | https://www.nasevitaminy.cz/vitar-eko-vitamin-d3-1000-iu |
| Vitar EKO Hlíva ústřičná | form | https://www.vitar.cz/vitar-eko-hliva-ustricna/ | https://www.nasevitaminy.cz/vitar-eko-hliva-ustricna |
| Vitar EKO Probiotika forte | form | https://www.vitar.cz/vitar-eko-probiotika-forte/ | https://www.nasevitaminy.cz/vitar-eko-probiotika-forte |
| Vitar EKO Vitamin C 500 mg | form | https://www.vitar.cz/vitar-eko-vitamin-c-500-mg/ | https://www.nasevitaminy.cz/vitar-eko-vitamin-c-500-mg |
| Vitar EKO Kolagen forte | form | https://www.vitar.cz/vitar-eko-kolagen-forte/ | https://www.nasevitaminy.cz/vitar-eko-kolagen-forte |
| Vitar EKO B-komplex forte | form | https://www.vitar.cz/vitar-eko-b-komplex-forte/ | https://www.nasevitaminy.cz/vitar-eko-b-komplex-forte |
| Vitar EKO Betakaroten | form | https://www.vitar.cz/vitar-eko-betakaroten/ | https://www.nasevitaminy.cz/vitar-eko-betakaroten |
| Vitar EKO Detox silná dávka | form | https://www.vitar.cz/vitar-eko-detox-silna-davka/ | https://www.nasevitaminy.cz/vitar-eko-detox-silna-davka |

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
