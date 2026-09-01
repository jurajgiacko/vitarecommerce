"use client";

/* eslint-disable @next/next/no-img-element */

import { FormEvent, useMemo, useState, useTransition } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  ExternalLink,
  FileText,
  History,
  LoaderCircle,
  MessageSquare,
  Save,
  Send,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { useRouter } from "next/navigation";

import { addComment, saveFinalDecision, saveReview } from "@/app/actions";
import type {
  ChannelDecision,
  ProductDetail,
  Profile,
  WorkbenchProduct,
} from "@/lib/workbench-types";

export const CHANNEL_OPTIONS = [
  { key: "vitar.cz", label: "VITAR.cz", note: "Premium marketplace" },
  { key: "nasevitaminy.cz", label: "NašeVitamíny.cz", note: "Retail a volume" },
  { key: "vitar_sport", label: "VITAR Sport", note: "Sportovní BU" },
  { key: "vitar_veterina", label: "VITAR Veterina", note: "Samostatný e-shop" },
  { key: "oem_b2b", label: "OEM / B2B", note: "Mimo B2C katalog" },
  { key: "archive", label: "Vyřadit / archiv", note: "Bez aktivního listingu" },
] as const;

const PORTFOLIO_ROLES = [
  ["hero", "Hero"],
  ["core", "Core"],
  ["support", "Support"],
  ["longtail", "Long tail"],
  ["test", "Test"],
  ["hold", "Hold"],
  ["exclude", "Vyřadit"],
] as const;

const TAB_OPTIONS = [
  ["decision", "Rozhodnutí", CheckCircle2],
  ["sources", "Zdroje", FileText],
  ["comments", "Poznámky", MessageSquare],
  ["history", "Historie", History],
] as const;

