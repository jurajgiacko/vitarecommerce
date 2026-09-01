import { asc, eq, ne } from "drizzle-orm";
import { NextResponse } from "next/server";

import { db, schema } from "@/lib/db";
import { hasAppAccess } from "@/lib/session";

const ROUND_ID = "round-vitar-split-2026-09";

const CHANNEL_LABELS: Record<string, string> = {
  "vitar.cz": "VITAR.cz",
  "nasevitaminy.cz": "NašeVitamíny.cz",
  vitar_veterina: "VITAR Veterina",
  oem_b2b: "OEM / B2B",
  workshop_hold: "Společně rozhodnout",
  archive: "Starý produkt / archiv",
};

const LIFECYCLE_LABELS: Record<string, string> = {
  active: "Aktivní",
  phaseout: "Doprodej / dožití",
  discontinue: "Ukončit výrobu",
  archive: "Starý produkt / archiv",
};

function csvCell(value: unknown) {
  const output = Array.isArray(value) ? value.join(" | ") : String(value ?? "");
  return `"${output.replaceAll('"', '""')}"`;
}

function markdownCell(value: unknown) {
  return String(value ?? "")
    .replaceAll("\\", "\\\\")
    .replaceAll("|", "\\|")
    .replaceAll("\r", " ")
    .replaceAll("\n", " ")
    .trim();
}

function markdownLink(label: string, url: string) {
  if (!url) return "";
  return `[${markdownCell(label)}](${url.replaceAll(" ", "%20").replaceAll(")", "%29")})`;
}

function channelSummary(channels: string[]) {
  return channels
    .map((item) => {
      const [channel, decision, role] = item.split(":");
      const label = CHANNEL_LABELS[channel] || channel;
      return [label, decision, role].filter(Boolean).join(" · ");
    })
    .join("; ");
}

