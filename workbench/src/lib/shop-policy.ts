import type { WorkbenchProduct } from "@/lib/workbench-types";

export type ShopPlanKey = "vitar" | "nase" | "outside";

const VITAR_ONLY_BRANDS = new Set([
  "Vitar",
  "Vitar Kids",
  "Vitar Kings",
  "Vitar Origin",
  "VITAR UNITY",
  "VITAR NEO",
]);

const OFFLINE_BRANDS = new Set(["Capri-Sun", "Predator"]);

export function fallbackShopTargets(product: Pick<WorkbenchProduct, "brand">): ShopPlanKey[] {
  if (product.brand === "Vitar Veterinae") return ["outside"];
  if (OFFLINE_BRANDS.has(product.brand)) return ["outside"];
  if (product.brand === "Maxi Vita Essentials") return ["vitar", "nase"];
  if (VITAR_ONLY_BRANDS.has(product.brand)) return ["vitar"];
  return ["nase"];
}

export function shopTargets(product: WorkbenchProduct): ShopPlanKey[] {
  const included = product.finalDecision?.channels
    .filter((channel) => channel.decision === "include")
    .map((channel) => channel.channel) || [];
  const targets = new Set<ShopPlanKey>();
  if (included.includes("vitar.cz")) targets.add("vitar");
  if (included.includes("nasevitaminy.cz")) targets.add("nase");
  if (included.some((channel) => ["vitar_veterina", "offline_retail", "oem_b2b"].includes(channel))) {
    targets.add("outside");
  }
  return targets.size ? [...targets] : fallbackShopTargets(product);
}

export function assignmentLabel(product: WorkbenchProduct) {
  const targets = shopTargets(product);
  if (targets.includes("vitar") && targets.includes("nase")) return "Oba e-shopy";
  if (targets.includes("vitar")) return "Jen VITAR.cz";
  if (targets.includes("nase")) return "Jen NašeVitamíny.cz";
  if (product.brand === "Vitar Veterinae") return "Samostatná Veterina";
  return "Mimo e-shopy / retail";
}

export function assignmentReason(product: WorkbenchProduct) {
  if (product.finalDecision?.rationale) return product.finalDecision.rationale;
  if (product.brand === "Maxi Vita Essentials") return "Jediná značka schválená pro oba e-shopy.";
  if (VITAR_ONLY_BRANDS.has(product.brand)) return "Současná nebo nová produktová řada značky VITAR.";
  if (product.brand === "Vitar Veterinae") return "Samostatná značka a samostatný e-shop.";
  if (OFFLINE_BRANDS.has(product.brand)) return "Bez zařazení do obou e-shopů; podpora retailu a marketplace.";
  return "Ostatní produktové portfolio patří na NašeVitamíny.cz.";
}

