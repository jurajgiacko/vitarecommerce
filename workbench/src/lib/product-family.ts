type FamilyCandidate = {
  id: string;
  name: string;
  brand: string;
};

export type ProductFamily = {
  key: string;
  name: string;
  size: number;
};

const FLAVOR_SUFFIXES = [
  "ananas",
  "broskev",
  "cerny rybiz",
  "citron",
  "grep",
  "jahoda",
  "jahoda a malina",
  "malina",
  "mango",
  "mango + maracuja",
  "maracuja",
  "pomeranc",
  "tropicke ovoce",
  "tresen",
  "visen",
  "visen + granatove jablko",
];

function fold(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("cs")
    .replace(/[®™]/g, "")
    .replace(/[–—]/g, "-");
}

function familyBase(product: FamilyCandidate) {
  const brand = fold(product.brand).trim();
  let value = fold(product.name).trim();
  if (value === brand) return value;
  if (value.startsWith(`${brand} `)) value = value.slice(brand.length + 1);

  value = value
    .replace(/\(?\b\d+\s*\+\s*\d+\s*kapsli\s*zdarma\b\)?/g, " ")
    .replace(/\b\d+\s*[x×]\s*\d+\b/g, " ")
    .replace(/\/\s*\d+(?:[.,]\d+)?\s*(?:mg|g|kg|ml|l)\b/g, " ")
    .replace(/\b\d+(?:[.,]\d+)?\s*(?:mg|g|kg|ml|l|iu|tbl\.?|tablet(?:y|a)?|kapsl(?:i|e)?|stick(?:u|y)?|ks)\b/g, " ")
    .replace(/\b(?:duopack|xxl|vyhodne baleni)\b/g, " ")
    .replace(/[()]/g, " ");

  const escapedFlavors = FLAVOR_SUFFIXES
    .sort((left, right) => right.length - left.length)
    .map((flavor) => flavor.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");
  value = value.replace(new RegExp(`\\s*-\\s*(?:${escapedFlavors})\\s*$`), " ");

  return value
    .replace(/\s+/g, " ")
    .replace(/^[\s+\-/]+|[\s+\-/]+$/g, "")
    .trim();
}

export function buildProductFamilyMap(products: FamilyCandidate[]) {
  const groups = new Map<string, FamilyCandidate[]>();
  for (const product of products) {
    const key = `${fold(product.brand).trim()}::${familyBase(product) || fold(product.name).trim()}`;
    const members = groups.get(key) || [];
    members.push(product);
    groups.set(key, members);
  }

  const result = new Map<string, ProductFamily>();
  for (const [key, members] of groups) {
    const name = [...members].sort(
      (left, right) => left.name.length - right.name.length || left.name.localeCompare(right.name, "cs"),
    )[0].name;
    for (const member of members) result.set(member.id, { key, name, size: members.length });
  }
  return result;
}
