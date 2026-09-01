import { config } from "dotenv";
import { and, eq, notInArray, sql } from "drizzle-orm";
import { readFile } from "node:fs/promises";
import path from "node:path";

config({ path: ".env.local" });

type SourceRecord = {
  source_id: string;
  source_key: string;
  source_site: string;
  url: string;
  name: string;
  sku: string;
  ean: string;
  price_czk: number | null;
  image: string;
  description: string;
  content_sections: Record<string, string>;
  quality: Record<string, boolean>;
};

type CatalogProduct = {
  id: string;
  name: string;
  brand: string;
  sku: string;
  ean: string;
  category: { key: string; label: string; confidence: string };
  form: { key: string; label: string };
  description: string;
  image: string;
  price_czk: number | null;
  source_count: number;
  sources: SourceRecord[];
  field_conflicts: unknown[];
  coverage: Record<string, boolean>;
  quality: {
    has_sku: boolean;
    has_ean: boolean;
    has_image: boolean;
    has_description: boolean;
    has_long_content: boolean;
    has_price: boolean;
    has_conflict: boolean;
    has_variation?: boolean;
  };
  system_recommendation: {
    channels: string[];
    primary?: string;
    confidence: "low" | "medium" | "high";
    reason: string;
  };
  lifecycle: string;
};

