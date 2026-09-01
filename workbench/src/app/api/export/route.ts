import { asc, eq } from "drizzle-orm";
import { NextResponse } from "next/server";

import { db, schema } from "@/lib/db";
import { hasAppAccess } from "@/lib/session";

const ROUND_ID = "round-vitar-split-2026-09";

function csvCell(value: unknown) {
  const output = Array.isArray(value) ? value.join(" | ") : String(value ?? "");
  return `"${output.replaceAll('"', '""')}"`;
}

export async function GET(request: Request) {
  if (!(await hasAppAccess())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const url = new URL(request.url);
  const format = url.searchParams.get("format") === "csv" ? "csv" : "json";
  const scope = url.searchParams.get("scope") || "final";
  const [products, sources, profiles, reviews, reviewChannels, decisions, decisionChannels] =
    await Promise.all([
      db.select().from(schema.products).orderBy(asc(schema.products.brand), asc(schema.products.name)),
      db.select().from(schema.productSources),
      db.select().from(schema.profiles),
      db.select().from(schema.productReviews).where(eq(schema.productReviews.roundId, ROUND_ID)),
      db.select().from(schema.reviewChannels),
      db.select().from(schema.finalDecisions).where(eq(schema.finalDecisions.roundId, ROUND_ID)),
      db.select().from(schema.finalDecisionChannels),
    ]);
  const sourceMap = new Map<string, typeof sources>();
  for (const source of sources) {
    const existing = sourceMap.get(source.productId) || [];
    existing.push(source);
    sourceMap.set(source.productId, existing);
  }
  const profileMap = new Map(profiles.map((profile) => [profile.id, profile.name]));
  const channelByReview = new Map<string, typeof reviewChannels>();
  for (const channel of reviewChannels) {
    const existing = channelByReview.get(channel.reviewId) || [];
    existing.push(channel);
    channelByReview.set(channel.reviewId, existing);
  }
  const reviewsByProduct = new Map<string, typeof reviews>();
  for (const review of reviews) {
    const existing = reviewsByProduct.get(review.productId) || [];
    existing.push(review);
    reviewsByProduct.set(review.productId, existing);
  }
  const finalChannelMap = new Map<string, typeof decisionChannels>();
  for (const channel of decisionChannels) {
    const existing = finalChannelMap.get(channel.decisionId) || [];
    existing.push(channel);
    finalChannelMap.set(channel.decisionId, existing);
  }
  const finalMap = new Map(decisions.map((decision) => [decision.productId, decision]));

  const rows = products.map((product) => {
    const final = finalMap.get(product.id);
    const productReviews = reviewsByProduct.get(product.id) || [];
    const productSources = sourceMap.get(product.id) || [];
    return {
      product_id: product.id,
      sku: product.sku,
      ean: product.ean,
      name: product.name,
      brand: product.brand,
      source_category: product.categoryLabel,
      lifecycle: product.lifecycle,
      source_sites: productSources.map((source) => source.sourceSite),
      source_urls: productSources.map((source) => source.url),
      vitar_url: productSources.find((source) => source.sourceKey === "vitar")?.url || "",
      nasevitaminy_url: productSources.find((source) => source.sourceKey === "nasevitaminy")?.url || "",
      ceskevitaminy_url: productSources.find((source) => source.sourceKey === "ceskevitaminy")?.url || "",
      final_status: final?.status || "unresolved",
      final_channels: final
        ? (finalChannelMap.get(final.id) || []).map(
            (channel) => `${channel.channel}:${channel.decision}:${channel.role}`,
          )
        : [],
      final_category: final?.categoryLabel || "",
      final_portfolio_role: final?.portfolioRole || "",
      final_lifecycle: final?.lifecycleDecision || "",
      final_rationale: final?.rationale || "",
      approved_by: final ? profileMap.get(final.approvedByProfileId) || "" : "",
      review_count: productReviews.length,
      submitted_review_count: productReviews.filter((review) => review.status === "submitted").length,
      reviews:
        scope === "all"
          ? productReviews.map((review) => ({
              profile: profileMap.get(review.profileId) || review.profileId,
              status: review.status,
              channels: (channelByReview.get(review.id) || []).map((channel) => ({
                channel: channel.channel,
                decision: channel.decision,
                role: channel.role,
              })),
              category: review.categoryLabel,
              portfolio_role: review.portfolioRole,
              lifecycle: review.lifecycleDecision,
              rationale: review.rationale,
            }))
          : undefined,
    };
  });

  if (format === "json") {
    return NextResponse.json(
      { generated_at: new Date().toISOString(), round_id: ROUND_ID, scope, products: rows },
      { headers: { "Content-Disposition": `attachment; filename="vitar-assortment-${scope}.json"` } },
    );
  }
  const columns = [
    "product_id",
    "sku",
    "ean",
    "name",
    "brand",
    "source_category",
    "lifecycle",
    "source_sites",
    "source_urls",
    "vitar_url",
    "nasevitaminy_url",
    "ceskevitaminy_url",
    "final_status",
    "final_channels",
    "final_category",
    "final_portfolio_role",
    "final_lifecycle",
    "final_rationale",
    "approved_by",
    "review_count",
    "submitted_review_count",
  ] as const;
  const csv = [
    columns.map(csvCell).join(","),
    ...rows.map((row) => columns.map((column) => csvCell(row[column])).join(",")),
  ].join("\r\n");
  return new NextResponse(`\uFEFF${csv}`, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="vitar-assortment-${scope}.csv"`,
    },
  });
}
