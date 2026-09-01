import { AccessGate } from "@/components/access-gate";
import { ProfilePicker } from "@/components/profile-picker";
import { WorkbenchApp } from "@/components/workbench-app";
import { getActiveProfileId, hasAppAccess } from "@/lib/session";
import { getProfiles, getWorkbenchData } from "@/lib/workbench-data";

export const dynamic = "force-dynamic";

export default async function Home() {
  if (!(await hasAppAccess())) return <AccessGate />;
  const profiles = await getProfiles();
  const profileId = await getActiveProfileId();
  if (!profileId || !profiles.some((profile) => profile.id === profileId)) {
    return <ProfilePicker profiles={profiles} />;
  }
  const data = await getWorkbenchData(profileId);
  if (!data) return <ProfilePicker profiles={profiles} />;
  return <WorkbenchApp data={data} />;
}