type DrawerProps = {
  product: WorkbenchProduct;
  profile: Profile;
  profiles: Profile[];
  categories: Array<{ key: string; label: string }>;
  onClose: () => void;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("cs-CZ", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function sourceLabel(key: string) {
  if (key === "vitar") return "VITAR.cz";
  if (key === "nasevitaminy") return "NašeVitamíny.cz";
  if (key === "ceskevitaminy") return "České vitamíny";
  return key;
}

export function ProductDrawer({ product, profile, profiles, categories, onClose }: DrawerProps) {
  const router = useRouter();
  const currentReview = product.reviews.find((review) => review.profileId === profile.id);
  const canSeeTeamOpinions =
    ["facilitator", "admin"].includes(profile.role) || currentReview?.status === "submitted";
  const suggestedChannels = product.systemRecommendation.channels.filter((channel) =>
    CHANNEL_OPTIONS.some((option) => option.key === channel),
  );
  const initialChannels = currentReview?.channels.length
    ? currentReview.channels.map((channel) => channel.channel)
    : suggestedChannels;
  const [tab, setTab] = useState<(typeof TAB_OPTIONS)[number][0]>("decision");
  const [channels, setChannels] = useState<string[]>(initialChannels);
  const [primaryChannel, setPrimaryChannel] = useState(
    currentReview?.channels.find((channel) => channel.role === "primary")?.channel ||
      product.systemRecommendation.primary ||
      initialChannels[0] ||
      "",
  );
  const [categoryKey, setCategoryKey] = useState(currentReview?.categoryKey || product.categoryKey);
  const [portfolioRole, setPortfolioRole] = useState(currentReview?.portfolioRole || "core");
  const [confidence, setConfidence] = useState(currentReview?.confidence || "medium");
  const [rationale, setRationale] = useState(currentReview?.rationale || "");
  const [comment, setComment] = useState("");
  const [detail, setDetail] = useState<ProductDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [pending, startTransition] = useTransition();

  const selectedCategory =
    categories.find((category) => category.key === categoryKey) || categories[0];

  function selectTab(nextTab: (typeof TAB_OPTIONS)[number][0]) {
    setTab(nextTab);
    if ((nextTab !== "sources" && nextTab !== "history") || detail || detailLoading) return;
    setDetailLoading(true);
    fetch(`/api/products/${product.id}`)
      .then((response) => {
        if (!response.ok) throw new Error("Detail zdrojů se nepodařilo načíst.");
        return response.json() as Promise<ProductDetail>;
      })
      .then(setDetail)
      .catch((error: Error) => setMessage(error.message))
      .finally(() => setDetailLoading(false));
  }

  const channelPayload = useMemo<ChannelDecision[]>(
    () =>
      channels.map((channel, index) => ({
        channel,
        decision: channel === "archive" ? "exclude" : "include",
        role: channel === primaryChannel || (!primaryChannel && index === 0) ? "primary" : "secondary",
        priority: channel === primaryChannel || (!primaryChannel && index === 0) ? 1 : 2,
      })),
    [channels, primaryChannel],
  );

  function toggleChannel(channel: string) {
    setChannels((current) => {
      if (current.includes(channel)) {
        const next = current.filter((item) => item !== channel);
        if (primaryChannel === channel) setPrimaryChannel(next[0] || "");
        return next;
      }
      if (channel === "archive") {
        setPrimaryChannel("archive");
        setPortfolioRole("exclude");
        return ["archive"];
      }
      const next = current.filter((item) => item !== "archive").concat(channel);
      if (!primaryChannel || primaryChannel === "archive") setPrimaryChannel(channel);
      return next;
    });
  }

  function submitReview(status: "draft" | "submitted") {
    if (!selectedCategory || !channels.length) {
      setMessage("Vyberte alespoň jeden cílový kanál a kategorii.");
      return;
    }
    setMessage("");
    startTransition(async () => {
      try {
        await saveReview({
          productId: product.id,
          profileId: profile.id,
          categoryKey: selectedCategory.key,
          categoryLabel: selectedCategory.label,
          portfolioRole: portfolioRole as "hero" | "core" | "support" | "longtail" | "test" | "exclude" | "hold",
          confidence: confidence as "low" | "medium" | "high",
          rationale,
          status,
          channels: channelPayload.map((channel) => ({
            ...channel,
            decision: channel.decision as "include" | "exclude" | "hold",
            role: channel.role as "primary" | "secondary",
          })),
        });
        setMessage(status === "submitted" ? "Návrh byl odevzdán." : "Koncept byl uložen.");
        router.refresh();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Uložení se nepodařilo.");
      }
    });
  }

  function finalize() {
    if (!selectedCategory || !channels.length) {
      setMessage("Finální rozhodnutí potřebuje kanál a kategorii.");
      return;
    }
    startTransition(async () => {
      try {
        await saveFinalDecision({
          productId: product.id,
          profileId: profile.id,
          categoryKey: selectedCategory.key,
          categoryLabel: selectedCategory.label,
          portfolioRole: portfolioRole as "hero" | "core" | "support" | "longtail" | "test" | "exclude" | "hold",
          confidence: confidence as "low" | "medium" | "high",
          rationale,
          status: "submitted",
          channels: channelPayload.map((channel) => ({
            ...channel,
            decision: channel.decision as "include" | "exclude" | "hold",
            role: channel.role as "primary" | "secondary",
          })),
        });
        setMessage("Finální rozhodnutí bylo schváleno.");
        router.refresh();
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Schválení se nepodařilo.");
      }
    });
  }

  function submitComment(event: FormEvent) {
    event.preventDefault();
    if (!comment.trim()) return;
    startTransition(async () => {
      await addComment({ productId: product.id, profileId: profile.id, body: comment });
      setComment("");
      router.refresh();
    });
  }

  return (
    <div className="drawer-layer" role="dialog" aria-modal="true" aria-label={`Detail produktu ${product.name}`}>
      <button className="drawer-backdrop" onClick={onClose} aria-label="Zavřít detail" />
      <aside className="product-drawer">
        <header className="drawer-header">
          <div className="drawer-product-image">
            {product.imageUrl ? <img src={product.imageUrl} alt="" /> : <span>{product.brand.slice(0, 1)}</span>}
          </div>
          <div className="drawer-title">
            <div className="drawer-meta-line">
              <span>{product.brand}</span>
              <span>SKU {product.sku || "čeká"}</span>
              {product.lifecycle === "wip" ? <span className="status-pill wip">WIP</span> : null}
            </div>
            <h2>{product.name}</h2>
            <div className="drawer-source-links">
              {product.sources.map((source) => (
                <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                  {sourceLabel(source.sourceKey)} <ExternalLink size={12} />
                </a>
              ))}
            </div>
          </div>
          <button className="icon-button" onClick={onClose} title="Zavřít detail">
            <X size={19} />
          </button>
        </header>

        <nav className="drawer-tabs" aria-label="Sekce produktu">
          {TAB_OPTIONS.map(([key, label, Icon]) => (
            <button className={tab === key ? "active" : ""} onClick={() => selectTab(key)} key={key}>
              <Icon size={15} />
              {label}
              {key === "comments" && product.comments.length ? <span>{product.comments.length}</span> : null}
            </button>
          ))}
        </nav>

        <div className="drawer-body">
          {tab === "decision" ? (
            <div className="decision-pane">
              {product.quality.hasConflict ? (
                <div className="data-warning">
                  <AlertTriangle size={18} />
                  <div>
                    <strong>Konflikt zdrojových dat</strong>
                    {product.fieldConflicts
                      .filter((conflict) => conflict.severity === "high")
                      .map((conflict) => (
                        <p key={conflict.field}>
                          {conflict.field}: {conflict.values?.join(" / ")}
                        </p>
                      ))}
                  </div>
                </div>
              ) : null}

              <section className="system-proposal">
                <div>
                  <Sparkles size={17} />
                  <strong>Systémový návrh</strong>
                  <span className={`confidence-dot ${product.systemRecommendation.confidence}`}>
                    {product.systemRecommendation.confidence}
                  </span>
                </div>
                <p>{product.systemRecommendation.reason}</p>
                {suggestedChannels.length ? (
                  <button
                    className="text-button"
                    onClick={() => {
                      setChannels(suggestedChannels);
                      setPrimaryChannel(product.systemRecommendation.primary || suggestedChannels[0]);
                    }}
                  >
                    Použít návrh
                  </button>
                ) : null}
              </section>

              <section className="form-section">
                <div className="section-heading">
                  <div>
                    <span>1</span>
                    <h3>Cílové e-shopy a BU</h3>
                  </div>
                  <small>Lze zvolit více kanálů</small>
                </div>
                <div className="channel-grid">
                  {CHANNEL_OPTIONS.map((channel) => {
                    const selected = channels.includes(channel.key);
                    return (
                      <button
                        type="button"
                        className={`channel-option ${selected ? "selected" : ""}`}
                        onClick={() => toggleChannel(channel.key)}
                        key={channel.key}
                      >
                        <span className="check-box">{selected ? <Check size={14} /> : null}</span>
                        <span>
                          <strong>{channel.label}</strong>
                          <small>{channel.note}</small>
                        </span>
                      </button>
                    );
                  })}
                </div>
                {channels.length > 1 ? (
                  <label className="field-row">
                    <span>Primární kanál</span>
                    <select value={primaryChannel} onChange={(event) => setPrimaryChannel(event.target.value)}>
                      {channels.map((channel) => (
                        <option value={channel} key={channel}>
                          {CHANNEL_OPTIONS.find((option) => option.key === channel)?.label || channel}
                        </option>
                      ))}
                    </select>
                  </label>
                ) : null}
              </section>

              <section className="form-section">
                <div className="section-heading">
                  <div>
                    <span>2</span>
                    <h3>Role v portfoliu</h3>
                  </div>
                </div>
                <div className="segmented-control role-control">
                  {PORTFOLIO_ROLES.map(([key, label]) => (
                    <button
                      type="button"
                      className={portfolioRole === key ? "active" : ""}
                      onClick={() => setPortfolioRole(key)}
                      key={key}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <div className="two-column-fields">
                  <label>
                    <span>Navržená kategorie</span>
                    <select value={categoryKey} onChange={(event) => setCategoryKey(event.target.value)}>
                      {categories.map((category) => (
                        <option value={category.key} key={category.key}>
                          {category.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    <span>Jistota rozhodnutí</span>
                    <select value={confidence} onChange={(event) => setConfidence(event.target.value)}>
                      <option value="high">Vysoká</option>
                      <option value="medium">Střední</option>
                      <option value="low">Nízká</option>
                    </select>
                  </label>
                </div>
                <label className="textarea-field">
                  <span>Odůvodnění / podmínky</span>
                  <textarea
                    rows={4}
                    value={rationale}
                    onChange={(event) => setRationale(event.target.value)}
                    placeholder="Proč tento kanál, co je potřeba doplnit nebo ověřit..."
                  />
                </label>
              </section>

              <section className="team-votes">
                <div className="section-heading">
                  <div>
                    <span>3</span>
                    <h3>Názory týmu</h3>
                  </div>
                  <small>
                    {canSeeTeamOpinions
                      ? `${product.reviews.filter((review) => review.status === "submitted").length}/${profiles.length} odevzdáno`
                      : "Odkryje se po vašem odevzdání"}
                  </small>
                </div>
                <div className="vote-list">
                  {profiles.map((person) => {
                    const review = product.reviews.find((item) => item.profileId === person.id);
                    const revealReview = person.id === profile.id || canSeeTeamOpinions;
                    return (
                      <div className="vote-row" key={person.id}>
                        <span className="avatar small" style={{ backgroundColor: person.color }}>{person.initials}</span>
                        <span className="vote-person">
                          <strong>{person.name}</strong>
                          <small>
                            {revealReview
                              ? review?.rationale || (review?.status === "draft" ? "Rozpracováno" : "Čeká na názor")
                              : "Nezávislý názor je zatím skrytý"}
                          </small>
                        </span>
                        <span className={`status-pill ${revealReview ? review?.status || "pending" : "hidden-vote"}`}>
                          {!revealReview
                            ? "Skryto"
                            : review?.status === "submitted"
                            ? review.channels.map((channel) => CHANNEL_OPTIONS.find((option) => option.key === channel.channel)?.label || channel.channel).join(" + ")
                            : review?.status === "draft"
                              ? "Koncept"
                              : "Čeká"}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </section>
            </div>
          ) : null}

          {tab === "sources" ? (
            <div className="sources-pane">
              {detailLoading ? <div className="loading-state"><LoaderCircle className="spin" /> Načítám zdroje...</div> : null}
              {detail?.sources.map((source) => (
                <article className="source-card" key={source.id}>
                  <header>
                    <div>
                      <span className={`source-logo ${source.sourceKey}`}>{sourceLabel(source.sourceKey).slice(0, 2)}</span>
                      <div>
                        <strong>{sourceLabel(source.sourceKey)}</strong>
                        <small>Aktuální publikovaný zdroj</small>
                      </div>
                    </div>
                    <a href={source.url} target="_blank" rel="noreferrer" title="Otevřít zdrojovou stránku">
                      <ExternalLink size={16} />
                    </a>
                  </header>
                  <dl className="source-fields">
                    <div><dt>Název</dt><dd>{source.name}</dd></div>
                    <div><dt>SKU</dt><dd>{source.sku || "Chybí"}</dd></div>
                    <div><dt>EAN</dt><dd>{source.ean || "Chybí"}</dd></div>
                    <div><dt>Cena</dt><dd>{source.priceCzk ? `${Number(source.priceCzk).toLocaleString("cs-CZ")} Kč` : "Chybí"}</dd></div>
                  </dl>
                  <p className="source-description">{source.description || "Krátký popis na zdroji chybí."}</p>
                  {Object.entries(source.contentSections).length ? (
                    <details className="content-details">
                      <summary>Obsahové sekce ({Object.keys(source.contentSections).length})</summary>
                      {Object.entries(source.contentSections).map(([heading, content]) => (
                        <div key={heading}><strong>{heading}</strong><p>{content}</p></div>
                      ))}
                    </details>
                  ) : null}
                </article>
              ))}
            </div>
          ) : null}

          {tab === "comments" ? (
            <div className="comments-pane">
              <div className="comment-list">
                {product.comments.length ? product.comments.map((item) => (
                  <article className="comment-item" key={item.id}>
                    <span className="avatar small" style={{ backgroundColor: item.profileColor }}>{item.profileInitials}</span>
                    <div><header><strong>{item.profileName}</strong><time>{formatDate(item.createdAt)}</time></header><p>{item.body}</p></div>
                  </article>
                )) : <div className="empty-inline"><MessageSquare size={22} /><p>Zatím bez poznámek.</p></div>}
              </div>
              <form className="comment-form" onSubmit={submitComment}>
                <textarea value={comment} onChange={(event) => setComment(event.target.value)} rows={3} placeholder="Přidat poznámku pro tým..." />
                <button className="primary-button compact" disabled={pending || !comment.trim()}><Send size={15} /> Odeslat</button>
              </form>
            </div>
          ) : null}

          {tab === "history" ? (
            <div className="history-pane">
              {detailLoading ? <div className="loading-state"><LoaderCircle className="spin" /> Načítám historii...</div> : null}
              {detail?.audit.length ? detail.audit.map((event) => (
                <div className="history-item" key={event.id}>
                  <span className="history-dot" />
                  <div><strong>{event.action.replaceAll("_", " ")}</strong><p>{event.actorName} · {formatDate(event.createdAt)}</p></div>
                </div>
              )) : !detailLoading ? <div className="empty-inline"><History size={22} /><p>První změna se objeví po uložení návrhu.</p></div> : null}
            </div>
          ) : null}
        </div>

        {tab === "decision" ? (
          <footer className="drawer-footer">
            <div>
              {message ? <p className="save-message">{message}</p> : <p>Změny se ukládají pod profilem {profile.name}.</p>}
            </div>
            <button className="secondary-button" disabled={pending} onClick={() => submitReview("draft")}>
              <Save size={16} /> Uložit koncept
            </button>
            <button className="primary-button" disabled={pending || !channels.length} onClick={() => submitReview("submitted")}>
              {pending ? <LoaderCircle className="spin" size={16} /> : <CheckCircle2 size={16} />} Odevzdat názor
            </button>
            {profile.role === "facilitator" ? (
              <button className="approve-button" disabled={pending || !channels.length} onClick={finalize} title="Uložit schválené finální rozhodnutí">
                <ShieldCheck size={17} /> Schválit finále
              </button>
            ) : null}
          </footer>
        ) : null}
      </aside>
    </div>
  );
}
