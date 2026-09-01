export const INFORMATION_REASONS = [
  "Prodeje nebo marže",
  "Sklad a dostupnost",
  "Produktová data nebo složení",
  "EAN nebo SKU",
  "Rozhodnutí produktového týmu",
  "Jiný podklad",
] as const;

export function informationRationale(reason: string) {
  return `Potřebuji doplnit: ${reason}.`;
}
