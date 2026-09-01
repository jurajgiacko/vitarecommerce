type FieldConflict = { field?: string; values?: string[]; severity?: string };

export function conflictFieldLabel(field?: string) {
  if (field === "name") return "Název";
  if (field === "ean") return "EAN";
  if (field === "sku") return "SKU";
  return field || "Údaj";
}

export function highConflictSummary(conflicts: FieldConflict[]) {
  return conflicts
    .filter((conflict) => conflict.severity === "high")
    .map((conflict) => `${conflictFieldLabel(conflict.field)}: různé hodnoty`)
    .join(" · ");
}

export function highConflictDetails(conflicts: FieldConflict[]) {
  return conflicts
    .filter((conflict) => conflict.severity === "high")
    .map((conflict) => `${conflictFieldLabel(conflict.field)}: ${conflict.values?.join(" / ") || "hodnoty se liší"}`)
    .join(" · ");
}
