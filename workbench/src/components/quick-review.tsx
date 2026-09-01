"use client";

/* eslint-disable @next/next/no-img-element */

import { PointerEvent, useMemo, useRef, useState, useTransition } from "react";
import {
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  CheckCircle2,
  CircleHelp,
  ExternalLink,
  Hourglass,
  Layers3,
  LoaderCircle,
  PawPrint,
  RotateCcw,
  Search,
  ShieldX,
  X,
} from "lucide-react";
import { useRouter } from "next/navigation";

import { saveReview } from "@/app/actions";
import { INFORMATION_REASONS, informationRationale } from "@/lib/review-options";
import type { Profile, SaveFeedbackHandler, WorkbenchProduct } from "@/lib/workbench-types";

type DecisionKind = "vitar" | "nase" | "both" | "hold" | "veterina" | "archive";

const DECISIONS: Record<
  DecisionKind,
  { channels: Array<{ channel: string; decision: "include" | "exclude" | "hold" }>; role: "core" | "hold" | "exclude"; label: string }
> = {
  vitar: { channels: [{ channel: "vitar.cz", decision: "include" }], role: "core", label: "VITAR.cz" },
  nase: { channels: [{ channel: "nasevitaminy.cz", decision: "include" }], role: "core", label: "NašeVitamíny.cz" },
  both: {
    channels: [
      { channel: "vitar.cz", decision: "include" },
      { channel: "nasevitaminy.cz", decision: "include" },
    ],
    role: "core",
    label: "Oba e-shopy",
  },
  hold: { channels: [{ channel: "workshop_hold", decision: "hold" }], role: "hold", label: "Potřebuji informace" },
  veterina: { channels: [{ channel: "vitar_veterina", decision: "include" }], role: "core", label: "VITAR Veterina" },
  archive: { channels: [{ channel: "archive", decision: "exclude" }], role: "exclude", label: "Starý produkt / archiv" },
};

type QuickReviewProps = {
  products: WorkbenchProduct[];
  profile: Profile;
  onOpenProduct: (id: string) => void;
  onSelectFamily: (ids: string[]) => void;
  onSaveFeedback: SaveFeedbackHandler;
};

function sourceLabel(sourceKey: string) {
  if (sourceKey === "vitar") return "V";
  if (sourceKey === "nasevitaminy") return "NV";
  if (sourceKey === "ceskevitaminy") return "ČV";
  return sourceKey.slice(0, 2).toUpperCase();
}

