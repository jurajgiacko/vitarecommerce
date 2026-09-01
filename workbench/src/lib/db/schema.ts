import {
  boolean,
  index,
  integer,
  jsonb,
  numeric,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uniqueIndex,
} from "drizzle-orm/pg-core";

export type ProductQuality = {
  hasSku: boolean;
  hasEan: boolean;
  hasImage: boolean;
  hasDescription: boolean;
  hasLongContent: boolean;
  hasPrice: boolean;
  hasConflict: boolean;
  hasVariation?: boolean;
};

export type SystemRecommendation = {
  channels: string[];
  primary?: string;
  confidence: "low" | "medium" | "high";
  reason: string;
};

export const profiles = pgTable("profiles", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().default(""),
  initials: text("initials").notNull(),
  role: text("role").notNull().default("reviewer"),
  color: text("color").notNull().default("#167A5A"),
  active: boolean("active").notNull().default(true),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  invitedAt: timestamp("invited_at", { withTimezone: true }),
  lastActiveAt: timestamp("last_active_at", { withTimezone: true }),
});

export const reviewRounds = pgTable("review_rounds", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull().default(""),
  status: text("status").notNull().default("open"),
  dueAt: timestamp("due_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  lockedAt: timestamp("locked_at", { withTimezone: true }),
});

export const products = pgTable(
  "products",
  {
    id: text("id").primaryKey(),
    name: text("name").notNull(),
    brand: text("brand").notNull().default("Neurčeno"),
    sku: text("sku").notNull().default(""),
    ean: text("ean").notNull().default(""),
    categoryKey: text("category_key").notNull().default("unclassified"),
    categoryLabel: text("category_label").notNull().default("Nezařazeno"),
    categoryConfidence: text("category_confidence").notNull().default("low"),
    formKey: text("form_key").notNull().default("unknown"),
    formLabel: text("form_label").notNull().default("Neurčeno"),
    description: text("description").notNull().default(""),
    imageUrl: text("image_url").notNull().default(""),
    priceCzk: numeric("price_czk", { precision: 12, scale: 2 }),
    sourceCount: integer("source_count").notNull().default(0),
    lifecycle: text("lifecycle").notNull().default("live"),
    manuallyCreated: boolean("manually_created").notNull().default(false),
    createdByProfileId: text("created_by_profile_id").references(() => profiles.id),
    coverage: jsonb("coverage").$type<Record<string, boolean>>().notNull().default({}),
    quality: jsonb("quality").$type<ProductQuality>().notNull(),
    fieldConflicts: jsonb("field_conflicts").$type<unknown[]>().notNull().default([]),
    systemRecommendation: jsonb("system_recommendation")
      .$type<SystemRecommendation>()
      .notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index("products_brand_idx").on(table.brand),
    index("products_category_idx").on(table.categoryKey),
    index("products_sku_idx").on(table.sku),
    index("products_lifecycle_idx").on(table.lifecycle),
  ],
);

