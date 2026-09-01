import { asc, desc, eq } from "drizzle-orm";

import { db, schema } from "@/lib/db";
import type {
  ChannelDecision,
  Comment,
  FinalDecision,
  Profile,
  Review,
  WorkbenchData,
  WorkbenchProduct,
} from "@/lib/workbench-types";

const ROUND_ID = "round-vitar-split-2026-09";

export async function getProfiles(): Promise<Profile[]> {
  return db
    .select({
      id: schema.profiles.id,
      name: schema.profiles.name,
      email: schema.profiles.email,
      initials: schema.profiles.initials,
      role: schema.profiles.role,
      color: schema.profiles.color,
      lastActiveAt: schema.profiles.lastActiveAt,
    })
    .from(schema.profiles)
    .where(eq(schema.profiles.active, true))
    .orderBy(asc(schema.profiles.createdAt))
    .then((rows) => rows.map((row) => ({
      ...row,
      lastActiveAt: row.lastActiveAt?.toISOString() || null,
    })));
}

export async function getWorkbenchData(profileId: string): Promise<WorkbenchData | null> {
  const [profileRows, roundRows, productRows, sourceRows, reviewRows, channelRows, commentRows, finalRows, finalChannelRows, crawlRows] =
    await Promise.all([
      getProfiles(),
      db.select().from(schema.reviewRounds).where(eq(schema.reviewRounds.id, ROUND_ID)).limit(1),
      db.select().from(schema.products).orderBy(asc(schema.products.brand), asc(schema.products.name)),
      db.select().from(schema.productSources).orderBy(asc(schema.productSources.sourceKey)),
      db.select().from(schema.productReviews).where(eq(schema.productReviews.roundId, ROUND_ID)),
      db.select().from(schema.reviewChannels),
      db.select().from(schema.comments).where(eq(schema.comments.roundId, ROUND_ID)).orderBy(asc(schema.comments.createdAt)),
      db.select().from(schema.finalDecisions).where(eq(schema.finalDecisions.roundId, ROUND_ID)),
      db.select().from(schema.finalDecisionChannels),
      db.select().from(schema.crawlRuns).orderBy(desc(schema.crawlRuns.completedAt)).limit(1),
    ]);

  const profile = profileRows.find((item) => item.id === profileId);
  const round = roundRows[0];
  if (!profile || !round) return null;

  const profileById = new Map(profileRows.map((item) => [item.id, item]));
  const channelsByReview = new Map<string, ChannelDecision[]>();
  for (const channel of channelRows) {
    const existing = channelsByReview.get(channel.reviewId) || [];
    existing.push({
      channel: channel.channel,
      decision: channel.decision,
      role: channel.role,
      priority: channel.priority,
    });
    channelsByReview.set(channel.reviewId, existing);
  }
  const reviewByProduct = new Map<string, Review[]>();
  for (const review of reviewRows) {
    const owner = profileById.get(review.profileId);
    if (!owner) continue;
    const item: Review = {
      id: review.id,
      profileId: review.profileId,
      profileName: owner.name,
      profileInitials: owner.initials,
      profileColor: owner.color,
      status: review.status,
      categoryKey: review.categoryKey,
      categoryLabel: review.categoryLabel,
      portfolioRole: review.portfolioRole,
      confidence: review.confidence,
      rationale: review.rationale,
      channels: channelsByReview.get(review.id) || [],
      updatedAt: review.updatedAt.toISOString(),
    };
    const existing = reviewByProduct.get(review.productId) || [];
    existing.push(item);
    reviewByProduct.set(review.productId, existing);
  }

  const commentsByProduct = new Map<string, Comment[]>();
  for (const comment of commentRows) {
    const owner = profileById.get(comment.profileId);
    if (!owner) continue;
    const item: Comment = {
      id: comment.id,
      profileId: comment.profileId,
      profileName: owner.name,
      profileInitials: owner.initials,
      profileColor: owner.color,
      body: comment.body,
      createdAt: comment.createdAt.toISOString(),
    };
    const existing = commentsByProduct.get(comment.productId) || [];
    existing.push(item);
    commentsByProduct.set(comment.productId, existing);
  }

  const sourcesByProduct = new Map<string, WorkbenchProduct["sources"]>();
  for (const source of sourceRows) {
    const existing = sourcesByProduct.get(source.productId) || [];
    existing.push({
      id: source.id,
      sourceKey: source.sourceKey,
      sourceSite: source.sourceSite,
      url: source.url,
      name: source.name,
      sku: source.sku,
      ean: source.ean,
      priceCzk: source.priceCzk,
      imageUrl: source.imageUrl,
      description: source.description,
      quality: source.quality,
    });
    sourcesByProduct.set(source.productId, existing);
  }

  const finalChannelsByDecision = new Map<string, ChannelDecision[]>();
  for (const channel of finalChannelRows) {
    const existing = finalChannelsByDecision.get(channel.decisionId) || [];
    existing.push({
      channel: channel.channel,
      decision: channel.decision,
      role: channel.role,
      priority: channel.priority,
    });
    finalChannelsByDecision.set(channel.decisionId, existing);
  }
  const finalByProduct = new Map<string, FinalDecision>();
  for (const decision of finalRows) {
    finalByProduct.set(decision.productId, {
      id: decision.id,
      categoryKey: decision.categoryKey,
      categoryLabel: decision.categoryLabel,
      portfolioRole: decision.portfolioRole,
      status: decision.status,
      rationale: decision.rationale,
      approvedByProfileId: decision.approvedByProfileId,
      channels: finalChannelsByDecision.get(decision.id) || [],
      updatedAt: decision.updatedAt.toISOString(),
    });
  }

  const products: WorkbenchProduct[] = productRows.map((product) => {
    const reviews = reviewByProduct.get(product.id) || [];
    const submitted = reviews.filter((review) => review.status === "submitted");
    const signatures = new Set(
      submitted.map((review) =>
        JSON.stringify({
          channels: review.channels.map((channel) => `${channel.channel}:${channel.decision}`).sort(),
          category: review.categoryKey,
          role: review.portfolioRole,
        }),
      ),
    );
    return {
      id: product.id,
      name: product.name,
      brand: product.brand,
      sku: product.sku,
      ean: product.ean,
      categoryKey: product.categoryKey,
      categoryLabel: product.categoryLabel,
      categoryConfidence: product.categoryConfidence,
      formKey: product.formKey,
      formLabel: product.formLabel,
      description: product.description,
      imageUrl: product.imageUrl,
      priceCzk: product.priceCzk,
      sourceCount: product.sourceCount,
      lifecycle: product.lifecycle,
      manuallyCreated: product.manuallyCreated,
      coverage: product.coverage,
      quality: product.quality,
      fieldConflicts: product.fieldConflicts as WorkbenchProduct["fieldConflicts"],
      systemRecommendation: product.systemRecommendation,
      sources: sourcesByProduct.get(product.id) || [],
      reviews,
      comments: commentsByProduct.get(product.id) || [],
      finalDecision: finalByProduct.get(product.id) || null,
      consensusConflict: signatures.size > 1,
    };
  });

  const crawl = crawlRows[0];
  return {
    profile,
    profiles: profileRows,
    round: {
      id: round.id,
      name: round.name,
      description: round.description,
      status: round.status,
      dueAt: round.dueAt?.toISOString() || null,
    },
    products,
    crawl: crawl
      ? {
          sitemapUrlCount: crawl.sitemapUrlCount,
          sourceProductCount: crawl.sourceProductCount,
          masterProductCount: crawl.masterProductCount,
          errorCount: crawl.errorCount,
          completedAt: crawl.completedAt.toISOString(),
          summary: crawl.summary,
        }
      : null,
  };
}
