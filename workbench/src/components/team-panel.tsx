"use client";

import { FormEvent, useMemo, useState, useTransition } from "react";
import { Check, Copy, Link2, Mail, Plus, UsersRound } from "lucide-react";
import { useRouter } from "next/navigation";

import { createInviteProfile } from "@/app/actions";
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
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");
  const [pending, startTransition] = useTransition();
  const router = useRouter();
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
        setCopied(false);
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

  return (
    <section className="team-page">
      <header className="page-heading">
        <div>
          <p className="eyebrow">PROFILY A SESSION</p>
          <h1>Týmový domácí úkol</h1>
          <p>Každý pozvaný člověk dostane vlastní session a jeho rozhodnutí zůstanou oddělená.</p>
        </div>
        <div className="heading-stat"><UsersRound size={19} /><strong>{profiles.length}</strong><span>aktivní profily</span></div>
      </header>

      <div className="team-progress-table">
        <div className="team-row team-row-head">
          <span>Profil</span><span>Kontakt</span><span>Stav</span><span>Odevzdáno</span>
        </div>
        {profiles.map((profile) => {
          const done = progress.get(profile.id) || 0;
          const percent = Math.round((done / products.length) * 100);
          return (
            <div className="team-row" key={profile.id}>
              <span className="team-person"><i className="avatar small" style={{ backgroundColor: profile.color }}>{profile.initials}</i><span><strong>{profile.name}</strong><small>{profile.role === "facilitator" ? "Facilitátor" : "Reviewer"}</small></span></span>
              <span>{profile.email || "E-mail čeká"}</span>
              <span className={`session-state ${profile.lastActiveAt ? "active" : "waiting"}`}>{profile.lastActiveAt ? "Session aktivní" : "Čeká na otevření"}</span>
              <span className="team-progress"><span><i style={{ width: `${percent}%` }} /></span><strong>{done}/{products.length}</strong></span>
            </div>
          );
        })}
      </div>

      {currentProfile.role === "facilitator" ? (
        <section className="invite-section">
          <header><div><Mail size={18} /><span><strong>Vytvořit osobní pozvánku</strong><small>Link platí 14 dní a přihlásí správný profil automaticky.</small></span></div></header>
          <form className="invite-form" onSubmit={submit}>
            <label><span>Jméno</span><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Např. Tomáš Červinka" /></label>
            <label><span>E-mail</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="jmeno@vitar.cz" /></label>
            <button className="primary-button" disabled={pending || name.trim().length < 2 || !email.includes("@")}><Plus size={16} /> {pending ? "Vytvářím..." : "Vytvořit pozvánku"}</button>
          </form>
          {error ? <p className="form-error">{error}</p> : null}
          {inviteUrl ? (
            <div className="invite-result">
              <Link2 size={17} />
              <input readOnly value={inviteUrl} onFocus={(event) => event.currentTarget.select()} />
              <button className="secondary-button" onClick={copyInvite}>{copied ? <Check size={16} /> : <Copy size={16} />}{copied ? "Zkopírováno" : "Kopírovat"}</button>
            </div>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}
