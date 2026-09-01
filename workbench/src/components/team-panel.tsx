"use client";

import { FormEvent, useMemo, useState, useTransition } from "react";
import { Check, Copy, Link2, Mail, Plus, UsersRound } from "lucide-react";
import { useRouter } from "next/navigation";

import { createInviteProfile, createProfileInvite } from "@/app/actions";
import type { Profile, WorkbenchProduct } from "@/lib/workbench-types";

type TeamPanelProps = {
  profiles: Profile[];
  products: WorkbenchProduct[];
  currentProfile: Profile;
};

export function TeamPanel({ profiles, products, currentProfile }: TeamPanelProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [inviteUrl, setInviteUrl] = useState("");
  const [inviteName, setInviteName] = useState("");
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");
  const [pending, startTransition] = useTransition();
  const router = useRouter();
  const canManage = ["facilitator", "admin"].includes(currentProfile.role);
  const progress = useMemo(
    () =>
      new Map(
        profiles.map((profile) => [
          profile.id,
          products.filter((product) =>
            product.reviews.some((review) => review.profileId === profile.id && review.status === "submitted"),
          ).length,
        ]),
      ),
    [products, profiles],
  );

  function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setInviteUrl("");
    startTransition(async () => {
      try {
        const result = await createInviteProfile({ name, email });
        setInviteUrl(result.inviteUrl);
        setInviteName(name.trim());
        setCopied(false);
        setName("");
        setEmail("");
        router.refresh();
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Pozvánku se nepodařilo vytvořit.");
      }
    });
  }

  async function copyInvite() {
    await navigator.clipboard.writeText(inviteUrl);
    setCopied(true);
  }

  function createLink(profile: Profile) {
    setError("");
    setInviteUrl("");
    startTransition(async () => {
      try {
        const result = await createProfileInvite(profile.id);
        setInviteUrl(result.inviteUrl);
        setInviteName(profile.name);
        setCopied(false);
        router.refresh();
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Pozvánku se nepodařilo vytvořit.");
      }
    });
  }

  return (
    <section className="team-page">
      <header className="page-heading">
        <div>
          <p className="eyebrow">PROFILY A PŘÍSTUPY</p>
          <h1>Týmový domácí úkol</h1>
          <p>Každý pozvaný člověk dostane vlastní přístup a jeho rozhodnutí zůstanou oddělená.</p>
        </div>
        <div className="heading-stat"><UsersRound size={19} /><strong>{profiles.length}</strong><span>aktivní profily</span></div>
      </header>

      <div className={`team-progress-table ${canManage ? "can-manage" : ""}`}>
        <div className="team-row team-row-head">
          <span>Profil</span><span>Kontakt</span><span>Stav</span><span>Odevzdáno</span>{canManage ? <span>Pozvánka</span> : null}
        </div>
        {profiles.map((profile) => {
          const done = progress.get(profile.id) || 0;
          const percent = Math.round((done / products.length) * 100);
          return (
            <div className="team-row" key={profile.id}>
              <span className="team-person"><i className="avatar small" style={{ backgroundColor: profile.color }}>{profile.initials}</i><span><strong>{profile.name}</strong></span></span>
              <span>{profile.email || "E-mail není nutný"}</span>
              <span className={`session-state ${profile.lastActiveAt ? "active" : "waiting"}`}>{profile.lastActiveAt ? "Přístup aktivní" : "Čeká na otevření"}</span>
              <span className="team-progress"><span><i style={{ width: `${percent}%` }} /></span><strong>{done}/{products.length}</strong></span>
              {canManage ? <button className="secondary-button compact invite-link-button" disabled={pending} onClick={() => createLink(profile)}><Link2 size={14} /> Vytvořit odkaz</button> : null}
            </div>
          );
        })}
      </div>

      {canManage ? (
        <section className="invite-section">
          <header><div><Mail size={18} /><span><strong>Přidat dalšího člověka</strong><small>Osobní odkaz platí 14 dní a přihlásí správný profil automaticky.</small></span></div></header>
          <form className="invite-form" onSubmit={submit}>
            <label><span>Jméno</span><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Např. Tomáš Červinka" /></label>
            <label><span>E-mail (volitelný)</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="jmeno@vitar.cz" /></label>
            <button className="primary-button" disabled={pending || name.trim().length < 2}><Plus size={16} /> {pending ? "Vytvářím..." : "Přidat a vytvořit odkaz"}</button>
          </form>
          {error ? <p className="form-error">{error}</p> : null}
          {inviteUrl ? (
            <div className="invite-result">
              <Link2 size={17} />
              <span><strong>Osobní odkaz pro {inviteName}</strong><input readOnly value={inviteUrl} onFocus={(event) => event.currentTarget.select()} /></span>
              <button className="secondary-button" onClick={copyInvite}>{copied ? <Check size={16} /> : <Copy size={16} />}{copied ? "Zkopírováno" : "Kopírovat"}</button>
            </div>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}
