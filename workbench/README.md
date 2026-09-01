# VITAR Assortment Workbench

Internal decision workspace for splitting the current VITAR portfolio between
`VITAR.cz`, `NaseVitaminy.cz`, separate business units and archive. It combines a
fresh source audit with independent reviewer sessions, mobile swipe review,
consensus tracking and a facilitator-owned final decision.

## Current scope

- Crawl completed on 1 September 2026.
- 865/865 sitemap URLs inventoried with 0 crawl errors.
- 567 source product profiles normalized into 341 safe master products.
- Sources: 262 VITAR.cz, 298 NaseVitaminy.cz and 7 Ceske-vitaminy.cz profiles.
- Exact EAN/SKU and guarded name matching; ambiguous identifiers stay separate.
- Product source content, source conflicts and decision history remain auditable.

## Review workflow

1. The facilitator opens `Team and invites`, enters a name and e-mail, and copies
   the generated personal link.
2. The link creates a signed 14-day session for exactly one reviewer. Every vote,
   note and edit is attributed to that profile.
3. Reviewers complete their homework independently on desktop or mobile. Other
   product opinions are hidden until their own opinion is submitted.
4. Mobile quick review supports right = VITAR.cz, left = NaseVitaminy.cz, up =
   both, down = hold, plus separate actions for Veterina and archive. Doprodej
   and manufacturing discontinuation are recorded as a separate lifecycle decision.
5. The facilitator uses Conflicts and Final Matrix during the workshop and records
   the approved channel, category, portfolio role, confidence and rationale.
6. Final or full data can be exported as JSON or CSV for development and PIM.

The shared access code is a facilitator bootstrap only. Team members should use
personal invite links so they cannot accidentally vote under somebody else's name.
The application generates links but does not send e-mail automatically.

## Architecture

- Next.js App Router and React
- Neon Postgres provisioned through Vercel
- Drizzle ORM schema and migration tooling
- Signed HMAC profile and invite cookies
- Vercel for the application; GitHub Pages remains the static report archive
- Monorepo root: `jurajgiacko/vitarecommerce`, Vercel root directory: `workbench`

## Local setup

```bash
npm install
npm run db:push
npm run db:seed
npm run dev
```

Copy `.env.example` to `.env.local` and populate the values locally. Vercel owns
the production values.

```bash
npm run data:crawl
npm run lint
npm run build
```

The crawler writes compact committed outputs to `data/current/` and
`src/data/catalog.json`. Downloaded HTML in `data/raw/` is intentionally ignored.

## Data governance

Never merge products only because their normalized names match when identifiers
conflict. A final channel decision is separate from individual proposals. WIP
products are visibly marked and require identifiers, content and commercial data
before platform import.
