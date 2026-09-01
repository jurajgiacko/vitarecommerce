import { asc, eq } from "drizzle-orm";
import { NextResponse } from "next/server";

import { db, schema } from "@/lib/db";
import { hasAppAccess } from "@/lib/session";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  if (!(await hasAppAccess())) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  const { id } = await context.params;
  const [sources, auditRows, profileRows] = await Promise.all([
    db
      .select()
      .from(schema.productSources)
      .where(eq(schema.productSources.productId, id))
      .orderBy(asc(schema.productSources.sourceKey)),
    db
      .select()
      .from(schema.auditEvents)
      .where(eq(schema.auditEvents.productId, id))
      .orderBy(asc(schema.auditEvents.createdAt)),
    db
      .select({ id: schema.profiles.id, name: schema.profiles.name })
      .from(schema.profiles),
  ]);
  const profileMap = new Map(profileRows.map((profile) => [profile.id, profile.name]));
  return NextResponse.json({
    productId: id,
    sources: sources.map((source) => ({
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
      contentSections: source.contentSections,
    })),
    audit: auditRows.map((event) => ({
      id: event.id,
      action: event.action,
      actorName: event.actorProfileId
        ? profileMap.get(event.actorProfileId) || "Neznámý profil"
        : "Systém",
      createdAt: event.createdAt.toISOString(),
      payload: event.payload,
    })),
  });
}
