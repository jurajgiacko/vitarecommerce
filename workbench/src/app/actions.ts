"use server";

import { createHash, randomUUID } from "node:crypto";

import { and, eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";
import { headers } from "next/headers";
import { z } from "zod";

import { db, schema } from "@/lib/db";
import {
  getActiveProfileId,
  createInviteToken,
  setActiveProfileId,
  setAppAccess,
} from "@/lib/session";

const ROUND_ID = "round-vitar-split-2026-09";

const channelSchema = z.object({
  channel: z.string().min(1),
  decision: z.enum(["include", "exclude", "hold"]).default("include"),
  role: z.enum(["primary", "secondary"]).default("secondary"),
  priority: z.number().int().min(1).max(3).default(2),
});

const reviewSchema = z.object({
  productId: z.string().min(1),
  profileId: z.string().min(1),
  categoryKey: z.string().min(1),
  categoryLabel: z.string().min(1),
  portfolioRole: z.enum(["hero", "core", "support", "longtail", "test", "exclude", "hold"]),
  lifecycleDecision: z.enum(["active", "phaseout", "discontinue", "archive"]).default("active"),
  confidence: z.enum(["low", "medium", "high"]),
  rationale: z.string().max(4000),
  status: z.enum(["draft", "submitted"]),
  channels: z.array(channelSchema).min(1),
});

async function assertProfile(profileId: string) {
  const activeProfileId = await getActiveProfileId();
  if (!activeProfileId || activeProfileId !== profileId) {
    throw new Error("Aktivní profil neodpovídá autorovi změny.");
  }
}

async function assertCanManageTeam() {
  const actorProfileId = await getActiveProfileId();
  const actor = await db
    .select({ role: schema.profiles.role })
    .from(schema.profiles)
    .where(eq(schema.profiles.id, actorProfileId))
    .limit(1);
  if (!actor[0] || !["facilitator", "admin"].includes(actor[0].role)) {
    throw new Error("Tento profil nemá oprávnění spravovat tým.");
  }
}

async function inviteUrlForProfile(profileId: string) {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") || requestHeaders.get("host") || "localhost:3000";
  const protocol = requestHeaders.get("x-forwarded-proto") || (host.includes("localhost") ? "http" : "https");
  return `${protocol}://${host}/join/${createInviteToken(profileId)}`;
}

export async function unlockApp(code: string) {
  const expected = process.env.APP_ACCESS_CODE;
  if (expected && code !== expected) return { ok: false, error: "Nesprávný přístupový kód." };
  await setAppAccess();
  revalidatePath("/");
  return { ok: true };
}

export async function chooseProfile(profileId: string) {
  const rows = await db
    .select({ id: schema.profiles.id })
    .from(schema.profiles)
    .where(and(eq(schema.profiles.id, profileId), eq(schema.profiles.active, true)))
    .limit(1);
  if (!rows[0]) throw new Error("Profil neexistuje.");
  await setActiveProfileId(profileId);
  revalidatePath("/");
}

export async function createProfile(input: { name: string; role?: string }) {
  const parsed = z
    .object({ name: z.string().trim().min(2).max(80), role: z.string().default("reviewer") })
    .parse(input);
  const initials = parsed.name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
  const id = `profile-${createHash("sha1").update(`${parsed.name}:${Date.now()}`).digest("hex").slice(0, 10)}`;
  const colors = ["#167A5A", "#2D63B8", "#B55B2A", "#7B4DA8", "#9B3E53"];
  await db.insert(schema.profiles).values({
    id,
    name: parsed.name,
    initials,
    role: parsed.role,
    color: colors[Math.floor(Math.random() * colors.length)],
  });
  await setActiveProfileId(id);
  revalidatePath("/");
  return { id };
}

export async function createProfileInvite(profileId: string) {
  await assertCanManageTeam();
  const parsedProfileId = z.string().min(1).parse(profileId);
  const profile = await db
    .select({ id: schema.profiles.id })
    .from(schema.profiles)
    .where(and(eq(schema.profiles.id, parsedProfileId), eq(schema.profiles.active, true)))
    .limit(1);
  if (!profile[0]) throw new Error("Profil neexistuje nebo není aktivní.");
  await db
    .update(schema.profiles)
    .set({ invitedAt: new Date(), updatedAt: new Date() })
    .where(eq(schema.profiles.id, parsedProfileId));
  return { ok: true, profileId: parsedProfileId, inviteUrl: await inviteUrlForProfile(parsedProfileId) };
}

export async function createInviteProfile(input: { name: string; email?: string }) {
  await assertCanManageTeam();
  const parsed = z
    .object({
      name: z.string().trim().min(2).max(80),
      email: z.union([z.string().trim().email().max(160), z.literal("")]).default(""),
    })
    .parse(input);
  const email = parsed.email.toLowerCase();
  const existingByEmail = email
    ? await db
        .select({ id: schema.profiles.id, email: schema.profiles.email })
        .from(schema.profiles)
        .where(eq(schema.profiles.email, email))
        .limit(1)
    : [];
  const existingByName = existingByEmail[0]
    ? []
    : await db
        .select({ id: schema.profiles.id, email: schema.profiles.email })
        .from(schema.profiles)
        .where(eq(schema.profiles.name, parsed.name))
        .limit(1);
  const matchedProfile = existingByEmail[0] || existingByName[0];
  const profileId =
    matchedProfile?.id ||
    `profile-${createHash("sha1").update(`${parsed.name}:${email}:${Date.now()}`).digest("hex").slice(0, 10)}`;
  if (!matchedProfile) {
    const initials = parsed.name
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join("");
    const colors = ["#167A5A", "#2D63B8", "#B55B2A", "#7B4DA8", "#9B3E53", "#397887"];
    await db.insert(schema.profiles).values({
      id: profileId,
      name: parsed.name,
      email,
      initials,
      role: "reviewer",
      color: colors[Math.floor(Math.random() * colors.length)],
      invitedAt: new Date(),
    });
  } else {
    await db
      .update(schema.profiles)
      .set({
        ...(email && !matchedProfile.email ? { email } : {}),
        invitedAt: new Date(),
        active: true,
        updatedAt: new Date(),
      })
      .where(eq(schema.profiles.id, profileId));
  }
  revalidatePath("/");
  return { ok: true, profileId, inviteUrl: await inviteUrlForProfile(profileId) };
}

export async function saveReview(input: z.input<typeof reviewSchema>) {
  const parsed = reviewSchema.parse(input);
  await assertProfile(parsed.profileId);
  const reviewId = `review-${createHash("sha1")
    .update(`${ROUND_ID}:${parsed.productId}:${parsed.profileId}`)
    .digest("hex")
    .slice(0, 16)}`;
  await db
    .insert(schema.productReviews)
    .values({
      id: reviewId,
      roundId: ROUND_ID,
      productId: parsed.productId,
      profileId: parsed.profileId,
      status: parsed.status,
      categoryKey: parsed.categoryKey,
      categoryLabel: parsed.categoryLabel,
      portfolioRole: parsed.portfolioRole,
      lifecycleDecision: parsed.lifecycleDecision,
      confidence: parsed.confidence,
      rationale: parsed.rationale,
      updatedAt: new Date(),
    })
    .onConflictDoUpdate({
      target: [
        schema.productReviews.roundId,
        schema.productReviews.productId,
        schema.productReviews.profileId,
      ],
      set: {
        status: parsed.status,
        categoryKey: parsed.categoryKey,
        categoryLabel: parsed.categoryLabel,
        portfolioRole: parsed.portfolioRole,
        lifecycleDecision: parsed.lifecycleDecision,
        confidence: parsed.confidence,
        rationale: parsed.rationale,
        updatedAt: new Date(),
      },
    });
  await db.delete(schema.reviewChannels).where(eq(schema.reviewChannels.reviewId, reviewId));
  await db.insert(schema.reviewChannels).values(
    parsed.channels.map((channel) => ({ reviewId, ...channel })),
  );
  await db.insert(schema.auditEvents).values({
    id: randomUUID(),
    actorProfileId: parsed.profileId,
    productId: parsed.productId,
    roundId: ROUND_ID,
    action: parsed.status === "submitted" ? "review_submitted" : "review_saved",
    payload: {
      channels: parsed.channels,
      category: parsed.categoryKey,
      portfolioRole: parsed.portfolioRole,
      lifecycleDecision: parsed.lifecycleDecision,
    },
  });
  revalidatePath("/");
  return { ok: true, reviewId };
}

export async function bulkSaveReviews(input: {
  productIds: string[];
  profileId: string;
  channel: string;
  decision: "include" | "exclude" | "hold";
  reason?: string;
  status: "draft" | "submitted";
}) {
  const parsed = z
    .object({
      productIds: z.array(z.string()).min(1).max(350),
      profileId: z.string(),
      channel: z.string(),
      decision: z.enum(["include", "exclude", "hold"]),
      reason: z.string().trim().max(160).optional(),
      status: z.enum(["draft", "submitted"]),
    })
    .parse(input);
  await assertProfile(parsed.profileId);
  const productRows = await db
    .select({ id: schema.products.id, categoryKey: schema.products.categoryKey, categoryLabel: schema.products.categoryLabel })
    .from(schema.products);
  const productMap = new Map(productRows.map((product) => [product.id, product]));
  const channels = parsed.decision === "hold"
    ? [{ channel: "workshop_hold", decision: "hold" as const, role: "primary" as const, priority: 1 }]
    : parsed.channel === "both"
      ? [
          { channel: "vitar.cz", decision: parsed.decision, role: "primary" as const, priority: 1 },
          { channel: "nasevitaminy.cz", decision: parsed.decision, role: "secondary" as const, priority: 2 },
        ]
      : [{ channel: parsed.channel, decision: parsed.decision, role: "primary" as const, priority: 1 }];
  for (const productId of parsed.productIds) {
    const product = productMap.get(productId);
    if (!product) continue;
    await saveReview({
      productId,
      profileId: parsed.profileId,
      categoryKey: product.categoryKey,
      categoryLabel: product.categoryLabel,
      portfolioRole: parsed.decision === "exclude" ? "exclude" : parsed.decision === "hold" ? "hold" : "core",
      lifecycleDecision: parsed.decision === "exclude" ? "archive" : "active",
      confidence: parsed.decision === "hold" ? "low" : "medium",
      rationale: parsed.decision === "hold"
        ? `Potřebuji doplnit: ${parsed.reason || "Jiný podklad"}.`
        : "Hromadné rozhodnutí z portfolio přehledu.",
      status: parsed.status,
      channels,
    });
  }
  revalidatePath("/");
  return { ok: true, count: parsed.productIds.length };
}

export async function addComment(input: { productId: string; profileId: string; body: string }) {
  const parsed = z
    .object({ productId: z.string(), profileId: z.string(), body: z.string().trim().min(1).max(4000) })
    .parse(input);
  await assertProfile(parsed.profileId);
  await db.insert(schema.comments).values({
    id: randomUUID(),
    productId: parsed.productId,
    profileId: parsed.profileId,
    roundId: ROUND_ID,
    body: parsed.body,
  });
  await db.insert(schema.auditEvents).values({
    id: randomUUID(),
    actorProfileId: parsed.profileId,
    productId: parsed.productId,
    roundId: ROUND_ID,
    action: "comment_added",
    payload: {},
  });
  revalidatePath("/");
  return { ok: true };
}

export async function createWipProduct(input: {
  profileId: string;
  name: string;
  brand: string;
  categoryKey: string;
  categoryLabel: string;
  description: string;
  targetChannels: Array<"vitar.cz" | "nasevitaminy.cz">;
}) {
  const parsed = z
    .object({
      profileId: z.string(),
      name: z.string().trim().min(3).max(160),
      brand: z.string().trim().min(2).max(100),
      categoryKey: z.string(),
      categoryLabel: z.string(),
      description: z.string().max(4000),
      targetChannels: z.array(z.enum(["vitar.cz", "nasevitaminy.cz"])).min(1).max(2),
    })
    .parse(input);
  await assertProfile(parsed.profileId);
  const id = `wip_${randomUUID()}`;
  await db.insert(schema.products).values({
    id,
    name: parsed.name,
    brand: parsed.brand,
    categoryKey: parsed.categoryKey,
    categoryLabel: parsed.categoryLabel,
    categoryConfidence: "manual",
    description: parsed.description,
    lifecycle: "wip",
    manuallyCreated: true,
    createdByProfileId: parsed.profileId,
    coverage: {},
    quality: {
      hasSku: false,
      hasEan: false,
      hasImage: false,
      hasDescription: parsed.description.length >= 40,
      hasLongContent: false,
      hasPrice: false,
      hasConflict: false,
    },
    systemRecommendation: {
      channels: parsed.targetChannels,
      primary: parsed.targetChannels[0],
      confidence: "low",
      reason: `WIP placeholder připravený pro ${parsed.targetChannels.join(" + ")}; vyžaduje společné rozhodnutí.`,
    },
  });
  await db.insert(schema.auditEvents).values({
    id: randomUUID(),
    actorProfileId: parsed.profileId,
    productId: id,
    roundId: ROUND_ID,
    action: "wip_product_created",
    payload: {
      name: parsed.name,
      categoryKey: parsed.categoryKey,
      targetChannels: parsed.targetChannels,
    },
  });
  revalidatePath("/");
  return { ok: true, id };
}

export async function saveFinalDecision(input: z.input<typeof reviewSchema>) {
  const parsed = reviewSchema.parse(input);
  await assertProfile(parsed.profileId);
  const profileRows = await db
    .select({ role: schema.profiles.role })
    .from(schema.profiles)
    .where(eq(schema.profiles.id, parsed.profileId))
    .limit(1);
  if (!profileRows[0] || !["facilitator", "admin"].includes(profileRows[0].role)) {
    throw new Error("Tento profil nemá oprávnění uložit finální rozhodnutí.");
  }
  const decisionId = `final-${createHash("sha1")
    .update(`${ROUND_ID}:${parsed.productId}`)
    .digest("hex")
    .slice(0, 16)}`;
  await db
    .insert(schema.finalDecisions)
    .values({
      id: decisionId,
      roundId: ROUND_ID,
      productId: parsed.productId,
      categoryKey: parsed.categoryKey,
      categoryLabel: parsed.categoryLabel,
      portfolioRole: parsed.portfolioRole,
      lifecycleDecision: parsed.lifecycleDecision,
      rationale: parsed.rationale,
      approvedByProfileId: parsed.profileId,
      updatedAt: new Date(),
    })
    .onConflictDoUpdate({
      target: [schema.finalDecisions.roundId, schema.finalDecisions.productId],
      set: {
        categoryKey: parsed.categoryKey,
        categoryLabel: parsed.categoryLabel,
        portfolioRole: parsed.portfolioRole,
        lifecycleDecision: parsed.lifecycleDecision,
        rationale: parsed.rationale,
        approvedByProfileId: parsed.profileId,
        updatedAt: new Date(),
      },
    });
  await db
    .delete(schema.finalDecisionChannels)
    .where(eq(schema.finalDecisionChannels.decisionId, decisionId));
  await db.insert(schema.finalDecisionChannels).values(
    parsed.channels.map((channel) => ({ decisionId, ...channel })),
  );
  await db.insert(schema.auditEvents).values({
    id: randomUUID(),
    actorProfileId: parsed.profileId,
    productId: parsed.productId,
    roundId: ROUND_ID,
    action: "final_decision_saved",
    payload: { channels: parsed.channels, lifecycleDecision: parsed.lifecycleDecision },
  });
  revalidatePath("/");
  return { ok: true };
}
