"use client";

/* eslint-disable @next/next/no-img-element */

import { FormEvent, useEffect, useMemo, useState, useTransition } from "react";
import {
  AlertTriangle,
  Archive,
  ArrowLeft,
  ArrowRight,
  BarChart3,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleDotDashed,
  ClipboardCheck,
  Database,
  Download,
  FileJson,
  FileSpreadsheet,
  FileText,
  Filter,
  Gauge,
  LayoutDashboard,
  Layers3,
  ListFilter,
  LoaderCircle,
  Menu,
  MessageSquareText,
  MoreHorizontal,
  PackagePlus,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Store,
  UsersRound,
  X,
  Zap,
} from "lucide-react";
import { useRouter } from "next/navigation";

import { bulkSaveReviews, createWipProduct } from "@/app/actions";
import { ProductDrawer, CHANNEL_OPTIONS, LIFECYCLE_OPTIONS } from "@/components/product-drawer";
import { QuickReview } from "@/components/quick-review";
import { TeamPanel } from "@/components/team-panel";
import { INFORMATION_REASONS } from "@/lib/review-options";
import type { SaveFeedbackHandler, SaveFeedbackState, WorkbenchData, WorkbenchProduct } from "@/lib/workbench-types";

type ViewKey =
  | "overview"
  | "quick"
  | "homework"
  | "portfolio"
  | "conflicts"
  | "coverage"
  | "wip"
  | "final"
  | "team";

const NAV_ITEMS: Array<{ key: ViewKey; label: string; icon: typeof LayoutDashboard }> = [
  { key: "overview", label: "Přehled", icon: LayoutDashboard },
  { key: "quick", label: "Rychlý review", icon: Zap },
  { key: "homework", label: "Můj domácí úkol", icon: ClipboardCheck },
  { key: "portfolio", label: "Všechny produkty", icon: ListFilter },
  { key: "conflicts", label: "Konflikty", icon: AlertTriangle },
  { key: "coverage", label: "Pokrytí a QA", icon: Database },
  { key: "wip", label: "WIP produkty", icon: PackagePlus },
  { key: "final", label: "Finální matice", icon: ShieldCheck },
  { key: "team", label: "Tým a pozvánky", icon: UsersRound },
];

const SOURCE_LABELS: Record<string, { short: string; label: string }> = {
  vitar: { short: "V", label: "VITAR.cz" },
  nasevitaminy: { short: "NV", label: "NašeVitamíny.cz" },
  ceskevitaminy: { short: "ČV", label: "České vitamíny" },
};

function currentReview(product: WorkbenchProduct, profileId: string) {
  return product.reviews.find((review) => review.profileId === profileId);
}

function channelLabel(key: string) {
  return CHANNEL_OPTIONS.find((channel) => channel.key === key)?.label ||
    (key === "workshop_hold" ? "Hold" : key);
}

function reviewStatus(product: WorkbenchProduct, profileId: string) {
  const review = currentReview(product, profileId);
  if (review?.channels.some((channel) => channel.channel === "workshop_hold")) return { key: "needs-info", label: "Chybí info" };
  if (review?.status === "submitted") return { key: "submitted", label: "Odevzdáno" };
  if (review?.status === "draft") return { key: "draft", label: "Koncept" };
  return { key: "pending", label: "Čeká" };
}

function lifecycleDecision(product: WorkbenchProduct, profileId: string) {
  return currentReview(product, profileId)?.lifecycleDecision ||
    product.finalDecision?.lifecycleDecision ||
    "active";
}

function lifecycleLabel(key: string) {
  return LIFECYCLE_OPTIONS.find(([value]) => value === key)?.[1] || key;
}

function formatDeadline(value: string | null) {
  if (!value) return "Bez termínu";
  return new Intl.DateTimeFormat("cs-CZ", {
    weekday: "long",
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Europe/Prague",
  }).format(new Date(value));
}

function pageTitle(view: ViewKey) {
  return NAV_ITEMS.find((item) => item.key === view)?.label || "Portfolio";
}

