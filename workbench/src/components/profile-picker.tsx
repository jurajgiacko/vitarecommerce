"use client";

import { FormEvent, useState, useTransition } from "react";
import { ArrowRight, Plus, UserRound } from "lucide-react";
import { useRouter } from "next/navigation";

import { chooseProfile, createProfile } from "@/app/actions";
import type { Profile } from "@/lib/workbench-types";

export function ProfilePicker({ profiles }: { profiles: Profile[] }) {
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  const [pending, startTransition] = useTransition();
  const router = useRouter();

  function choose(id: string) {
    startTransition(async () => {
      await chooseProfile(id);
      router.refresh();
    });
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    startTransition(async () => {
      await createProfile({ name });
      router.refresh();
    });
  }

  return (
    <main className="profile-shell">
      <section className="profile-panel">
        <p className="eyebrow">VITAR ASSORTMENT WORKBENCH</p>
        <h1>Kdo dnes rozhoduje?</h1>
        <p>Každý profil má vlastní domácí úkol, poznámky a návrhy.</p>
        <div className="profile-grid">
          {profiles.map((profile) => (
            <button
              className="profile-option"
              key={profile.id}
              onClick={() => choose(profile.id)}
              disabled={pending}
            >
              <span className="avatar" style={{ backgroundColor: profile.color }}>
                {profile.initials}
              </span>
              <span>
                <strong>{profile.name}</strong>
                <small>{profile.role === "facilitator" ? "Facilitátor" : "Reviewer"}</small>
              </span>
              <ArrowRight size={17} aria-hidden="true" />
            </button>
          ))}
        </div>
        {creating ? (
          <form className="create-profile-form" onSubmit={submit}>
            <UserRound size={18} aria-hidden="true" />
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Jméno a příjmení"
              autoFocus
            />
            <button className="primary-button compact" disabled={pending || name.trim().length < 2}>
              Vytvořit
            </button>
          </form>
        ) : (
          <button className="text-button" onClick={() => setCreating(true)}>
            <Plus size={16} aria-hidden="true" />
            Přidat nový profil
          </button>
        )}
      </section>
    </main>
  );
}