async function main() {
  const [{ db }, schema, catalogRaw] = await Promise.all([
    import("../src/lib/db/index"),
    import("../src/lib/db/schema"),
    readFile(path.join(process.cwd(), "src/data/catalog.json"), "utf8"),
  ]);
  const catalog = JSON.parse(catalogRaw) as {
    summary: Record<string, unknown> & {
      crawl_started_at: string;
      generated_at: string;
      source_products: number;
      master_products: number;
      coverage: Record<string, { sitemap_urls: number; errors: number }>;
    };
    products: CatalogProduct[];
  };

  const profileRows = [
    { id: "profile-juraj", name: "Juraj Giacko", initials: "JG", role: "facilitator", color: "#167A5A" },
    { id: "profile-tomas", name: "Tomáš Červinka", initials: "TČ", role: "reviewer", color: "#2D63B8" },
    { id: "profile-daniel", name: "Daniel Polášek", initials: "DP", role: "reviewer", color: "#B55B2A" },
    { id: "profile-miloslav", name: "Miloslav Matoušek", initials: "MM", role: "reviewer", color: "#7B4DA8" },
    { id: "profile-roman", name: "Roman Majda", initials: "RM", role: "reviewer", color: "#397887" },
  ];
  await db.insert(schema.profiles).values(profileRows).onConflictDoNothing();
  await db
    .insert(schema.reviewRounds)
    .values({
      id: "round-vitar-split-2026-09",
      name: "VITAR.cz assortment split",
      description: "Rozdělení portfolia mezi VITAR.cz, NašeVitamíny.cz a samostatné business units.",
      status: "open",
      dueAt: new Date("2026-09-03T08:00:00+02:00"),
    })
    .onConflictDoUpdate({
      target: schema.reviewRounds.id,
      set: { status: "open", dueAt: new Date("2026-09-03T08:00:00+02:00") },
    });

  const chunkSize = 75;
  for (let index = 0; index < catalog.products.length; index += chunkSize) {
    const chunk = catalog.products.slice(index, index + chunkSize);
    await db
      .insert(schema.products)
      .values(
        chunk.map((product) => ({
          id: product.id,
          name: product.name.replace(/<[^>]+>/g, ""),
          brand: product.brand,
          sku: product.sku,
          ean: product.ean,
          categoryKey: product.category.key,
          categoryLabel: product.category.label,
          categoryConfidence: product.category.confidence,
          formKey: product.form.key,
          formLabel: product.form.label,
          description: product.description,
          imageUrl: product.image,
          priceCzk: product.price_czk === null ? null : String(product.price_czk),
          sourceCount: product.source_count,
          lifecycle: product.lifecycle,
          coverage: product.coverage,
          quality: {
            hasSku: product.quality.has_sku,
            hasEan: product.quality.has_ean,
            hasImage: product.quality.has_image,
            hasDescription: product.quality.has_description,
            hasLongContent: product.quality.has_long_content,
            hasPrice: product.quality.has_price,
            hasConflict: product.quality.has_conflict,
            hasVariation: product.quality.has_variation,
          },
          fieldConflicts: product.field_conflicts,
          systemRecommendation: product.system_recommendation,
          updatedAt: new Date(),
        })),
      )
      .onConflictDoUpdate({
        target: schema.products.id,
        set: {
          name: sql`excluded.name`,
          brand: sql`excluded.brand`,
          sku: sql`excluded.sku`,
          ean: sql`excluded.ean`,
          categoryKey: sql`excluded.category_key`,
          categoryLabel: sql`excluded.category_label`,
          categoryConfidence: sql`excluded.category_confidence`,
          formKey: sql`excluded.form_key`,
          formLabel: sql`excluded.form_label`,
          description: sql`excluded.description`,
          imageUrl: sql`excluded.image_url`,
          priceCzk: sql`excluded.price_czk`,
          sourceCount: sql`excluded.source_count`,
          lifecycle: sql`excluded.lifecycle`,
          coverage: sql`excluded.coverage`,
          quality: sql`excluded.quality`,
          fieldConflicts: sql`excluded.field_conflicts`,
          systemRecommendation: sql`excluded.system_recommendation`,
          updatedAt: sql`excluded.updated_at`,
        },
      });
  }
  const currentProductIds = catalog.products.map((product) => product.id);
  if (currentProductIds.length) {
    await db
      .update(schema.products)
      .set({ lifecycle: "out_of_scope", updatedAt: new Date() })
      .where(
        and(
          eq(schema.products.manuallyCreated, false),
          notInArray(schema.products.id, currentProductIds),
        ),
      );
  }

  const sources = catalog.products.flatMap((product) =>
    product.sources.map((source) => ({
      id: source.source_id,
      productId: product.id,
      sourceKey: source.source_key,
      sourceSite: source.source_site,
      url: source.url,
      name: source.name.replace(/<[^>]+>/g, ""),
      sku: source.sku,
      ean: source.ean,
      priceCzk: source.price_czk === null ? null : String(source.price_czk),
      imageUrl: source.image,
      description: source.description,
      contentSections: source.content_sections,
      quality: source.quality,
      lastSeenAt: new Date(catalog.summary.generated_at),
    })),
  );
  for (let index = 0; index < sources.length; index += chunkSize) {
    await db
      .insert(schema.productSources)
      .values(sources.slice(index, index + chunkSize))
      .onConflictDoUpdate({
        target: schema.productSources.url,
        set: {
          productId: sql`excluded.product_id`,
          sourceKey: sql`excluded.source_key`,
          sourceSite: sql`excluded.source_site`,
          name: sql`excluded.name`,
          sku: sql`excluded.sku`,
          ean: sql`excluded.ean`,
          priceCzk: sql`excluded.price_czk`,
          imageUrl: sql`excluded.image_url`,
          description: sql`excluded.description`,
          contentSections: sql`excluded.content_sections`,
          quality: sql`excluded.quality`,
          lastSeenAt: sql`excluded.last_seen_at`,
        },
      });
  }

  const sitemapUrlCount = Object.values(catalog.summary.coverage).reduce(
    (total, source) => total + source.sitemap_urls,
    0,
  );
  const errorCount = Object.values(catalog.summary.coverage).reduce(
    (total, source) => total + source.errors,
    0,
  );
  await db
    .insert(schema.crawlRuns)
    .values({
      id: `crawl-${catalog.summary.generated_at.slice(0, 10)}`,
      startedAt: new Date(catalog.summary.crawl_started_at),
      completedAt: new Date(catalog.summary.generated_at),
      sitemapUrlCount,
      sourceProductCount: catalog.summary.source_products,
      masterProductCount: catalog.summary.master_products,
      errorCount,
      summary: catalog.summary,
    })
    .onConflictDoUpdate({
      target: schema.crawlRuns.id,
      set: {
        startedAt: new Date(catalog.summary.crawl_started_at),
        completedAt: new Date(catalog.summary.generated_at),
        sitemapUrlCount,
        sourceProductCount: catalog.summary.source_products,
        masterProductCount: catalog.summary.master_products,
        errorCount,
        summary: catalog.summary,
      },
    });

  const outOfScopeRows = await db
    .select({ id: schema.products.id })
    .from(schema.products)
    .where(eq(schema.products.lifecycle, "out_of_scope"));

  console.log(
    JSON.stringify(
      {
        profiles: profileRows.length,
        products: catalog.products.length,
        sources: sources.length,
        outOfScopeProducts: outOfScopeRows.length,
        round: "round-vitar-split-2026-09",
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
