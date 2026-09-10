"use client";

/* eslint-disable @next/next/no-img-element */

import { useMemo, useState } from "react";
import { ChevronRight, ExternalLink, PackageOpen, Search, Store } from "lucide-react";

import { assignmentLabel, assignmentReason, shopTargets, type ShopPlanKey } from "@/lib/shop-policy";
import type { WorkbenchProduct } from "@/lib/workbench-types";

const SHOP_TABS: Array<{ key: ShopPlanKey; label: string; description: string }> = [
  { key: "vitar", label: "VITAR.cz", description: "VITAR, VITAR NEO, VITAR UNITY a Maxi Vita Essentials" },
  { key: "nase", label: "NašeVitamíny.cz", description: "Ostatní produktové portfolio a Maxi Vita Essentials" },
  { key: "outside", label: "Mimo e-shopy", description: "Capri-Sun, Predator a samostatná VITAR Veterina" },
];

function waveLabel(product: WorkbenchProduct) {
  return product.systemRecommendation.reason.match(/Wave\s*[123]/i)?.[0] || "";
}

export function ShopPlanner({ products, onOpenProduct }: { products: WorkbenchProduct[]; onOpenProduct: (id: string) => void }) {
  const [shop, setShop] = useState<ShopPlanKey>("vitar");
  const [search, setSearch] = useState("");
  const [brand, setBrand] = useState("all");
  const [category, setCategory] = useState("all");
  const [kind, setKind] = useState("all");

  const shopProducts = useMemo(() => products.filter((product) => shopTargets(product).includes(shop)), [products, shop]);
  const brands = useMemo(() => {
    const counts = new Map<string, number>();
    shopProducts.forEach((product) => counts.set(product.brand, (counts.get(product.brand) || 0) + 1));
    return [...counts.entries()].sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0], "cs"));
  }, [shopProducts]);
  const categories = useMemo(() => {
    const counts = new Map<string, number>();
    shopProducts.forEach((product) => counts.set(product.categoryLabel, (counts.get(product.categoryLabel) || 0) + 1));
    return [...counts.entries()].sort((left, right) => left[0].localeCompare(right[0], "cs"));
  }, [shopProducts]);
  const filtered = useMemo(() => {
    const needle = search.trim().toLocaleLowerCase("cs");
    return shopProducts.filter((product) => {
      if (brand !== "all" && product.brand !== brand) return false;
      if (category !== "all" && product.categoryLabel !== category) return false;
      if (kind === "current" && product.manuallyCreated) return false;
      if (kind === "wip" && !product.manuallyCreated) return false;
      return !needle || `${product.name} ${product.brand} ${product.sku} ${product.ean}`.toLocaleLowerCase("cs").includes(needle);
    });
  }, [brand, category, kind, search, shopProducts]);
  const groups = useMemo(() => {
    const grouped = new Map<string, WorkbenchProduct[]>();
    filtered.forEach((product) => {
      const items = grouped.get(product.categoryLabel) || [];
      items.push(product);
      grouped.set(product.categoryLabel, items);
    });
    return [...grouped.entries()].sort((left, right) => left[0].localeCompare(right[0], "cs"));
  }, [filtered]);
  const activeTab = SHOP_TABS.find((tab) => tab.key === shop) || SHOP_TABS[0];
  const currentCount = shopProducts.filter((product) => !product.manuallyCreated).length;
  const wipCount = shopProducts.filter((product) => product.manuallyCreated).length;

  function changeShop(next: ShopPlanKey) {
    setShop(next);
    setBrand("all");
    setCategory("all");
    setKind("all");
    setSearch("");
  }

  return (
    <section className="shop-plan-page">
      <header className="shop-plan-heading">
        <div>
          <p className="eyebrow">SCHVÁLENÉ ROZDĚLENÍ · 3. 9. 2026</p>
          <h1>Portfolio pro jednotlivé e-shopy</h1>
          <p>Finální kanál vychází z rozhodnutí vedení. Kategorie navazují na týmový návrh a zdrojová data.</p>
        </div>
        <a className="secondary-button" href="https://jurajgiacko.github.io/vitarecommerce/html/vitar-category-planner.html" target="_blank" rel="noreferrer">
          <ExternalLink size={15} /> Otevřít GitHub Pages
        </a>
      </header>

      <div className="shop-segments" role="tablist" aria-label="Cílové portfolio">
        {SHOP_TABS.map((tab) => {
          const count = products.filter((product) => shopTargets(product).includes(tab.key)).length;
          return <button className={shop === tab.key ? "active" : ""} onClick={() => changeShop(tab.key)} role="tab" aria-selected={shop === tab.key} key={tab.key}><span>{tab.label}</span><strong>{count}</strong></button>;
        })}
      </div>

      <section className="shop-rule-band">
        <Store size={19} />
        <div><strong>{activeTab.label}</strong><p>{activeTab.description}</p></div>
        <span><b>{currentCount}</b> současných</span>
        <span><b>{wipCount}</b> WIP</span>
      </section>

      <section className="shop-brand-nav">
        <header><strong>Značky</strong><small>První úroveň navigace</small></header>
        <div>
          <button className={brand === "all" ? "active" : ""} onClick={() => setBrand("all")}><span>Všechny</span><b>{shopProducts.length}</b></button>
          {brands.map(([label, count]) => <button className={brand === label ? "active" : ""} onClick={() => setBrand(label)} key={label}><span>{label}</span><b>{count}</b></button>)}
        </div>
      </section>

      <div className="shop-toolbar">
        <label className="shop-search"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Hledat produkt, SKU nebo EAN" /></label>
        <select aria-label="Filtrovat kategorii plánu" value={category} onChange={(event) => setCategory(event.target.value)}><option value="all">Všechny kategorie</option>{categories.map(([label, count]) => <option value={label} key={label}>{label} ({count})</option>)}</select>
        <select aria-label="Filtrovat typ produktu" value={kind} onChange={(event) => setKind(event.target.value)}><option value="all">Současné + WIP</option><option value="current">Jen současné</option><option value="wip">Jen WIP placeholdery</option></select>
      </div>

      <div className="shop-result-line"><strong>{filtered.length}</strong> produktů v zobrazení <span /> {groups.length} kategorií</div>
      {groups.length ? groups.map(([label, items]) => (
        <section className="shop-category-group" key={label}>
          <header><div><p className="eyebrow">KATEGORIE</p><h2>{label}</h2></div><strong>{items.length}</strong></header>
          <div className="shop-product-grid">
            {items.map((product) => (
              <article className="shop-product-card" key={product.id}>
                <button className="shop-product-main" onClick={() => onOpenProduct(product.id)}>
                  <span className="shop-product-image">{product.imageUrl ? <img src={product.imageUrl} alt="" /> : <PackageOpen size={24} />}</span>
                  <span className="shop-product-copy">
                    <small>{product.brand}</small>
                    <strong>{product.name}</strong>
                    <em>{product.formLabel}{product.sku ? ` · SKU ${product.sku}` : ""}</em>
                  </span>
                  <ChevronRight size={17} />
                </button>
                <footer>
                  <span className={`shop-status ${product.manuallyCreated ? "wip" : "current"}`}>{product.manuallyCreated ? "WIP placeholder" : "Současný produkt"}</span>
                  {waveLabel(product) ? <span className="shop-status wave">{waveLabel(product)}</span> : null}
                  <span className="shop-assignment" title={assignmentReason(product)}>{assignmentLabel(product)}</span>
                </footer>
              </article>
            ))}
          </div>
        </section>
      )) : <div className="shop-empty"><PackageOpen size={28} /><h2>Žádné produkty</h2><p>Změňte značku, kategorii nebo hledaný výraz.</p></div>}
    </section>
  );
}
