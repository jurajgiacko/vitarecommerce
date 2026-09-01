import { createHmac, timingSafeEqual } from "node:crypto";

import { cookies } from "next/headers";

const ACCESS_COOKIE = "vitar_workbench_access";
const PROFILE_COOKIE = "vitar_workbench_profile";

function secret() {
  return process.env.SESSION_SECRET || "local-vitar-workbench-secret";
}

function sign(value: string) {
  return createHmac("sha256", secret()).update(value).digest("hex");
}

function safeEqual(left: string, right: string) {
  if (left.length !== right.length) return false;
  return timingSafeEqual(Buffer.from(left), Buffer.from(right));
}

export function accessToken() {
  const code = process.env.APP_ACCESS_CODE || "";
  return sign(`access:${code}`);
}

export async function hasAppAccess() {
  if (!process.env.APP_ACCESS_CODE) return true;
  const cookieStore = await cookies();
  const actual = cookieStore.get(ACCESS_COOKIE)?.value || "";
  const expected = accessToken();
  return safeEqual(actual, expected);
}

export async function setAppAccess() {
  const cookieStore = await cookies();
  cookieStore.set(ACCESS_COOKIE, accessToken(), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 30,
    path: "/",
  });
}

export async function getActiveProfileId() {
  const cookieStore = await cookies();
  const value = cookieStore.get(PROFILE_COOKIE)?.value || "";
  const [encoded, signature] = value.split(".");
  if (!encoded || !signature) return "";
  let profileId = "";
  try {
    profileId = Buffer.from(encoded, "base64url").toString("utf8");
  } catch {
    return "";
  }
  return safeEqual(signature, sign(`profile:${profileId}`)) ? profileId : "";
}

export async function setActiveProfileId(profileId: string) {
  const cookieStore = await cookies();
  const encoded = Buffer.from(profileId).toString("base64url");
  cookieStore.set(PROFILE_COOKIE, `${encoded}.${sign(`profile:${profileId}`)}`, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 120,
    path: "/",
  });
}

export function createInviteToken(profileId: string, validDays = 14) {
  const expiresAt = Date.now() + validDays * 24 * 60 * 60 * 1000;
  const payload = Buffer.from(JSON.stringify({ profileId, expiresAt })).toString("base64url");
  return `${payload}.${sign(`invite:${payload}`)}`;
}

export function verifyInviteToken(token: string) {
  const [payload, signature] = token.split(".");
  if (!payload || !signature || !safeEqual(signature, sign(`invite:${payload}`))) return null;
  try {
    const parsed = JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as {
      profileId: string;
      expiresAt: number;
    };
    if (!parsed.profileId || parsed.expiresAt < Date.now()) return null;
    return parsed;
  } catch {
    return null;
  }
}
