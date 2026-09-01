import { config } from "dotenv";
import { writeFile } from "node:fs/promises";
import path from "node:path";

import { buildProductFamilyMap } from "../src/lib/product-family";

config({ path: ".env.local" });

type CatalogSource = {
  source_key: string;
  url: string;
};

type CatalogProduct = {
  id: string;
  name: string;
  brand: string;
  source_count: number;
  sources: CatalogSource[];
  category: { key: string; label: string };
  quality: Record<string, boolean>;
};

type Coverage = {
  sitemap_urls: number;
  inventory_urls: number;
  products: number;
  errors: number;
  reconciled: boolean;
};

type Check = {
  name: string;
  ok: boolean;
  detail: string;
};

async function main() {
  const [{ db, schema }, catalogModule] = await Promise.all([
    import("../src/lib/db/index"),
    import("../src/data/catalog.json"),
  ]);
  const catalog = catalogModule.default as {
    summary: {
      generated_at: string;
      source_products: number;
      master_products: number;
      coverage: Record<string, Coverage>;
    };
    products: CatalogProduct[];
  };
  const [products, sources, profiles, rounds, crawlRuns] = await Promise.all([
    db.select().from(schema.products),
    db.select().from(schema.productSources),
    db.select().from(schema.profiles),
    db.select().from(schema.reviewRounds),
    db.select().from(schema.crawlRuns),
  ]);

  const catalogProductIds = new Set(catalog.products.map((product) => product.id));
  const catalogSources = catalog.products.flatMap((product) => product.sources);
  const catalogSourceUrls = new Set(catalogSources.map((source) => source.url));
  const activeDatabaseProducts = products.filter(
    (product) => product.manuallyCreated || product.lifecycle !== "out_of_scope",
  );
  const activeDatabaseProductIds = new Set(activeDatabaseProducts.map((product) => product.id));
  const activeDatabaseSources = sources.filter((source) => activeDatabaseProductIds.has(source.productId));
  const databaseProductIds = new Set(activeDatabaseProducts.map((product) => product.id));
  const databaseSourceUrls = new Set(activeDatabaseSources.map((source) => source.url));
  const databaseSourcesByProduct = new Map<string, number>();
  for (const source of activeDatabaseSources) {
    databaseSourcesByProduct.set(source.productId, (databaseSourcesByProduct.get(source.productId) || 0) + 1);
  }

  const coverageRows = Object.entries(catalog.summary.coverage);
  const missingProducts = catalog.products.filter((product) => !databaseProductIds.has(product.id));
  const staleProducts = activeDatabaseProducts.filter(
    (product) => !product.manuallyCreated && !catalogProductIds.has(product.id),
  );
  const missingSources = catalogSources.filter((source) => !databaseSourceUrls.has(source.url));
  const staleSources = activeDatabaseSources.filter((source) => !catalogSourceUrls.has(source.url));
  const sourceCountMismatches = catalog.products.filter(
    (product) => (databaseSourcesByProduct.get(product.id) || 0) !== product.source_count,
  );
  const malformedWip = products.filter(
    (product) => product.manuallyCreated && (!product.name.trim() || !product.brand.trim() || !product.categoryKey.trim()),
  );
  const requiredProfiles = [
    "Juraj Giacko",
    "Tomáš Červinka",
    "Daniel Polášek",
    "Miloslav Matoušek",
    "Roman Majda",
  ];
  const activeProfileNames = new Set(profiles.filter((profile) => profile.active).map((profile) => profile.name));
  const latestCrawl = crawlRuns.sort((left, right) => right.completedAt.getTime() - left.completedAt.getTime())[0];
  const reviewRound = rounds.find((round) => round.id === "round-vitar-split-2026-09");
  const familyMap = buildProductFamilyMap(catalog.products);
  const familySizes = [...new Map([...familyMap.values()].map((family) => [family.key, family.size])).values()];
  const multiFamilySizes = familySizes.filter((size) => size > 1);
  const largestFamily = Math.max(1, ...familySizes);

  const checks: Check[] = [
    {
      name: "Sitemap reconciliation",
      ok: coverageRows.every(([, value]) => value.reconciled && value.sitemap_urls === value.inventory_urls),
      detail: coverageRows.map(([key, value]) => `${key} ${value.inventory_urls}/${value.sitemap_urls}`).join(", "),
    },
    {
      name: "Crawl errors",
      ok: coverageRows.every(([, value]) => value.errors === 0),
      detail: `${coverageRows.reduce((sum, [, value]) => sum + value.errors, 0)} errors`,
    },
    {
      name: "Master products in database",
      ok: missingProducts.length === 0 && staleProducts.length === 0,
      detail: `${catalog.products.length} current, ${missingProducts.length} missing, ${staleProducts.length} stale`,
    },
    {
      name: "Product source URLs in database",
      ok: missingSources.length === 0 && staleSources.length === 0,
      detail: `${catalogSources.length} current, ${missingSources.length} missing, ${staleSources.length} stale`,
    },
    {
      name: "Per-product source counts",
      ok: sourceCountMismatches.length === 0,
      detail: `${sourceCountMismatches.length} mismatches`,
    },
    {
      name: "Current crawl recorded",
      ok: Boolean(
        latestCrawl &&
          Math.abs(latestCrawl.completedAt.getTime() - new Date(catalog.summary.generated_at).getTime()) < 1000,
      ),
      detail: latestCrawl?.completedAt.toISOString() || "missing",
    },
    {
      name: "Required team profiles",
      ok: requiredProfiles.every((name) => activeProfileNames.has(name)),
      detail: `${requiredProfiles.filter((name) => activeProfileNames.has(name)).length}/${requiredProfiles.length} active`,
    },
    {
      name: "Review round open",
      ok: reviewRound?.status === "open",
      detail: reviewRound?.status || "missing",
    },
    {
      name: "WIP records valid",
      ok: malformedWip.length === 0,
      detail: `${products.filter((product) => product.manuallyCreated).length} WIP, ${malformedWip.length} malformed`,
    },
    {
      name: "Product family grouping",
      ok: familyMap.size === catalog.products.length && largestFamily <= 12,
      detail: `${multiFamilySizes.length} multi-variant families, ${multiFamilySizes.reduce((sum, size) => sum + size, 0)} products, largest ${largestFamily}`,
    },
  ];

  const report = {
    generated_at: new Date().toISOString(),
    catalog_generated_at: catalog.summary.generated_at,
    status: checks.every((check) => check.ok) ? "pass" : "fail",
    checks,
    metrics: {
      sitemap_urls: coverageRows.reduce((sum, [, value]) => sum + value.sitemap_urls, 0),
      source_products: catalog.summary.source_products,
      master_products: catalog.summary.master_products,
      database_products: activeDatabaseProducts.length,
      database_sources: activeDatabaseSources.length,
      out_of_scope_products: products.filter((product) => product.lifecycle === "out_of_scope").length,
      active_profiles: activeProfileNames.size,
      unclassified_products: catalog.products.filter((product) => product.category.key === "unclassified").length,
      products_without_sku: catalog.products.filter((product) => !product.quality.has_sku).length,
      products_without_ean: catalog.products.filter((product) => !product.quality.has_ean).length,
      products_without_image: catalog.products.filter((product) => !product.quality.has_image).length,
      products_without_description: catalog.products.filter((product) => !product.quality.has_description).length,
      products_without_long_content: catalog.products.filter((product) => !product.quality.has_long_content).length,
      products_without_price: catalog.products.filter((product) => !product.quality.has_price).length,
      products_with_source_conflicts: catalog.products.filter((product) => product.quality.has_conflict).length,
      multi_variant_families: multiFamilySizes.length,
      products_in_multi_variant_families: multiFamilySizes.reduce((sum, size) => sum + size, 0),
      largest_product_family: largestFamily,
    },
    failures: {
      missing_product_ids: missingProducts.map((product) => product.id),
      stale_product_ids: staleProducts.map((product) => product.id),
      missing_source_urls: missingSources.map((source) => source.url),
      stale_source_urls: staleSources.map((source) => source.url),
      source_count_product_ids: sourceCountMismatches.map((product) => product.id),
    },
  };

  const outputPath = path.join(process.cwd(), "data/current/release-audit.json");
  await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== "pass") process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