export function WorkbenchApp({ data }: { data: WorkbenchData }) {
  const [view, setView] = useState<ViewKey>("overview");
  const [search, setSearch] = useState("");
  const [brand, setBrand] = useState("all");
  const [category, setCategory] = useState("all");
  const [source, setSource] = useState("all");
  const [status, setStatus] = useState("all");
  const [lifecycle, setLifecycle] = useState("all");
  const [page, setPage] = useState(1);
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [mobileNav, setMobileNav] = useState(false);
  const [showWip, setShowWip] = useState(false);
  const [toast, setToast] = useState("");
  const [saveFeedback, setSaveFeedback] = useState<{ state: SaveFeedbackState; message: string }>({ state: "idle", message: "" });
  const [pending, startTransition] = useTransition();
  const router = useRouter();

  const categories = useMemo(() => {
    const values = new Map<string, string>();
    for (const product of data.products) values.set(product.categoryKey, product.categoryLabel);
    if (![...values.values()].includes("Nezařazeno")) values.set("unclassified", "Nezařazeno");
    return [...values.entries()]
      .map(([key, label]) => ({ key, label }))
      .sort((left, right) => left.label.localeCompare(right.label, "cs"));
  }, [data.products]);
  const brands = useMemo(
    () => [...new Set(data.products.map((product) => product.brand))].sort((a, b) => a.localeCompare(b, "cs")),
    [data.products],
  );

  const metrics = useMemo(() => {
    const submitted = data.products.filter(
      (product) => currentReview(product, data.profile.id)?.status === "submitted",
    ).length;
    const drafts = data.products.filter(
      (product) => currentReview(product, data.profile.id)?.status === "draft",
    ).length;
    const conflicts = data.products.filter((product) =>
      product.consensusConflict ||
      product.quality.hasConflict ||
      product.reviews.some((review) => review.channels.some((channel) => channel.channel === "workshop_hold")),
    ).length;
    const sourceGaps = data.products.filter(
      (product) => product.sourceCount === 1 || !product.quality.hasEan || !product.quality.hasDescription,
    ).length;
    const finalized = data.products.filter((product) => product.finalDecision).length;
    const consensus = data.products.filter((product) => {
      const complete = product.reviews.filter((review) => review.status === "submitted");
      return complete.length >= 2 && !product.consensusConflict;
    }).length;
    return { submitted, drafts, conflicts, sourceGaps, finalized, consensus };
  }, [data.products, data.profile.id]);

  const counts: Record<ViewKey, number | null> = {
    overview: null,
    quick: data.products.length - metrics.submitted,
    homework: data.products.length - metrics.submitted,
    portfolio: data.products.length,
    conflicts: metrics.conflicts,
    coverage: metrics.sourceGaps,
    wip: data.products.filter((product) => product.lifecycle === "wip").length,
    final: metrics.finalized,
    team: data.profiles.length,
  };

  const selectedProduct = data.products.find((product) => product.id === selectedProductId) || null;

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 3500);
    return () => window.clearTimeout(timer);
  }, [toast]);

  useEffect(() => {
    if (saveFeedback.state !== "saved" && saveFeedback.state !== "error") return;
    const timer = window.setTimeout(() => setSaveFeedback({ state: "idle", message: "" }), 3800);
    return () => window.clearTimeout(timer);
  }, [saveFeedback]);

  useEffect(() => {
    if (saveFeedback.state !== "idle") return;
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") startTransition(() => router.refresh());
    }, 30_000);
    return () => window.clearInterval(timer);
  }, [router, saveFeedback.state, startTransition]);

  const reportSave: SaveFeedbackHandler = (state, message) => setSaveFeedback({ state, message });

  function selectFamily(ids: string[]) {
    setSelectedIds(new Set(ids));
    setSelectedProductId(null);
    setView("portfolio");
    setPage(1);
    setToast(`${ids.length} variant produktové rodiny je vybráno.`);
  }

  function changeView(next: ViewKey) {
    if (view === "quick" && next !== "quick") router.refresh();
    setView(next);
    setPage(1);
    setMobileNav(false);
    setSelectedIds(new Set());
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNav ? "mobile-open" : ""}`}>
        <header className="brand-lockup">
          <div className="brand-symbol">V</div>
          <div><strong>VITAR</strong><span>Assortment Workbench</span></div>
          <button className="icon-button mobile-close" onClick={() => setMobileNav(false)} title="Zavřít menu"><X size={18} /></button>
        </header>
        <div className="round-chip"><span className="live-dot" /><span><strong>Review otevřený</strong><small>Termín: {formatDeadline(data.round.dueAt).split(",")[0]}</small></span></div>
        <nav className="side-nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <button className={view === item.key ? "active" : ""} onClick={() => changeView(item.key)} key={item.key}>
                <Icon size={17} />
                <span>{item.label}</span>
                {counts[item.key] !== null ? <small>{counts[item.key]}</small> : null}
              </button>
            );
          })}
        </nav>
        <footer className="sidebar-footer">
          <div className="profile-block">
            <span className="avatar" style={{ backgroundColor: data.profile.color }}>{data.profile.initials}</span>
            <span><strong>{data.profile.name}</strong></span>
            <MoreHorizontal size={17} />
          </div>
        </footer>
      </aside>

      {mobileNav ? <button className="mobile-nav-backdrop" onClick={() => setMobileNav(false)} aria-label="Zavřít menu" /> : null}

      <div className="app-main">
        <header className="topbar">
          <button className="icon-button mobile-menu" onClick={() => setMobileNav(true)} title="Otevřít menu"><Menu size={19} /></button>
          <div><span className="topbar-path">VITAR DIGITAL GROWTH /</span><strong>{pageTitle(view)}</strong></div>
          <div className="topbar-actions">
            <div className={`sync-state ${saveFeedback.state}`} aria-live="polite"><span /><strong>{saveFeedback.state === "saving" ? "Ukládám…" : saveFeedback.state === "saved" ? "Uloženo" : saveFeedback.state === "error" ? "Chyba uložení" : "Data aktuální"}</strong><small>{saveFeedback.state === "idle" ? (data.crawl ? new Intl.DateTimeFormat("cs-CZ", { day: "numeric", month: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Prague" }).format(new Date(data.crawl.completedAt)) : "") : saveFeedback.message}</small></div>
            <button className="icon-button sync-refresh" onClick={() => startTransition(() => router.refresh())} title="Obnovit data týmu" aria-label="Obnovit data týmu"><RefreshCw className={pending ? "spin" : ""} size={16} /></button>
            <details className="export-menu">
              <summary className="secondary-button" title="Exportovat data"><Download size={16} /> <span>Export</span></summary>
              <div>
                <strong>Finální rozhodnutí</strong>
                <a href="/api/export?format=json&scope=final"><FileJson size={15} /> JSON</a>
                <a href="/api/export?format=md&scope=final"><FileText size={15} /> Markdown</a>
                <a href="/api/export?format=csv&scope=final"><FileSpreadsheet size={15} /> CSV</a>
                <strong>Všechny názory</strong>
                <a href="/api/export?format=json&scope=all"><FileJson size={15} /> JSON</a>
                <a href="/api/export?format=md&scope=all"><FileText size={15} /> Markdown</a>
                <a href="/api/export?format=csv&scope=all"><FileSpreadsheet size={15} /> CSV</a>
              </div>
            </details>
            <span className="avatar top-avatar" style={{ backgroundColor: data.profile.color }}>{data.profile.initials}</span>
          </div>
        </header>

        <main className="content-area">
          {view === "overview" ? (
            <Overview
              data={data}
              metrics={metrics}
              onChangeView={changeView}
              onOpenProduct={setSelectedProductId}
            />
          ) : null}
          {view === "quick" ? (
            <QuickReview products={data.products} profile={data.profile} onOpenProduct={setSelectedProductId} onSelectFamily={selectFamily} onSaveFeedback={reportSave} />
          ) : null}
          {view === "team" ? (
            <TeamPanel profiles={data.profiles} products={data.products} currentProfile={data.profile} />
          ) : null}
          {!(["overview", "quick", "team"] as ViewKey[]).includes(view) ? (
            <ProductWorkspace
              view={view}
              products={data.products}
              profileId={data.profile.id}
              brands={brands}
              categories={categories}
              search={search}
              setSearch={(value) => { setSearch(value); setPage(1); }}
              brand={brand}
              setBrand={(value) => { setBrand(value); setPage(1); }}
              category={category}
              setCategory={(value) => { setCategory(value); setPage(1); }}
              source={source}
              setSource={(value) => { setSource(value); setPage(1); }}
              status={status}
              setStatus={(value) => { setStatus(value); setPage(1); }}
              lifecycle={lifecycle}
              setLifecycle={(value) => { setLifecycle(value); setPage(1); }}
              page={page}
              setPage={setPage}
              selectedIds={selectedIds}
              setSelectedIds={setSelectedIds}
              onOpenProduct={setSelectedProductId}
              onSelectFamily={selectFamily}
              onAddWip={() => setShowWip(true)}
            />
          ) : null}
        </main>

        <nav className="mobile-bottom-nav">
          {NAV_ITEMS.filter((item) => ["overview", "quick", "homework", "conflicts"].includes(item.key)).map((item) => {
            const Icon = item.icon;
            return <button className={view === item.key ? "active" : ""} onClick={() => changeView(item.key)} key={item.key}><Icon size={19} /><span>{item.label.replace("Můj domácí úkol", "Úkol").replace("Rychlý review", "Swipe")}</span></button>;
          })}
          <button onClick={() => setMobileNav(true)}><Menu size={19} /><span>Více</span></button>
        </nav>
      </div>

      {selectedProduct ? (
        <ProductDrawer
          key={selectedProduct.id}
          product={selectedProduct}
          profile={data.profile}
          profiles={data.profiles}
          categories={categories}
          familyProducts={data.products.filter((product) => product.familyKey === selectedProduct.familyKey)}
          onSelectFamily={selectFamily}
          onSaveFeedback={reportSave}
          onClose={() => setSelectedProductId(null)}
        />
      ) : null}
      {showWip ? (
        <WipDialog profileId={data.profile.id} categories={categories} onSaveFeedback={reportSave} onClose={() => setShowWip(false)} />
      ) : null}
      {selectedIds.size ? (
        <BulkBar
          selectedIds={selectedIds}
          profileId={data.profile.id}
          pending={pending}
          onClear={() => setSelectedIds(new Set())}
          onRun={(channel, decision, submit, reason) => {
            reportSave("saving", `${selectedIds.size} produktů`);
            startTransition(async () => {
              try {
                await bulkSaveReviews({
                  productIds: [...selectedIds],
                  profileId: data.profile.id,
                  channel,
                  decision,
                  reason,
                  status: submit ? "submitted" : "draft",
                });
                setToast(`${selectedIds.size} produktů bylo ${submit ? "odevzdáno" : "uloženo"}.`);
                reportSave("saved", `${selectedIds.size} produktů uloženo`);
                setSelectedIds(new Set());
                router.refresh();
              } catch (error) {
                reportSave("error", error instanceof Error ? error.message : "Hromadné uložení se nepodařilo");
              }
            });
          }}
        />
      ) : null}
      {toast && saveFeedback.state === "idle" ? <div className="toast"><Check size={16} />{toast}</div> : null}
      {saveFeedback.state !== "idle" ? <div className={`mobile-save-feedback ${saveFeedback.state}`} aria-live="polite">{saveFeedback.state === "saving" ? <LoaderCircle className="spin" size={16} /> : saveFeedback.state === "saved" ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}<span><strong>{saveFeedback.state === "saving" ? "Ukládám…" : saveFeedback.state === "saved" ? "Uloženo" : "Chyba uložení"}</strong><small>{saveFeedback.message}</small></span></div> : null}
    </div>
  );
}

type Metrics = {
  submitted: number;
  drafts: number;
  conflicts: number;
  sourceGaps: number;
  finalized: number;
  consensus: number;
};

function Overview({
  data,
  metrics,
  onChangeView,
  onOpenProduct,
}: {
  data: WorkbenchData;
  metrics: Metrics;
  onChangeView: (view: ViewKey) => void;
  onOpenProduct: (id: string) => void;
}) {
  const progress = Math.round((metrics.submitted / data.products.length) * 100);
  const sourceCoverage = (data.crawl?.summary.coverage || {}) as Record<
    string,
    { sitemap_urls?: number; inventory_urls?: number; products?: number; errors?: number; reconciled?: boolean }
  >;
  const nextProduct = data.products.find(
    (product) => currentReview(product, data.profile.id)?.status !== "submitted",
  );
  const brandCounts = [...new Map(data.products.map((product) => [product.brand, 0])).keys()]
    .map((brand) => ({ brand, count: data.products.filter((product) => product.brand === brand).length }))
    .sort((left, right) => right.count - left.count)
    .slice(0, 8);
  return (
    <section className="overview-page">
      <header className="overview-heading">
        <div>
          <p className="eyebrow">REVIEW ROUND · {data.round.status.toUpperCase()}</p>
          <h1>Rozdělení portfolia pro nové e-shopy</h1>
          <p>{data.round.description}</p>
        </div>
        <div className="deadline-block"><span>Rozhodnutí</span><strong>{formatDeadline(data.round.dueAt)}</strong></div>
      </header>

      <section className="homework-guide">
        <header>
          <div><p className="eyebrow">RYCHLÝ NÁVOD</p><h2>Jak připravit domácí úkol</h2><p>U každého produktu rozhodněte, zda zůstává, kde se bude prodávat a kam patří.</p></div>
          <button className="primary-button" onClick={() => onChangeView("quick")}><Zap size={16} /> Začít rychlý review</button>
        </header>
        <div className="homework-guide-steps">
          <div><span><Archive size={17} /></span><p><strong>1. Ponechat, nebo vyřadit?</strong>Určete aktivní produkt, doprodej, ukončení výroby nebo archiv.</p></div>
          <div><span><Store size={17} /></span><p><strong>2. Zvolte cílový e-shop</strong>VITAR.cz, NašeVitamíny.cz, oba, Veterina nebo společné rozhodnutí.</p></div>
          <div><span><ListFilter size={17} /></span><p><strong>3. Potvrďte kategorii</strong>Vyberte hlavní kategorii; stejné varianty můžete označit přes Produktovou rodinu.</p></div>
          <div><span><MessageSquareText size={17} /></span><p><strong>4. Doplňte výjimky a novinky</strong>Chybí-li podklad, označte důvod; novinky uložte ve WIP jako trvalý placeholder.</p></div>
        </div>
      </section>

      <div className="metric-strip">
        <button onClick={() => onChangeView("homework")}><span className="metric-icon green"><ClipboardCheck size={19} /></span><span><small>Můj postup</small><strong>{metrics.submitted}<i> / {data.products.length}</i></strong><em>{progress}% hotovo</em></span></button>
        <button onClick={() => onChangeView("conflicts")}><span className="metric-icon red"><AlertTriangle size={19} /></span><span><small>Konflikty</small><strong>{metrics.conflicts}</strong><em>data nebo názory</em></span></button>
        <button onClick={() => onChangeView("final")}><span className="metric-icon blue"><ShieldCheck size={19} /></span><span><small>Finálně schváleno</small><strong>{metrics.finalized}</strong><em>z {data.products.length} produktů</em></span></button>
        <button onClick={() => onChangeView("coverage")}><span className="metric-icon gold"><Database size={19} /></span><span><small>QA fronta</small><strong>{metrics.sourceGaps}</strong><em>vyžaduje kontrolu</em></span></button>
      </div>

      <div className="overview-grid">
        <section className="homework-panel">
          <header><div><h2>Dnešní domácí úkol</h2><p>Váš osobní názor před společným workshopem.</p></div><span>{progress}%</span></header>
          <div className="large-progress"><i style={{ width: `${progress}%` }} /></div>
          <div className="homework-stats"><span><strong>{metrics.submitted}</strong> odevzdáno</span><span><strong>{metrics.drafts}</strong> koncepty</span><span><strong>{data.products.length - metrics.submitted - metrics.drafts}</strong> čeká</span></div>
          {nextProduct ? (
            <div className="next-product">
              <div>{nextProduct.imageUrl ? <img src={nextProduct.imageUrl} alt="" /> : <span>{nextProduct.brand[0]}</span>}</div>
              <span><small>Další produkt</small><strong>{nextProduct.name}</strong><em>{nextProduct.brand} · {nextProduct.categoryLabel}</em></span>
              <button className="primary-button" onClick={() => onChangeView("quick")}><Zap size={16} /> Spustit swipe</button>
              <button className="icon-button" onClick={() => onOpenProduct(nextProduct.id)} title="Otevřít plný detail"><ChevronRight size={18} /></button>
            </div>
          ) : null}
        </section>

        <section className="agreement-panel">
          <header><div><h2>Shoda týmu</h2><p>Produkty s nejméně dvěma odevzdanými názory.</p></div><Gauge size={21} /></header>
          <div className="agreement-chart"><strong>{metrics.consensus}</strong><span>produktů ve shodě</span></div>
          <div className="agreement-legend"><span><i className="green" /> Shoda {metrics.consensus}</span><span><i className="red" /> Rozpor {data.products.filter((product) => product.consensusConflict).length}</span><span><i className="gray" /> Čeká na hlasy</span></div>
          <button className="text-button" onClick={() => onChangeView("conflicts")}>Otevřít rozdílné názory <ArrowRight size={15} /></button>
        </section>
      </div>

      <section className="team-overview">
        <header><div><h2>Postup podle profilů</h2><p>Vidíte přípravu týmu ještě před workshopem.</p></div><button className="text-button" onClick={() => onChangeView("team")}><UsersRound size={15} /> Spravovat tým</button></header>
        <div className="profile-progress-list">
          {data.profiles.map((profile) => {
            const done = data.products.filter((product) => product.reviews.some((review) => review.profileId === profile.id && review.status === "submitted")).length;
            const percent = Math.round((done / data.products.length) * 100);
            return <div className="profile-progress-row" key={profile.id}><span className="avatar small" style={{ backgroundColor: profile.color }}>{profile.initials}</span><span className="profile-progress-name"><strong>{profile.name}</strong></span><span className="profile-progress-bar"><i style={{ width: `${percent}%` }} /></span><strong>{done}/{data.products.length}</strong><em>{percent}%</em></div>;
          })}
        </div>
      </section>

      <div className="overview-grid lower">
        <section className="source-audit-panel">
          <header><div><h2>Kontrola zdrojů</h2><p>Každá sitemap URL je zaúčtovaná.</p></div><span className={`audit-state ${data.crawl?.errorCount ? "error" : "ok"}`}><CircleDotDashed size={15} /> {data.crawl?.errorCount || 0} chyb</span></header>
          <div className="source-audit-table">
            {Object.entries(sourceCoverage).map(([key, value]) => (
              <div key={key}><span className={`source-logo ${key}`}>{SOURCE_LABELS[key]?.short || key.slice(0, 2)}</span><span><strong>{SOURCE_LABELS[key]?.label || key}</strong><small>{value.products || 0} produktových profilů</small></span><span><strong>{value.inventory_urls || 0}/{value.sitemap_urls || 0}</strong><small>URL zkontrolováno</small></span><span className={value.reconciled ? "reconciled" : "not-reconciled"}>{value.reconciled ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}{value.reconciled ? "Sedí" : "Nesedí"}</span></div>
            ))}
          </div>
        </section>

        <section className="brand-panel">
          <header><div><h2>Největší značky</h2><p>Počet master produktů po bezpečném párování.</p></div><BarChart3 size={20} /></header>
          <div className="brand-bars">
            {brandCounts.map((item) => <div key={item.brand}><span>{item.brand}</span><i><b style={{ width: `${Math.max(6, (item.count / brandCounts[0].count) * 100)}%` }} /></i><strong>{item.count}</strong></div>)}
          </div>
        </section>
      </div>
    </section>
  );
}

type ProductWorkspaceProps = {
  view: ViewKey;
  products: WorkbenchProduct[];
  profileId: string;
  brands: string[];
  categories: Array<{ key: string; label: string }>;
  search: string;
  setSearch: (value: string) => void;
  brand: string;
  setBrand: (value: string) => void;
  category: string;
  setCategory: (value: string) => void;
  source: string;
  setSource: (value: string) => void;
  status: string;
  setStatus: (value: string) => void;
  lifecycle: string;
  setLifecycle: (value: string) => void;
  page: number;
  setPage: (page: number) => void;
  selectedIds: Set<string>;
  setSelectedIds: (value: Set<string>) => void;
  onOpenProduct: (id: string) => void;
  onSelectFamily: (ids: string[]) => void;
  onAddWip: () => void;
};

function ProductWorkspace(props: ProductWorkspaceProps) {
  const pageSize = 40;
  const filtered = useMemo(() => {
    const query = props.search.trim().toLocaleLowerCase("cs");
    return props.products
      .filter((product) => {
        const mine = currentReview(product, props.profileId);
        const effectiveCategoryKey = props.view === "final" && product.finalDecision
          ? product.finalDecision.categoryKey
          : mine?.categoryKey || product.finalDecision?.categoryKey || product.categoryKey;
        if (props.view === "homework" && mine?.status === "submitted") return false;
        if (props.view === "conflicts" && !product.consensusConflict && !product.quality.hasConflict && !product.reviews.some((review) => review.channels.some((channel) => channel.channel === "workshop_hold"))) return false;
        if (props.view === "coverage" && product.sourceCount > 1 && product.quality.hasEan && product.quality.hasDescription && !product.quality.hasConflict) return false;
        if (props.view === "wip" && product.lifecycle !== "wip") return false;
        if (props.brand !== "all" && product.brand !== props.brand) return false;
        if (props.category !== "all" && effectiveCategoryKey !== props.category) return false;
        if (props.source !== "all" && !product.sources.some((source) => source.sourceKey === props.source)) return false;
        if (props.status !== "all" && reviewStatus(product, props.profileId).key !== props.status) return false;
        if (props.lifecycle !== "all" && lifecycleDecision(product, props.profileId) !== props.lifecycle) return false;
        if (query && !`${product.name} ${product.brand} ${product.sku} ${product.ean}`.toLocaleLowerCase("cs").includes(query)) return false;
        return true;
      })
      .sort((left, right) => {
        if (props.view === "final") return Number(Boolean(left.finalDecision)) - Number(Boolean(right.finalDecision));
        if (props.view === "conflicts") return Number(right.quality.hasConflict) - Number(left.quality.hasConflict);
        return left.brand.localeCompare(right.brand, "cs") || left.name.localeCompare(right.name, "cs");
      });
  }, [props]);
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const visible = filtered.slice((props.page - 1) * pageSize, props.page * pageSize);
  const allVisibleSelected = visible.length > 0 && visible.every((product) => props.selectedIds.has(product.id));

  function toggleAll() {
    const next = new Set(props.selectedIds);
    if (allVisibleSelected) visible.forEach((product) => next.delete(product.id));
    else visible.forEach((product) => next.add(product.id));
    props.setSelectedIds(next);
  }

  function toggleOne(id: string) {
    const next = new Set(props.selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    props.setSelectedIds(next);
  }

  return (
    <section className="workspace-page">
      <header className="page-heading compact-heading">
        <div><p className="eyebrow">{props.view === "conflicts" ? "DECISION QUEUE" : props.view === "coverage" ? "DATA CONTROL TOWER" : "MASTER CATALOG"}</p><h1>{pageTitle(props.view)}</h1><p>{props.view === "homework" ? "Produkty, pro které ještě nemáte odevzdaný názor." : props.view === "conflicts" ? "Rozdílné názory nebo konfliktní zdrojová data." : props.view === "coverage" ? "Chybějící data, osamocené zdroje a identifikační konflikty." : props.view === "final" ? "Schválené rozhodnutí je oddělené od osobních návrhů." : "Kompletní portfolio ze tří aktuálních zdrojů."}</p></div>
        <div className="heading-actions"><span className="result-count"><strong>{filtered.length}</strong> produktů</span><button className="secondary-button" onClick={props.onAddWip}><Plus size={16} /> Nový WIP</button></div>
      </header>

      <div className="filter-toolbar">
        <label className="search-field"><Search size={16} /><input value={props.search} onChange={(event) => props.setSearch(event.target.value)} placeholder="Hledat název, SKU nebo EAN" /><kbd>⌘ K</kbd></label>
        <select value={props.brand} onChange={(event) => props.setBrand(event.target.value)} aria-label="Filtrovat značku"><option value="all">Všechny značky</option>{props.brands.map((item) => <option key={item}>{item}</option>)}</select>
        <select value={props.category} onChange={(event) => props.setCategory(event.target.value)} aria-label="Filtrovat kategorii"><option value="all">Všechny kategorie</option>{props.categories.map((item) => <option value={item.key} key={item.key}>{item.label}</option>)}</select>
        <select value={props.source} onChange={(event) => props.setSource(event.target.value)} aria-label="Filtrovat zdroj"><option value="all">Všechny zdroje</option><option value="vitar">VITAR.cz</option><option value="nasevitaminy">NašeVitamíny.cz</option><option value="ceskevitaminy">České vitamíny</option></select>
        <select value={props.status} onChange={(event) => props.setStatus(event.target.value)} aria-label="Filtrovat stav"><option value="all">Všechny stavy</option><option value="pending">Čeká</option><option value="draft">Koncept</option><option value="submitted">Odevzdáno</option><option value="needs-info">Chybí informace</option></select>
        <select value={props.lifecycle} onChange={(event) => props.setLifecycle(event.target.value)} aria-label="Filtrovat životní cyklus"><option value="all">Všechny životní cykly</option>{LIFECYCLE_OPTIONS.map(([key, label]) => <option value={key} key={key}>{label}</option>)}</select>
        <button className="icon-button" title="Vymazat filtry" onClick={() => { props.setSearch(""); props.setBrand("all"); props.setCategory("all"); props.setSource("all"); props.setStatus("all"); props.setLifecycle("all"); }}><X size={17} /></button>
      </div>

      <div className="product-table-wrap">
        <table className="product-table">
          <thead><tr><th className="check-column"><button className={`table-checkbox ${allVisibleSelected ? "checked" : ""}`} onClick={toggleAll} aria-label="Vybrat viditelné produkty">{allVisibleSelected ? <Check size={13} /> : null}</button></th><th>Produkt</th><th>Kategorie</th><th>Zdroje</th><th>Doporučení</th><th>Můj stav</th><th>Tým</th><th>QA</th><th /></tr></thead>
          <tbody>
            {visible.map((product) => {
              const mine = currentReview(product, props.profileId);
              const productStatus = reviewStatus(product, props.profileId);
              const productLifecycle = lifecycleDecision(product, props.profileId);
              const effectiveCategoryLabel = props.view === "final" && product.finalDecision
                ? product.finalDecision.categoryLabel
                : mine?.categoryLabel || product.finalDecision?.categoryLabel || product.categoryLabel;
              const recommendation = mine?.channels.length ? mine.channels.map((channel) => channelLabel(channel.channel)).join(" + ") : product.systemRecommendation.channels.map(channelLabel).join(" + ");
              return (
                <tr onClick={() => props.onOpenProduct(product.id)} className={props.selectedIds.has(product.id) ? "selected-row" : ""} key={product.id}>
                  <td className="check-column"><button className={`table-checkbox ${props.selectedIds.has(product.id) ? "checked" : ""}`} onClick={(event) => { event.stopPropagation(); toggleOne(product.id); }} aria-label={`Vybrat ${product.name}`}>{props.selectedIds.has(product.id) ? <Check size={13} /> : null}</button></td>
                  <td><div className="product-cell"><div className="table-image">{product.imageUrl ? <img src={product.imageUrl} alt="" /> : <span>{product.brand[0]}</span>}</div><span><strong>{product.name}</strong><small>{product.brand} · SKU {product.sku || "čeká"}{product.lifecycle === "wip" ? " · WIP" : ""}</small>{product.familySize > 1 ? <button className="family-select-button" onClick={(event) => { event.stopPropagation(); props.onSelectFamily(props.products.filter((item) => item.familyKey === product.familyKey).map((item) => item.id)); }}><Layers3 size={12} /> Rodina · {product.familySize} variant</button> : null}</span></div></td>
                  <td><span className="category-cell">{effectiveCategoryLabel}</span><small className="form-label">{product.formLabel}</small></td>
                  <td><div className="source-badges">{product.sources.map((sourceItem) => <a href={sourceItem.url} target="_blank" rel="noreferrer" className={sourceItem.sourceKey} title={`Otevřít ${SOURCE_LABELS[sourceItem.sourceKey]?.label || sourceItem.sourceSite}`} aria-label={`Otevřít produkt na ${SOURCE_LABELS[sourceItem.sourceKey]?.label || sourceItem.sourceSite}`} onClick={(event) => event.stopPropagation()} key={sourceItem.id}>{SOURCE_LABELS[sourceItem.sourceKey]?.short}</a>)}</div></td>
                  <td><span className={`recommendation-cell ${mine ? "personal" : "system"}`}>{mine ? null : <Sparkles size={12} />}{recommendation || "K rozhodnutí"}</span></td>
                  <td><span className={`status-pill ${productStatus.key}`}>{productStatus.label}</span></td>
                  <td><div className="team-avatars">{product.reviews.slice(0, 5).map((review) => <span className={`avatar tiny ${review.status}`} style={{ backgroundColor: review.profileColor }} title={`${review.profileName}: ${review.status}`} key={review.profileId}>{review.profileInitials}</span>)}{product.consensusConflict ? <AlertTriangle className="team-conflict" size={15} /> : null}</div></td>
                  <td><div className="qa-flags">{productLifecycle !== "active" ? <span className={productLifecycle === "phaseout" ? "warn" : "error"} title={lifecycleLabel(productLifecycle)}>{productLifecycle === "phaseout" ? "DOP" : productLifecycle === "discontinue" ? "STOP" : "ARCH"}</span> : null}{product.quality.hasConflict ? <span className="error" title="Konflikt identifikátorů"><AlertTriangle size={14} /></span> : null}{product.sourceCount === 1 ? <span className="warn" title="Pouze jeden zdroj">1×</span> : null}{!product.quality.hasEan ? <span className="warn" title="Chybí EAN">EAN</span> : null}{product.finalDecision ? <span className="ok" title="Finální rozhodnutí"><ShieldCheck size={14} /></span> : null}</div></td>
                  <td><ChevronRight size={17} /></td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {!visible.length ? <div className="empty-table"><Filter size={28} /><h3>Žádný produkt neodpovídá filtrům</h3><p>Zkuste změnit značku, kategorii nebo stav.</p></div> : null}
      </div>

      <footer className="table-footer"><span>Zobrazeno {visible.length ? (props.page - 1) * pageSize + 1 : 0}–{Math.min(props.page * pageSize, filtered.length)} z {filtered.length}</span><div><button className="icon-button" disabled={props.page <= 1} onClick={() => props.setPage(props.page - 1)} title="Předchozí stránka"><ArrowLeft size={17} /></button><span>Strana {props.page} / {totalPages}</span><button className="icon-button" disabled={props.page >= totalPages} onClick={() => props.setPage(props.page + 1)} title="Další stránka"><ArrowRight size={17} /></button></div></footer>
    </section>
  );
}

function BulkBar({ selectedIds, profileId, pending, onClear, onRun }: { selectedIds: Set<string>; profileId: string; pending: boolean; onClear: () => void; onRun: (channel: string, decision: "include" | "exclude" | "hold", submit: boolean, reason?: string) => void }) {
  const [channel, setChannel] = useState("vitar.cz");
  const [decision, setDecision] = useState<"include" | "exclude" | "hold">("include");
  const [reason, setReason] = useState<(typeof INFORMATION_REASONS)[number]>(INFORMATION_REASONS[0]);
  const bulkChannels = [{ key: "both", label: "Oba e-shopy" }, ...CHANNEL_OPTIONS.filter((option) => option.key !== "workshop_hold")];
  return <div className="bulk-bar"><span><strong>{selectedIds.size}</strong> vybráno</span><button className="icon-button inverse" onClick={onClear} title="Zrušit výběr"><X size={16} /></button><i /><label>Cíl<select value={channel} disabled={decision === "hold"} onChange={(event) => setChannel(event.target.value)}>{bulkChannels.map((option) => <option value={option.key} key={option.key}>{option.label}</option>)}</select></label><label>Akce<select value={decision} onChange={(event) => setDecision(event.target.value as "include" | "exclude" | "hold")}><option value="include">Zařadit</option><option value="hold">Potřebuji informace</option><option value="exclude">Vyřadit</option></select></label>{decision === "hold" ? <label>Důvod<select value={reason} onChange={(event) => setReason(event.target.value as (typeof INFORMATION_REASONS)[number])}>{INFORMATION_REASONS.map((item) => <option key={item}>{item}</option>)}</select></label> : null}<button className="secondary-button dark" disabled={pending} onClick={() => onRun(channel, decision, false, reason)}>Uložit koncept</button><button className="primary-button light" disabled={pending} onClick={() => onRun(channel, decision, true, reason)}>{pending ? <LoaderCircle className="spin" size={16} /> : <CheckCircle2 size={16} />} Odevzdat hromadně</button><small>{profileId}</small></div>;
}

function WipDialog({ profileId, categories, onSaveFeedback, onClose }: { profileId: string; categories: Array<{ key: string; label: string }>; onSaveFeedback: SaveFeedbackHandler; onClose: () => void }) {
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("Vitar");
  const [categoryKey, setCategoryKey] = useState(categories.find((item) => item.key === "unclassified" || item.label === "Nezařazeno")?.key || categories[0]?.key || "unclassified");
  const [description, setDescription] = useState("");
  const [targetChannels, setTargetChannels] = useState<Array<"vitar.cz" | "nasevitaminy.cz">>(["vitar.cz"]);
  const [error, setError] = useState("");
  const [pending, startTransition] = useTransition();
  const router = useRouter();

  function submit(event: FormEvent) {
    event.preventDefault();
    const selected = categories.find((item) => item.key === categoryKey);
    if (!selected) return;
    setError("");
    onSaveFeedback("saving", "Ukládám nový placeholder");
    startTransition(async () => {
      try {
        await createWipProduct({
          profileId,
          name,
          brand,
          categoryKey,
          categoryLabel: selected.label,
          description,
          targetChannels,
        });
        onSaveFeedback("saved", "Placeholder trvale uložen");
        router.refresh();
        onClose();
      } catch (submitError) {
        const rawMessage = submitError instanceof Error ? submitError.message : "";
        const errorMessage = /fetch|network|load failed/i.test(rawMessage)
          ? "Připojení se přerušilo. Data zůstala ve formuláři, zkuste uložení znovu."
          : rawMessage || "Produkt se nepodařilo přidat.";
        setError(errorMessage);
        onSaveFeedback("error", errorMessage);
      }
    });
  }

  return (
    <div className="modal-layer">
      <button className="modal-backdrop" onClick={onClose} aria-label="Zavřít" />
      <form className="modal-panel" onSubmit={submit}>
        <header>
          <div><p className="eyebrow">WIP INBOX</p><h2>Přidat nový placeholder</h2></div>
          <button type="button" className="icon-button" onClick={onClose} title="Zavřít"><X size={18} /></button>
        </header>
        <p>Placeholder se trvale uloží do databáze, zůstane vedle nascrapovaného portfolia a projde stejným review.</p>
        <label><span>Pracovní název</span><input value={name} onChange={(event) => setName(event.target.value)} autoFocus /></label>
        <div className="two-column-fields">
          <label><span>Značka / řada</span><input value={brand} onChange={(event) => setBrand(event.target.value)} /></label>
          <label>
            <span>Kategorie</span>
            <select value={categoryKey} onChange={(event) => setCategoryKey(event.target.value)}>
              {categories.map((item) => <option value={item.key} key={item.key}>{item.label}</option>)}
            </select>
          </label>
        </div>
        <div className="wip-channel-field">
          <span>Cílový e-shop (povinné)</span>
          <div className="channel-grid">
            {CHANNEL_OPTIONS.slice(0, 2).map((channel) => {
              const key = channel.key as "vitar.cz" | "nasevitaminy.cz";
              const selected = targetChannels.includes(key);
              return (
                <button
                  type="button"
                  className={`channel-option ${selected ? "selected" : ""}`}
                  onClick={() => setTargetChannels((current) => selected ? current.filter((item) => item !== key) : [...current, key])}
                  key={key}
                >
                  <span className="check-box">{selected ? <Check size={14} /> : null}</span>
                  <span><strong>{channel.label}</strong><small>{channel.note}</small></span>
                </button>
              );
            })}
          </div>
          <small>Lze zvolit jeden nebo oba e-shopy. Cíl se uloží přímo k placeholderu.</small>
        </div>
        <label><span>Koncept / USP</span><textarea rows={5} value={description} onChange={(event) => setDescription(event.target.value)} /></label>
        {error ? <p className="form-error" role="alert">{error}</p> : null}
        <footer>
          <button type="button" className="secondary-button" onClick={onClose}>Zrušit</button>
          <button className="primary-button" disabled={pending || name.trim().length < 3 || targetChannels.length === 0}>
            {pending ? <LoaderCircle className="spin" size={16} /> : <Plus size={16} />} Uložit placeholder
          </button>
        </footer>
      </form>
    </div>
  );
}