export const productSources = pgTable(
  "product_sources",
  {
    id: text("id").primaryKey(),
    productId: text("product_id")
      .notNull()
      .references(() => products.id, { onDelete: "cascade" }),
    sourceKey: text("source_key").notNull(),
    sourceSite: text("source_site").notNull(),
    url: text("url").notNull(),
    name: text("name").notNull(),
    sku: text("sku").notNull().default(""),
    ean: text("ean").notNull().default(""),
    priceCzk: numeric("price_czk", { precision: 12, scale: 2 }),
    imageUrl: text("image_url").notNull().default(""),
    description: text("description").notNull().default(""),
    contentSections: jsonb("content_sections").$type<Record<string, string>>().notNull().default({}),
    quality: jsonb("quality").$type<Record<string, boolean>>().notNull().default({}),
    lastSeenAt: timestamp("last_seen_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index("product_sources_product_idx").on(table.productId),
    index("product_sources_source_idx").on(table.sourceKey),
    uniqueIndex("product_sources_url_unique").on(table.url),
  ],
);

export const productReviews = pgTable(
  "product_reviews",
  {
    id: text("id").primaryKey(),
    roundId: text("round_id")
      .notNull()
      .references(() => reviewRounds.id, { onDelete: "cascade" }),
    productId: text("product_id")
      .notNull()
      .references(() => products.id, { onDelete: "cascade" }),
    profileId: text("profile_id")
      .notNull()
      .references(() => profiles.id, { onDelete: "cascade" }),
    status: text("status").notNull().default("draft"),
    categoryKey: text("category_key").notNull().default(""),
    categoryLabel: text("category_label").notNull().default(""),
    portfolioRole: text("portfolio_role").notNull().default("core"),
    lifecycleDecision: text("lifecycle_decision").notNull().default("active"),
    confidence: text("confidence").notNull().default("medium"),
    rationale: text("rationale").notNull().default(""),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    uniqueIndex("product_reviews_round_product_profile_unique").on(
      table.roundId,
      table.productId,
      table.profileId,
    ),
    index("product_reviews_profile_idx").on(table.profileId),
    index("product_reviews_product_idx").on(table.productId),
  ],
);

export const reviewChannels = pgTable(
  "review_channels",
  {
    reviewId: text("review_id")
      .notNull()
      .references(() => productReviews.id, { onDelete: "cascade" }),
    channel: text("channel").notNull(),
    decision: text("decision").notNull().default("include"),
    role: text("role").notNull().default("secondary"),
    priority: integer("priority").notNull().default(2),
  },
  (table) => [primaryKey({ columns: [table.reviewId, table.channel] })],
);

export const comments = pgTable(
  "comments",
  {
    id: text("id").primaryKey(),
    productId: text("product_id")
      .notNull()
      .references(() => products.id, { onDelete: "cascade" }),
    roundId: text("round_id").references(() => reviewRounds.id, { onDelete: "cascade" }),
    profileId: text("profile_id")
      .notNull()
      .references(() => profiles.id, { onDelete: "cascade" }),
    body: text("body").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [index("comments_product_idx").on(table.productId)],
);

export const finalDecisions = pgTable(
  "final_decisions",
  {
    id: text("id").primaryKey(),
    roundId: text("round_id")
      .notNull()
      .references(() => reviewRounds.id, { onDelete: "cascade" }),
    productId: text("product_id")
      .notNull()
      .references(() => products.id, { onDelete: "cascade" }),
    categoryKey: text("category_key").notNull().default(""),
    categoryLabel: text("category_label").notNull().default(""),
    portfolioRole: text("portfolio_role").notNull().default("core"),
    lifecycleDecision: text("lifecycle_decision").notNull().default("active"),
    status: text("status").notNull().default("approved"),
    rationale: text("rationale").notNull().default(""),
    approvedByProfileId: text("approved_by_profile_id")
      .notNull()
      .references(() => profiles.id),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    uniqueIndex("final_decisions_round_product_unique").on(table.roundId, table.productId),
  ],
);

export const finalDecisionChannels = pgTable(
  "final_decision_channels",
  {
    decisionId: text("decision_id")
      .notNull()
      .references(() => finalDecisions.id, { onDelete: "cascade" }),
    channel: text("channel").notNull(),
    decision: text("decision").notNull().default("include"),
    role: text("role").notNull().default("secondary"),
    priority: integer("priority").notNull().default(2),
  },
  (table) => [primaryKey({ columns: [table.decisionId, table.channel] })],
);

export const auditEvents = pgTable(
  "audit_events",
  {
    id: text("id").primaryKey(),
    actorProfileId: text("actor_profile_id").references(() => profiles.id),
    productId: text("product_id").references(() => products.id, { onDelete: "cascade" }),
    roundId: text("round_id").references(() => reviewRounds.id, { onDelete: "cascade" }),
    action: text("action").notNull(),
    payload: jsonb("payload").$type<Record<string, unknown>>().notNull().default({}),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [index("audit_events_product_idx").on(table.productId)],
);

export const crawlRuns = pgTable("crawl_runs", {
  id: text("id").primaryKey(),
  startedAt: timestamp("started_at", { withTimezone: true }).notNull(),
  completedAt: timestamp("completed_at", { withTimezone: true }).notNull(),
  sitemapUrlCount: integer("sitemap_url_count").notNull(),
  sourceProductCount: integer("source_product_count").notNull(),
  masterProductCount: integer("master_product_count").notNull(),
  errorCount: integer("error_count").notNull(),
  summary: jsonb("summary").$type<Record<string, unknown>>().notNull(),
});
