"use client";

import { FormEvent, useState, useTransition } from "react";
import { ArrowRight, KeyRound } from "lucide-react";

import { unlockApp } from "@/app/actions";

export function AccessGate() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [pending, startTransition] = useTransition();

  function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    startTransition(async () => {
      const result = await unlockApp(code);
      if (!result.ok) {
        setError(result.error || "Přístup se nepodařilo ověřit.");
        return;
      }
      window.location.reload();
    });
  }

  return (
    <main className="gate-shell">
      <section className="gate-panel">
        <div className="gate-mark" aria-hidden="true">V</div>
        <p className="eyebrow">VITAR DIGITAL GROWTH</p>
        <h1>Správa sortimentu</h1>
        <p className="gate-copy">
          Interní rozhodovací prostor pro portfolio VITAR.cz a NašeVitamíny.cz.
        </p>
        <form onSubmit={submit} className="gate-form">
          <label htmlFor="access-code">Přístupový kód</label>
          <div className="input-with-icon">
            <KeyRound size={17} aria-hidden="true" />
            <input
              id="access-code"
              type="password"
              value={code}
              onChange={(event) => setCode(event.target.value)}
              autoComplete="current-password"
              autoFocus
            />
          </div>
          {error ? <p className="form-error">{error}</p> : null}
          <button className="primary-button" disabled={pending || !code} type="submit">
            {pending ? "Ověřuji..." : "Vstoupit"}
            <ArrowRight size={16} aria-hidden="true" />
          </button>
        </form>
      </section>
    </main>
  );
}