export function QuickReview({ products, profile, onOpenProduct, onSelectFamily, onSaveFeedback }: QuickReviewProps) {
  const router = useRouter();
  const [queueIds] = useState(() =>
    products
      .filter((product) => !product.reviews.some((review) => review.profileId === profile.id && review.status === "submitted"))
      .map((product) => product.id),
  );
  const productById = useMemo(() => new Map(products.map((item) => [item.id, item])), [products]);
  const [index, setIndex] = useState(0);
  const [history, setHistory] = useState<number[]>([]);
  const [drag, setDrag] = useState({ x: 0, y: 0 });
  const [message, setMessage] = useState("");
  const [showInformationPicker, setShowInformationPicker] = useState(false);
  const [pending, startTransition] = useTransition();
  const pointerStart = useRef({ x: 0, y: 0 });
  const product = productById.get(queueIds[index]);
  const familyProducts = product ? products.filter((item) => item.familyKey === product.familyKey) : [];
  const completedBefore = products.length - queueIds.length;
  const completed = Math.min(products.length, completedBefore + index);

  function decide(kind: DecisionKind, informationReason?: string) {
    if (!product || pending) return;
    if (kind === "hold" && !informationReason) {
      setDrag({ x: 0, y: 0 });
      setShowInformationPicker(true);
      return;
    }
    const decision = DECISIONS[kind];
    const rationale = kind === "hold" && informationReason
      ? informationRationale(informationReason)
      : `Rychlý review: ${decision.label}.`;
    setMessage(decision.label);
    onSaveFeedback("saving", `Ukládám: ${decision.label}`);
    startTransition(async () => {
      try {
        await saveReview({
          productId: product.id,
          profileId: profile.id,
          categoryKey: product.categoryKey,
          categoryLabel: product.categoryLabel,
          portfolioRole: decision.role,
          lifecycleDecision: kind === "archive" ? "archive" : "active",
          confidence: kind === "hold" ? "low" : "medium",
          rationale,
          status: "submitted",
          channels: decision.channels.map((channel, channelIndex) => ({
            ...channel,
            role: channelIndex === 0 ? "primary" : "secondary",
            priority: channelIndex === 0 ? 1 : 2,
          })),
        });
        setShowInformationPicker(false);
        setHistory((current) => current.concat(index));
        setIndex((current) => current + 1);
        setDrag({ x: 0, y: 0 });
        setMessage(`Uloženo: ${decision.label}`);
        onSaveFeedback("saved", `${decision.label} uloženo`);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Rozhodnutí se nepodařilo uložit";
        setMessage(errorMessage);
        onSaveFeedback("error", errorMessage);
      }
    });
  }

  function pointerDown(event: PointerEvent<HTMLDivElement>) {
    if (pending) return;
    if ((event.target as HTMLElement).closest("a, button")) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    pointerStart.current = { x: event.clientX, y: event.clientY };
  }

  function pointerMove(event: PointerEvent<HTMLDivElement>) {
    if (!event.currentTarget.hasPointerCapture(event.pointerId) || pending) return;
    setDrag({ x: event.clientX - pointerStart.current.x, y: event.clientY - pointerStart.current.y });
  }

  function pointerUp(event: PointerEvent<HTMLDivElement>) {
    if (!event.currentTarget.hasPointerCapture(event.pointerId) || pending) return;
    event.currentTarget.releasePointerCapture(event.pointerId);
    const { x, y } = drag;
    if (Math.abs(x) < 60 && Math.abs(y) < 60) {
      setDrag({ x: 0, y: 0 });
      return;
    }
    if (Math.abs(x) > Math.abs(y)) decide(x > 0 ? "vitar" : "nase");
    else decide(y < 0 ? "both" : "hold");
  }

  function undo() {
    const previous = history.at(-1);
    if (previous === undefined || pending) return;
    setIndex(previous);
    setHistory((current) => current.slice(0, -1));
    setMessage("Zvolte nové rozhodnutí; původní se přepíše.");
  }

  if (!product) {
    return (
      <section className="quick-review complete">
        <CheckCircle2 size={44} />
        <h2>Domácí úkol je hotový</h2>
        <p>Máte odevzdaný názor pro všech {products.length} produktů.</p>
        <button className="secondary-button" onClick={() => router.refresh()}>Obnovit stav</button>
      </section>
    );
  }

  const rotation = Math.max(-7, Math.min(7, drag.x / 28));
  return (
    <section className="quick-review">
      <header className="quick-header">
        <div>
          <p className="eyebrow">RYCHLÝ REVIEW</p>
          <h1>Kam tento produkt patří?</h1>
        </div>
        <div className="quick-progress">
          <strong>{completed}/{products.length}</strong>
          <span><i style={{ width: `${Math.round((completed / products.length) * 100)}%` }} /></span>
        </div>
      </header>

      <div className="swipe-stage">
        <div className="swipe-hint top"><ArrowUp size={16} /> Oba</div>
        <div className="swipe-hint left"><ArrowLeft size={16} /> NašeVitamíny</div>
        <div className="swipe-hint right">VITAR.cz <ArrowRight size={16} /></div>
        <div className="swipe-hint bottom"><ArrowDown size={16} /> Potřebuji info</div>
        <div
          className={`swipe-card ${pending ? "saving" : ""}`}
          style={{ transform: `translate3d(${drag.x}px, ${drag.y}px, 0) rotate(${rotation}deg)` }}
          onPointerDown={pointerDown}
          onPointerMove={pointerMove}
          onPointerUp={pointerUp}
          onPointerCancel={() => setDrag({ x: 0, y: 0 })}
        >
          <div className="swipe-image">
            {product.imageUrl ? <img src={product.imageUrl} alt="" draggable={false} /> : <span>{product.brand.slice(0, 1)}</span>}
            <div className="swipe-sources">
              {product.sources.map((source) => (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  title={`Otevřít produkt na ${source.sourceSite}`}
                  aria-label={`Otevřít produkt na ${source.sourceSite}`}
                  onPointerDown={(event) => event.stopPropagation()}
                  onClick={(event) => event.stopPropagation()}
                  key={source.id}
                >
                  {sourceLabel(source.sourceKey)}
                </a>
              ))}
            </div>
            {pending ? <div className="saving-overlay"><LoaderCircle className="spin" /> Ukládám {message}</div> : null}
          </div>
          <div className="swipe-content">
            <p>{product.brand}</p>
            <h2>{product.name}</h2>
            <div className="swipe-meta">
              <span>{product.categoryLabel}</span>
              <span>{product.formLabel}</span>
              <span>{product.priceCzk ? `${Number(product.priceCzk).toLocaleString("cs-CZ")} Kč` : "Bez ceny"}</span>
            </div>
            {familyProducts.length > 1 ? (
              <button
                className="family-quick-button"
                onPointerDown={(event) => event.stopPropagation()}
                onClick={(event) => {
                  event.stopPropagation();
                  onSelectFamily(familyProducts.map((item) => item.id));
                }}
              >
                <Layers3 size={14} /> Rodina · {familyProducts.length} variant
              </button>
            ) : null}
            <p className="swipe-description">{product.description || "Produkt čeká na doplnění popisu."}</p>
            <div className="swipe-recommendation">
              <strong>Systém:</strong> {product.systemRecommendation.reason}
            </div>
            <button
              className="text-button"
              onPointerDown={(event) => event.stopPropagation()}
              onClick={(event) => { event.stopPropagation(); onOpenProduct(product.id); }}
            >
              <Search size={15} /> Detail a zdroje <ExternalLink size={12} />
            </button>
          </div>
        </div>
      </div>

      {showInformationPicker ? (
        <div className="quick-information-layer" role="dialog" aria-modal="true" aria-label="Důvod chybějících informací">
          <button className="quick-information-backdrop" onClick={() => setShowInformationPicker(false)} aria-label="Zavřít" />
          <section className="quick-information-panel">
            <header><span><CircleHelp size={18} /><strong>Co potřebujete doplnit?</strong></span><button className="icon-button" onClick={() => setShowInformationPicker(false)} title="Zavřít"><X size={17} /></button></header>
            <div>{INFORMATION_REASONS.map((reason) => <button onClick={() => decide("hold", reason)} key={reason}>{reason}</button>)}</div>
          </section>
        </div>
      ) : null}

      <div className="swipe-actions" aria-label="Rychlé rozhodnutí">
        <button className="swipe-action undo" onClick={undo} disabled={!history.length || pending} title="Vrátit předchozí kartu"><RotateCcw size={20} /></button>
        <button className="swipe-action nase" onClick={() => decide("nase")} disabled={pending} title="NašeVitamíny.cz"><ArrowLeft size={22} /><span>NV</span></button>
        <button className="swipe-action hold" onClick={() => decide("hold")} disabled={pending} title="Potřebuji informace"><ArrowDown size={21} /></button>
        <button className="swipe-action both" onClick={() => decide("both")} disabled={pending} title="Oba e-shopy"><ArrowUp size={21} /></button>
        <button className="swipe-action vitar" onClick={() => decide("vitar")} disabled={pending} title="VITAR.cz"><ArrowRight size={22} /><span>V</span></button>
      </div>
      <div className="special-actions">
        <button onClick={() => decide("veterina")} disabled={pending}><PawPrint size={15} /> Veterina</button>
        <button onClick={() => onOpenProduct(product.id)} disabled={pending}><Hourglass size={15} /> Doprodej / ukončit</button>
        <button onClick={() => decide("archive")} disabled={pending}><ShieldX size={15} /> Starý / archiv</button>
      </div>
      {message && !pending ? <p className="quick-message">{message}</p> : null}
    </section>
  );
}
