import { and, eq } from "drizzle-orm";
import { NextResponse } from "next/server";

import { db, schema } from "@/lib/db";
import { setActiveProfileId, setAppAccess, verifyInviteToken } from "@/lib/session";

export async function GET(
  request: Request,
  context: { params: Promise<{ token: string }> },
) {
  const { token } = await context.params;
  const invitation = verifyInviteToken(token);
  if (!invitation) return NextResponse.redirect(new URL("/?invite=invalid", request.url));
  const profile = await db
    .select({ id: schema.profiles.id })
    .from(schema.profiles)
    .where(and(eq(schema.profiles.id, invitation.profileId), eq(schema.profiles.active, true)))
    .limit(1);
  if (!profile[0]) return NextResponse.redirect(new URL("/?invite=inactive", request.url));
  await setAppAccess();
  await setActiveProfileId(profile[0].id);
  await db
    .update(schema.profiles)
    .set({ lastActiveAt: new Date(), updatedAt: new Date() })
    .where(eq(schema.profiles.id, profile[0].id));
  return NextResponse.redirect(new URL("/", request.url));
}