export async function GET(request: Request) {
  if (!(await hasAppAccess())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const url = new URL(request.url);
  const requestedFormat = url.searchParams.get("format");
  const format = requestedFormat === "csv" || requestedFormat === "md" ? requestedFormat : "json";
  const scope = url.searchParams.get("scope") === "all" ? "all" : "final";
  const [products, sources, profiles, reviews, reviewChannels, comments, decisions, decisionChannels] =
    await Promise.all([
      db
        .select()
        .from(schema.products)
        .where(ne(schema.products.lifecycle, "out_of_scope"))
        .orderBy(asc(schema.products.brand), asc(schema.products.name)),
      db.select().from(schema.productSources),
      db.select().from(schema.profiles),
      db.select().from(schema.productReviews).where(eq(schema.productReviews.roundId, ROUND_ID)),
      db.select().from(schema.reviewChannels),
      db.select().from(schema.comments).where(eq(schema.comments.roundId, ROUND_ID)),
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
  const commentsByProduct = new Map<string, typeof comments>();
  for (const comment of comments) {
    const existing = commentsByProduct.get(comment.productId) || [];
    existing.push(comment);
    commentsByProduct.set(comment.productId, existing);
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
    const productComments = commentsByProduct.get(product.id) || [];
    return {
      product_id: product.id,
      sku: product.sku,
      ean: product.ean,
      name: product.name,
      brand: product.brand,
      source_category: product.categoryLabel,
      lifecycle: product.lifecycle,
      is_placeholder: product.manuallyCreated,
      placeholder_channels: product.manuallyCreated ? product.systemRecommendation.channels : [],
      placeholder_created_by: product.createdByProfileId
        ? profileMap.get(product.createdByProfileId) || product.createdByProfileId
        : "",
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
      comments:
        scope === "all"
          ? productComments.map((comment) => ({
              profile: profileMap.get(comment.profileId) || comment.profileId,
              body: comment.body,
              created_at: comment.createdAt.toISOString(),
            }))
          : undefined,
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
  const finalColumns = [
    "product_id",
    "sku",
    "ean",
    "name",
    "brand",
    "source_category",
    "lifecycle",
    "is_placeholder",
    "placeholder_channels",
    "placeholder_created_by",
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

  if (format === "md") {
    const generatedAt = new Date().toISOString();
    const approvedCount = rows.filter((row) => row.final_status !== "unresolved").length;
    const title = scope === "all" ? "VITAR Assortment - všechny názory" : "VITAR Assortment - finální rozhodnutí";
    const lines = [
      `# ${title}`,
      "",
      `- Vygenerováno: ${generatedAt}`,
      `- Kolo: ${ROUND_ID}`,
      `- Produktů: ${rows.length}`,
      `- Finálně rozhodnuto: ${approvedCount}`,
      `- Neuzavřeno: ${rows.length - approvedCount}`,
      "",
      "## Produktová matice",
      "",
      "| Produkt | Brand | SKU | EAN | Zdroje | Placeholder cíl | Finální stav | Životní cyklus | Cílové kanály | Kategorie | Role | Review | Důvod |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
      ...rows.map((row) => {
        const sourceLinks = [
          markdownLink("VITAR.cz", row.vitar_url),
          markdownLink("NašeVitamíny.cz", row.nasevitaminy_url),
          markdownLink("České vitamíny", row.ceskevitaminy_url),
        ].filter(Boolean).join(", ");
        const cells = [
          row.name,
          row.brand,
          row.sku,
          row.ean,
          sourceLinks,
          channelSummary(row.placeholder_channels.map((channel) => `${channel}:include`)),
          row.final_status,
          LIFECYCLE_LABELS[row.final_lifecycle] || row.final_lifecycle,
          channelSummary(row.final_channels),
          row.final_category,
          row.final_portfolio_role,
          `${row.submitted_review_count}/${row.review_count}`,
          row.final_rationale,
        ];
        return `| ${cells.map(markdownCell).join(" | ")} |`;
      }),
    ];

    if (scope === "all") {
      lines.push(
        "",
        "## Individuální názory",
        "",
        "| Produkt | Reviewer | Stav | Životní cyklus | Kanály | Kategorie | Role | Odůvodnění |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
      );
      for (const row of rows) {
        for (const review of row.reviews || []) {
          const reviewChannels = review.channels
            .map((channel) => `${CHANNEL_LABELS[channel.channel] || channel.channel} · ${channel.decision} · ${channel.role}`)
            .join("; ");
          const cells = [
            row.name,
            review.profile,
            review.status,
            LIFECYCLE_LABELS[review.lifecycle] || review.lifecycle,
            reviewChannels,
            review.category,
            review.portfolio_role,
            review.rationale,
          ];
          lines.push(`| ${cells.map(markdownCell).join(" | ")} |`);
        }
      }

      const commentCount = rows.reduce((sum, row) => sum + (row.comments?.length || 0), 0);
      if (commentCount > 0) {
        lines.push(
          "",
          "## Poznámky",
          "",
          "| Produkt | Autor | Datum | Poznámka |",
          "| --- | --- | --- | --- |",
        );
        for (const row of rows) {
          for (const comment of row.comments || []) {
            lines.push(`| ${[row.name, comment.profile, comment.created_at, comment.body].map(markdownCell).join(" | ")} |`);
          }
        }
      }
    }

    return new NextResponse(`${lines.join("\n")}\n`, {
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Content-Disposition": `attachment; filename="vitar-assortment-${scope}.md"`,
      },
    });
  }

  if (scope === "all") {
    const reviewColumns = [
      ...finalColumns,
      "review_profile",
      "review_status",
      "review_channels",
      "review_category",
      "review_portfolio_role",
      "review_lifecycle",
      "review_rationale",
      "product_comments",
    ] as const;
    const csvRows = rows.flatMap((row) => {
      const reviewRows = row.reviews?.length ? row.reviews : [null];
      return reviewRows.map((review) => ({
        ...row,
        review_profile: review?.profile || "",
        review_status: review?.status || "",
        review_channels: review?.channels.map((channel) => `${channel.channel}:${channel.decision}:${channel.role}`) || [],
        review_category: review?.category || "",
        review_portfolio_role: review?.portfolio_role || "",
        review_lifecycle: review?.lifecycle || "",
        review_rationale: review?.rationale || "",
        product_comments: row.comments?.map((comment) => `${comment.profile}: ${comment.body}`) || [],
      }));
    });
    const csv = [
      reviewColumns.map(csvCell).join(","),
      ...csvRows.map((row) => reviewColumns.map((column) => csvCell(row[column])).join(",")),
    ].join("\r\n");
    return new NextResponse(`\uFEFF${csv}`, {
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": `attachment; filename="vitar-assortment-${scope}.csv"`,
      },
    });
  }

  const csv = [
    finalColumns.map(csvCell).join(","),
    ...rows.map((row) => finalColumns.map((column) => csvCell(row[column])).join(",")),
  ].join("\r\n");
  return new NextResponse(`\uFEFF${csv}`, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="vitar-assortment-${scope}.csv"`,
    },
  });
}
