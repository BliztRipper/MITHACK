<!-- Hallmark · genre: modern-minimal (clinical instrument) · macrostructure: Workbench (app scope: the image is the work surface) · theme: custom "ward-lit slate" · nav: N3 side-rail · footer: none (app) · enrichment: none -->
# Design direction: Group 6 web app

Written before any UI code exists. Implementers apply it mechanically. If a rule here conflicts with a spec, the spec wins; tell the design owner.

Inferred context (the brief came from the team lead, not a design interview): **audience** = frontline GPs and ED doctors in Thai hospitals who are not ophthalmologists, plus an ophthalmologist reviewer and an admin. **Use** = get from a fundus photo to a defensible next action, then sign it. **Tone** = utilitarian, technical, calm.

## 1. Stance

This is an instrument, not a product page. A GP at 3 a.m. with a patient who has lost vision in one eye needs the next action, its reasons, and proof that it is still preliminary, in one look. Everything else stays quiet. The chrome is cool slate and recedes. The fundus photo sits on a dark stage, like a light box, so its red-orange is the only warm colour in its region and the overlays read against it. Colour is kept for clinical meaning. Only STROKE_PATHWAY gets a solid red surface. Lower levels step down in fill weight (solid, then tint, then outline), so the screen does not shout when the case is routine. Every clinical state is carried by text, plus an icon or a border style, plus colour, and never by colour alone. Numbers, thresholds, versions and rule reasons are set in a monospace face because they are evidence and should look like evidence. The UI is in English. The Thai patient summary is set in a looped Thai face that older patients read easily.

## 2. Tokens

Target **Tailwind v4** (`@tailwindcss/vite`, CSS-first config). Paste this into `app/web/src/index.css` below `@import "tailwindcss";`. If the scaffold ends up on Tailwind v3, put the same names under `theme.extend` (`colors.triage.stroke`, etc.). The class names stay the same.

Values are sRGB hex so the contrast table is exact. They were derived from OKLCH (hue 250 slate anchor) and gamut-clamped.

```css
@theme {
  /* ---- neutrals: cool slate, never #000/#fff ---- */
  --color-paper: #f6f9fb;          /* app background */
  --color-surface: #fcfdfe;        /* cards, dialogs, inputs */
  --color-sunken: #edf0f4;         /* table zebra, disabled fill, wells */
  --color-rule: #d4d8dd;           /* decorative dividers only (not a UI boundary) */
  --color-rule-strong: #6e757d;    /* input/checkbox borders, toggles: >=3:1 */
  --color-muted: #515961;          /* secondary text */
  --color-ink: #141b24;            /* primary text */

  /* ---- image stage (light box) ---- */
  --color-stage: #0e1216;
  --color-stage-ink: #e5e8ec;
  --color-stage-muted: #a6abb1;

  /* ---- action accent (links, primary buttons, selected nav) ---- */
  --color-accent: #155aa7;
  --color-accent-tint: #e2eefe;
  --color-focus: #005ccc;          /* focus ring on light surfaces */
  --color-focus-dark: #67d2ff;     /* focus ring on the stage */

  /* ---- triage levels: solid / fg / tint ---- */
  --color-triage-stroke: #a00f15;
  --color-triage-stroke-fg: #941617;
  --color-triage-stroke-tint: #ffeae7;
  --color-triage-urgent: #8f4700;
  --color-triage-urgent-fg: #773a00;
  --color-triage-urgent-tint: #ffecd4;
  --color-triage-escalate: #5d4099;
  --color-triage-escalate-fg: #573d8e;
  --color-triage-escalate-tint: #f1edff;
  --color-triage-retake: #414f5d;
  --color-triage-retake-tint: #ebeff4;
  --color-triage-routine: #185d49;
  --color-triage-routine-tint: #e3f5ee;

  /* ---- CRAO probability bands ---- */
  --color-band-unlikely: #414f5d;  /* = retake slate: neutral, not "green = safe" */
  --color-band-uncertain: #7b5100;
  --color-band-likely: #a00f15;

  /* ---- 10-year ASCVD risk (PCE), ordinal 1..4 (ACC/AHA bands) ---- */
  --color-risk-1: #eedacb;         /* ink text on it */
  --color-risk-2: #e0b491;         /* ink text */
  --color-risk-3: #c16d45;         /* ink text, >=18.66px bold only (4.54:1) */
  --color-risk-4: #97271b;         /* paper text */

  /* ---- result status ---- */
  --color-status-preliminary: #704500;
  --color-status-preliminary-tint: #fdf1d0;
  --color-status-preliminary-border: #9a6a17;
  --color-status-final: #141b24;   /* = ink; paper text on it */

  /* ---- system / monitoring ---- */
  --color-system-warn-tint: #fbe9c6; /* IRIS-down banner, drift alerts */
  --color-system-ok: #185d49;

  /* ---- overlays (on the stage, over the fundus; see §3.7) ---- */
  --color-overlay-vessel: #eef3f8;   /* near-white filaments */
  --color-overlay-artery: #ffd23f;   /* yellow */
  --color-overlay-vein: #5aa0ff;     /* sky blue */
  --color-overlay-disc: #ffffff;     /* dashed ring (SVG), not a fill */
  --color-overlay-heatmap: #22d3ee;  /* single-hue cyan, intensity = alpha */

  /* ---- type ---- */
  --font-sans: "IBM Plex Sans", "IBM Plex Sans Thai", system-ui, "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
  --font-thai: "IBM Plex Sans Thai Looped", "IBM Plex Sans Thai", "Leelawadee UI", Thonburi, "Noto Sans Thai", sans-serif;

  --text-xs: 0.75rem;   --text-xs--line-height: 1rem;      /* meta only, never clinical content */
  --text-sm: 0.875rem;  --text-sm--line-height: 1.25rem;   /* table cells, captions */
  --text-base: 1rem;    --text-base--line-height: 1.5rem;  /* body, form labels */
  --text-lg: 1.125rem;  --text-lg--line-height: 1.75rem;   /* action lists in the triage card */
  --text-xl: 1.375rem;  --text-xl--line-height: 1.75rem;   /* page titles, panel titles */
  --text-2xl: 1.75rem;  --text-2xl--line-height: 2.125rem; /* triage level, headline risk % */
  --text-3xl: 2.25rem;  --text-3xl--line-height: 2.5rem;   /* gauge readout only */

  /* ---- shape ---- */
  --radius-sm: 3px;   /* badges, chips */
  --radius-md: 5px;   /* buttons, inputs */
  --radius-lg: 8px;   /* cards, dialogs */
  /* the fundus image and stage are NEVER rounded: radius 0 */

  --shadow-pop: 0 1px 2px rgb(14 18 22 / 0.08), 0 8px 24px rgb(14 18 22 / 0.14); /* dialogs, menus only */
  --shadow-halo: drop-shadow(0 0 0.75px rgb(0 0 0 / 0.9)) drop-shadow(0 0 0.75px rgb(0 0 0 / 0.9)); /* overlay filter */
}
```

**Spacing:** use Tailwind's default 4 px scale (`--spacing: 0.25rem`). Allowed steps are 1, 2, 3, 4, 6, 8, 12 and 16. Form rows are `gap-4`, sections inside a card are `gap-6`, and gutters between page regions are `gap-8`. Content max-width is `max-w-[1440px]`, and the result view uses all of it.

**Fonts are self-hosted (offline demo):** `npm i @fontsource/ibm-plex-sans @fontsource/ibm-plex-sans-thai @fontsource/ibm-plex-sans-thai-looped @fontsource/ibm-plex-mono` (all v5.3.0 on npm). Import only weights 400, 500 and 600 (Plex Mono: 400 and 500) in `main.tsx`. Vite bundles the woff2 files. Never add a `<link>` to Google Fonts. Plex Sans Thai sits in the UI stack, so a Thai name typed into the patient list renders in a matching face. Thai text gets `leading-[1.7]` (`.font-thai` blocks), because stacked vowels and tone marks clip at 1.5. Numbers use `font-mono tabular-nums` or `font-sans tabular-nums` inside tables.

**Focus:** a global rule, never animated:
`*:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px; }` and, inside `.stage`, `outline-color: var(--color-focus-dark)`. Never `outline: none` without this replacement.

### Contrast table (WCAG 2.x, computed from the hex values above)

| Pair (fg on bg) | Ratio | Use | Passes |
|---|---|---|---|
| ink on paper / surface / sunken | 16.3 / 17.0 / 15.2 | all body text | AAA |
| muted on paper / surface / sunken | 6.7 / 7.0 / 6.2 | secondary text | AA |
| rule-strong on paper / surface | 4.4 / 4.6 | input and toggle borders | AA non-text (3:1) |
| accent on paper / paper on accent | 6.5 / 6.5 | links / primary button | AA |
| accent on accent-tint | 5.9 | selected nav item | AA |
| focus on paper / surface | 5.8 / 6.0 | focus ring | 3:1 |
| focus-dark on stage | 11.0 | focus ring on the image | 3:1 |
| stage-ink / stage-muted on stage | 15.3 / 8.2 | labels over the image well | AAA |
| paper on triage-stroke | 7.7 | STROKE_PATHWAY solid card | AAA |
| triage-stroke-fg on stroke-tint | 7.6 | stroke badge in rows | AAA |
| triage-urgent-fg on urgent-tint | 7.6 | URGENT card text | AAA |
| triage-urgent on urgent-tint | 5.9 | URGENT border and icon | AA |
| triage-escalate-fg on escalate-tint | 7.5 | ESCALATE badge | AAA |
| triage-retake on retake-tint | 7.3 | RETAKE badge | AAA |
| triage-routine on routine-tint | 6.9 | ROUTINE badge | AA |
| band-uncertain on paper | 6.6 | gauge label | AA |
| status-preliminary on preliminary-tint | 7.4 | PRELIMINARY badge | AAA |
| status-preliminary-border on preliminary-tint | 4.2 | dashed border | 3:1 |
| paper on status-final (ink) | 16.3 | FINAL badge | AAA |
| ink on risk-1 / risk-2 | 12.8 / 9.1 | risk segment labels | AAA |
| ink on risk-3 | 4.5 | risk label, 600 weight ≥ 18.66 px only | AA large |
| paper on risk-4 | 7.6 | highest-risk segment | AAA |
| ink on system-warn-tint | 14.5 | IRIS banner, alert rows | AAA |

Overlay colours against the fundus (sampled mid-orange `#b85a2a`, dark periphery `#4a1a0c`): vessel 4.2 / 13.0, artery 3.2 / 10.1, vein 1.7 / 5.5, heatmap 2.6 / 8.1. Vein and heatmap are weak on the mid-orange, so every overlay layer gets the `--shadow-halo` dark 0.75 px outline (`filter`), which follows the PNG alpha and separates the layer from any fundus colour, including the bright disc.

## 3. Component rules

Icons are `lucide-react` (bundled, offline), 20 px in rows and 24 px on cards, `stroke-width 2`, and always beside a text label. The names are lucide names, not verified against the installed version. If one is missing at import, use the closest icon of the same shape (octagon, triangle, camera, …). Never use an icon-only button without `aria-label` and a visible tooltip on focus.

### 3.1 Triage and status vocabulary (used everywhere)

| Level | Label text | Icon (lucide) | Weight on result view | Badge in rows |
|---|---|---|---|---|
| STROKE_PATHWAY | STROKE PATHWAY | `OctagonAlert` | **solid** `bg-triage-stroke text-paper` | tint + fg + 2 px solid border |
| URGENT | URGENT | `TriangleAlert` | **tint** `bg-triage-urgent-tint`, 2 px border `triage-urgent` | tint + fg |
| ESCALATE | ESCALATE: specialist review | `UserRoundSearch` | **outline** `bg-surface`, 2 px border `triage-escalate` | tint + fg |
| RETAKE | RETAKE PHOTO | `Camera` | outline, 2 px **dashed** border `triage-retake` | tint + fg, dashed |
| ROUTINE | ROUTINE | `CalendarClock` | outline, 1 px border `rule-strong` | tint + fg |

ROUTINE deliberately has no check mark or green "all clear", because a normal-looking photo does not reassure (spec). The machine code (`STROKE_PATHWAY`) also appears in `font-mono text-xs text-muted` under the label for traceability.

Status badge, always top-right of any result, queue row or report header:
- **PRELIMINARY**: `bg-status-preliminary-tint text-status-preliminary border-[1.5px] border-dashed border-status-preliminary-border`, icon `FilePen`, text `PRELIMINARY · AI-assisted, not a diagnosis`. The dashed border is the non-colour cue.
- **FINAL**: `bg-status-final text-paper`, solid, icon `FileCheck2`, text `FINAL · signed by {name}, {time}`.
- **AMENDED**: the FINAL style plus `· amended` and a link to history.

### 3.2 App shell and role nav (N3 side-rail)

- Left rail, `w-56`, `bg-surface border-r border-rule`, full height. Top: wordmark text "Retina CVD/CRAO" (`font-semibold text-base`, no logo mark). Below it are role-filtered links: **gp** gets Patients, New case and Review queue (own). **reviewer** gets the same plus the escalated cases in the queue and Monitoring. **admin** gets Monitoring and Audit. **About** shows for all roles, last. The menu is built from `GET /auth/me` role and never shows a link that would 403.
- Active link: `bg-accent-tint text-accent font-medium` plus `aria-current="page"`. Inactive: `text-ink hover:bg-sunken`. The text label is always visible. No collapsed icon-only rail.
- Rail bottom: user name, role chip (`text-xs uppercase tracking-wide text-muted`), Sign out.
- The main area is `bg-paper`, with a page title `text-xl font-semibold` and no breadcrumbs except in the wizard. No top bar except the IRIS banner.
- Below 1024 px the rail collapses to a top bar with a menu button (the demo is desktop, but nothing may overflow at 768).

### 3.3 IRIS-down banner

- Poll `GET /health` at start-up, every 30 s and after any 503. Show the banner when `record_store === "unavailable"`.
- Full width, above everything (outside the rail), `bg-system-warn-tint text-ink border-b-2 border-triage-urgent`, `role="status"` with `aria-live="polite"`. Icon `DatabaseZap`. Text: **"Record store unavailable. Results still display, but nothing can be saved or signed until it is back."** Not dismissible. It disappears on its own when health recovers.
- While it is shown: Save and Sign buttons are disabled with the visible reason "record store unavailable", not just greyed out. A result with `saved:false` shows `save_error` inline in the result header in the same banner style.
- On the consent check, a 503 is a hard stop (fails closed): the wizard shows "Cannot verify consent while the record store is down. Analysis is blocked." No bypass.

### 3.4 Patient list row

- Use a semantic `<table>`, not cards. Columns: HN (`font-mono`), Name (Thai or Latin, as stored), Sex, Date of birth / age, Last case (date · mode · level badge), Consent (words, not ticks: "care: yes · model use: no").
- Row height 48 px, `border-b border-rule`, `hover:bg-sunken`. The whole row is one link to the patient (`<a>` in the name cell, plus row click). The name cell gets the focus ring.
- The search field sits above the table: one input, label "Search name or HN", submits on Enter (POST /patients/search). Empty state: "No patient matches '{q}'." No illustration.

### 3.5 Consent gate

- This is a wizard step, not a modal. When consent is missing, it shows a bordered `surface` panel titled **"Consent required before analysis"**, with the PDPA reason in one sentence.
- Form: `Care use` (required checkbox), `Use for model improvement` (optional, unchecked by default, with a separate sentence that refusing changes nothing about care), `Retention (years)` number ≥ 1, and `Right to withdraw explained to patient` (required checkbox). These are native checkboxes, 20 px, with `rule-strong` borders and the label on the right. The label is clickable.
- The primary button "Record consent and continue" stays disabled until the required boxes are ticked, with the reason listed under the button ("Tick: care use, right to withdraw").
- When consent exists, the step shows a one-line confirmation ("Consent on file: care yes, model use no") and an Edit link. It does not auto-skip silently.

### 3.6 Wizard steps

- Horizontal step list at the top: `Mode → Consent → Inputs → Photo → Result`. Each step is number + label. Current: `text-ink font-semibold` with a 2 px `accent` underline. Done: `text-muted` with `Check`. Future: `text-muted`. This is an ordered list with `aria-current="step"`, and done steps are links back.
- **Mode** is two large selectable panels (radio group, not buttons): "Screening: 10-year CVD risk" and "Emergency: sudden vision loss". The Emergency panel has a `TriangleAlert` icon and the line "Use for sudden, painless loss of vision in one eye". Selection = 2 px `accent` border + `accent-tint` background + `Check`.
- **Inputs:** a two-column form at ≥ 1024 px (label above input, `text-base`). Units sit inside the field suffix (`mmHg`, `mg/dL`). Pre-filled values show their source date under the field: `text-sm text-muted` "from record, 12 Mar 2026". Out-of-range errors appear under the field in `text-triage-stroke-fg` with the `CircleAlert` icon and name the range ("Accepted 60–260 mmHg"). Errors also go to `aria-describedby`. Emergency inputs: onset hours (number, plus an "Onset unknown" checkbox that clears and disables it), "Sudden, painless, one eye?" (yes/no radio), and "Jaw claudication, scalp tenderness, or new headache (GCA symptoms)?" (yes/no radio). Never default these radios to an answer.
- Footer bar: Back (secondary) on the left, Continue (primary) on the right. The primary button is `bg-accent text-paper rounded-md h-10 px-4 font-medium`. Secondary is `bg-surface border border-rule-strong text-ink`. Disabled is `bg-sunken text-muted border-rule` plus a visible reason.

### 3.7 Upload with quality result and retake reason

- Drop zone: `border-2 border-dashed border-rule-strong bg-surface rounded-lg`, a real `<input type=file accept="image/jpeg,image/png">` with a visible "Choose fundus photo" button. Drag-and-drop is an extra, not the only path. State the limit: "JPEG or PNG, up to 20 MB".
- Demo cache images appear as a row of named thumbnail buttons below ("Cached: RAO example", "Cached: screening example", "Cached: poor quality"), with text labels.
- While analysing: the button reads "Analysing…" with a spinner, the input is disabled, and the step list stays visible.
- **Quality failed (RETAKE):** the photo is shown on the stage at reduced size, next to a RETAKE card (dashed border). It lists every `quality.reasons` entry as a sentence ("Image too dark", "Image out of focus") with the score `font-mono` ("quality 0.31, below threshold (placeholder)"). In Emergency mode the urgent-referral fallback line is always shown, in `text-lg font-medium`: "If a gradable photo cannot be taken within minutes, refer urgently. Do not delay." Primary action: "Retake photo".
- Quality passed: the score appears as a chip on the result header ("quality 0.82, passed"). There is no celebration.

### 3.8 Result view (the hero)

Layout at ≥ 1280 px: a two-column grid `grid-cols-[minmax(0,1fr)_420px] gap-8`. **Left is the stage (image), right is the decision column** (status badge, triage card or risk panel, explanation, Sign button). Below 1280 the columns stack, with the decision column **first** in source and visual order, because the action matters more than the picture on a small screen.

Result header (full width above the grid): patient name, HN, mode, time, then on the right the status badge (3.1) and the "AI-assisted, not a diagnosis" label. The header is sticky, so PRELIMINARY never scrolls out of view.

**Stage:** `bg-stage p-4`, square corners. The image box is `relative aspect-square max-h-[78vh] mx-auto`. Layers are stacked `absolute inset-0 w-full h-full object-contain`, in this order:
1. the fundus `<img>` (base, never filtered)
2. vessel layer
3. artery/vein layer
4. heatmap layer (Emergency only)
5. optic-disc ring: an `<svg>` circle from `segmentation.disc_centre` and `disc_diameter`, scaled with `viewBox` set to the image's natural size, `stroke: var(--color-overlay-disc)`, `stroke-width` 2 (non-scaling), `stroke-dasharray 6 4`, with a "Disc" text label. When `disc_found` is false, draw no ring and show "Optic disc not located; region-based explanation omitted" in the layer panel.

Recolouring the PNGs without canvas: the vessel and heatmap layers are `<div>`s with `background: var(--color-overlay-*)` and `mask: url(data:image/png;base64,…) center/contain no-repeat` (plus `-webkit-mask`). The PNG's alpha becomes the shape and intensity, and the token supplies the colour. The heatmap is therefore single-hue cyan, with opacity carrying intensity. That replaces the backend JET rainbow, which is not colour-blind safe and fights the fundus. Artery/vein holds two colours in one PNG, so it cannot be recoloured this way. **Backend follow-up (one line):** `app/api/vision/segment.py` `COLOURS` artery → `(255, 210, 63)`, vein → `(90, 160, 255)`. Until then, A/V renders with the backend red/blue. Every overlay element gets `style={{filter: 'var(--shadow-halo)'}}`.

**Layer panel** (under the image, still on the stage, `text-stage-ink`):
- "Vessels" is a 3-way segmented radio: `Off · All vessels · Artery / vein`. They are mutually exclusive, so near-white and blue are never stacked.
- "Optic disc" and "Model attention (heatmap)" are switches (`role="switch"`, visible On/Off text).
- Each control has a 12 px legend swatch drawn in the layer colour **and** a pattern word ("filaments", "dashed ring", "glow").
- One opacity slider, "Overlay opacity", a native `<input type=range>` 0–100, step 5, default 70, value shown as "70 %". It applies to all overlay layers. The base image is never dimmed.
- Whenever the heatmap is on, a non-dismissable caption sits directly under the image, `text-sm text-stage-ink` with `Info` icon: **"Heatmap shows model attention, not lesions."** It is also printed.
- **Compare** button (`Columns2` icon) toggles side-by-side: two equal stage panes, left "Original (unaltered)" with no layers ever, right "With layers", same size and both labelled. Esc or the same button exits. Default for Emergency is single view with the heatmap on. Default for Screening is single view with vessels on "Artery / vein".

Keyboard: every control is in tab order (radios with arrow keys). `1/2/3` shortcuts are optional extras, not required.

### 3.9 Band gauge (Emergency)

- A horizontal bar, 100 % wide, 16 px tall, split at `p_low` and `p_high` into three segments. Each segment has its text label printed **inside or under it** ("unlikely", "uncertain", "likely"). Unlikely is a `sunken` fill, uncertain is `band-uncertain` **diagonal hatch** (`repeating-linear-gradient` 45°, 2 px lines over tint; this is a pattern, not decoration), and likely is a `band-likely` solid fill. The hatch keeps the three distinguishable in greyscale and print.
- Marker: a downward triangle plus a 2 px line at `p`, with a readout above it, `font-mono text-3xl`: `p = 0.82`. Next to it, the band word as text in `text-2xl font-semibold` in the band colour: **likely**.
- Threshold ticks show `p_low` and `p_high` from the case result (e.g. `0.30`, `0.70`), with a `placeholder` chip (`text-xs border border-dashed border-rule-strong text-muted`), always visible.
- Under the gauge, one `text-sm text-muted font-mono` line: `{model} {version} · calibrated {calibration_date}`. This line is mandatory beside every probability.
- No model: the gauge is replaced by a `sunken` box: "No model loaded. Probability not available. Case routed to ESCALATE."
- Uncertain band: the line "Not a positive or negative finding. Specialist review recommended." appears under the band word.

### 3.10 Triage card

- This is the first thing in the decision column. The level row has the icon at 24 px, the label in `text-2xl font-semibold uppercase tracking-wide`, and the code in mono below it. The fill weight follows the table in 3.1. The STROKE_PATHWAY card is the only solid red element in the whole app.
- **Actions:** an ordered list, `text-lg`, numbered. Item 1 is `font-semibold`, because it is the first action. For STROKE_PATHWAY, action 1 includes the sentence "thrombolysis benefit for CRAO is uncertain; follow local protocol" in the same weight, not as small print. The GCA arteritis action, when present, is item 1 with the icon `Pill` and no stroke-team line anywhere. The secondary-prevention reminder is always last.
- **Reasons:** a `<dl>` titled "Why this level", `font-mono text-sm`, one rule input per line (render `triage.reasons` verbatim, e.g. `p=0.82 ≥ 0.70`, `onset 2.0 h ≤ 4.5 h`). Thresholds in reasons carry `(placeholder)`. Always expanded. Never a disclosure or tooltip.
- **Limitations** block, always visible below the reasons, `text-sm text-ink` on `sunken`, `Info` icon: "Trained on established (not hyperacute) artery occlusions. An early CRAO can look normal on a fundus photo."
- Inside the card, all text on solid stroke red is `text-paper`, and chips become `border-paper/70` outlines.

### 3.11 Risk panel (Screening)

- The headline is **PCE 10-year ASCVD risk**: a label ("10-year ASCVD risk (PCE)") above `font-mono text-3xl` `14.2 %`, with "10-year" and the band name as text. A 4-segment ordinal bar uses `risk-1…4`, each labelled with its ACC/AHA range (`<5 %`, `5–<7.5`, `7.5–<20`, `≥20`), and the patient's segment has a 2 px `ink` outline plus a triangle marker. Outside 40–79: show "outside validated age range (40–79)" in place of the number, with no bar.
- The caveat sits directly under the number, `text-sm text-muted` and never collapsed: "PCE was not derived in Asian populations and may overestimate risk."
- **Statin group:** when the patient is in a 2018 AHA/ACC statin benefit group (known ASCVD, LDL ≥ 190, diabetes 40–75 with LDL ≥ 70), a bordered statement names the group and says the indication holds regardless of calculated risk. Any PCE number shown then informs statin intensity only.
- **Bypass** (known ASCVD or LDL ≥ 190): this replaces both numbers with a bordered statement, `text-lg font-medium` ("Secondary prevention: risk calculators do not apply"). No suggestion is shown.
- **Enhancers:** a list with source tags ("retinal", "clinical"). The fixed line "Enhancers do not change the calculated risk" always shows. "Retinal enhancers not assessed (image failed quality)" shows when relevant.
- **Measurements:** a small table of AVR, CRAE and CRVE with value (mono), reference interval, flag word ("within reference" / "outside reference"), and a `placeholder` chip on the reference.
- **Suggestion:** a box labelled "For clinician–patient discussion", `bg-surface border border-rule`, never styled as an instruction. Stage 1 HTN and arcus prompts are separate one-line notes with `Info`.

### 3.12 Explanation block

- Title "What the model looked at". The `explanation.sentences` render as a paragraph, `text-base`, `max-w-[65ch]`. The named region (macula, optic disc, …) is `font-semibold`. The last sentence always asks the clinician to confirm on the image.
- When `region` is null (disc not found), the block says so in one sentence and does not guess.
- No AI sparkle icon, no "insight" styling. It looks like a dictated note.

### 3.13 Sign / override dialog

- A native `<dialog>` (modal) with `bg-surface rounded-lg shadow-pop w-[560px]`. Focus moves to the first control and is trapped. Esc cancels. The title is "Sign result". A read-only summary at the top repeats the AI level/band and the model version, so the clinician signs what they see.
- **Decision:** a radio pair, each option a full-width bordered row: "Confirm AI result" and "Override with my finding".
- Override reveals: **Finding** (text, required), **Reason** (radio list: image misread · clinical findings disagree · poor image · other), and **Details** (textarea, required when "other"). Whitespace-only counts as empty.
- **Emergency only, always shown, required, no default:** "Clinician assessment: is this CRAO?" as a radio pair `Yes, CRAO` / `No, not CRAO` (`crao: true/false`). Helper text: "Used to check model calibration."
- The Sign button stays disabled until the form is valid, and the missing items are listed above it in `text-triage-stroke-fg` ("Choose a reason for the override"). A server 422 maps to the same inline list. It is never a toast.
- Signing is the one irreversible action, so the button reads "Sign as final" and there is no second confirmation dialog. Amend exists afterwards.
- While IRIS is down, the dialog cannot open. The button shows the reason (3.3).

### 3.14 Review queue row

- A table, sorted Emergency first then by waiting time. **Do not re-sort client-side.** Columns: Level badge (3.1), Mode (word), Patient (name + HN mono), Waiting (`font-mono tabular-nums`, "32 min"), Conclusion (truncated to one line with `title`), Status badge.
- Emergency rows put the mode word "EMERGENCY" in `font-semibold`. No row-wide red fill, because the badge carries it (prevents alarm fatigue in a long list). Escalated rows for a reviewer get the escalate badge plus "escalated to you".
- Waiting > 30 min on an Emergency row adds a `Clock` icon and the time in `text-triage-urgent-fg font-semibold`.

### 3.15 Monitoring tiles and alert rows

- The top bar holds a period select (7/30/90 days) and the current model version (mono).
- Metrics are a responsive grid of plain tiles (`border border-rule rounded-lg bg-surface p-4`), each holding a label, a value in `font-mono text-2xl`, and **"n = 47"** always beside the value. Per-version values go in a small table inside the tile, not one tile per version. The tiles are: cases by mode, quality rejection rate, uncertain-band rate, agreement rate, override reasons (horizontal bars with text values), and triage level distribution (bars that use the level badge labels, not colours alone).
- Rates with a configured limit draw a limit tick on a thin bar, with `placeholder` when unvalidated.
- **Calibration panel:** below 30 cases, the whole panel is a dotted-border `sunken` box: **"Insufficient data (12 of 30)"** plus one line on why. No empty chart.
- **Alert rows:** `bg-system-warn-tint` rows with a `TriangleAlert` icon, the metric, the value against its limit (mono), the opened time, and an "Acknowledge" button that opens an inline note field (required). The agreement-rate alert text names automation bias: "Agreement above 98%: review for rubber-stamping." Acknowledged rows move to a collapsed "Acknowledged" list.
- **Incidents:** same row style, with `Flag` icon, description, case link and "Close" with a note.

### 3.16 About panel

- A page, not a modal. It has three sections: Thresholds, Model, Limitations.
- **Thresholds** is a table: name, value (mono), unit, status. Status renders as a chip: `placeholder, not clinically validated` (dashed border, `status-preliminary` colours) or `validated` (solid ink). Every placeholder is visible at once, with no expand.
- **Model** is a `<dl>` with identifier, version, calibration date, training data and backbone, plus a link "Model card" to `docs/model-card.md`. With no model it reads "No model loaded".
- **Limitations** is a bulleted list, including the hyperacute limitation and the PCE population caveat.

### 3.17 Print report (A4, black-and-white safe)

- `@media print` plus `@page { size: A4; margin: 14mm 14mm 16mm; }`. Hide the rail, banner, buttons and layer panel. The body is `font-sans 10.5pt/1.4`, ink on white (the print exception to the no-#fff rule), with no backgrounds except the fundus.
- The image prints **with the overlays that were visible at signing**, at 90 mm square, with `print-color-adjust: exact` on the stage only and a caption listing the visible layers, plus the heatmap caption when it was on. The side-by-side compare does not print.
- In print, triage and status survive without colour: the STROKE_PATHWAY card prints as a 3 pt black border plus the icon and label, URGENT 2 pt, ESCALATE 1.5 pt, RETAKE dashed and ROUTINE 1 pt. The gauge keeps its hatch and segment labels. A preliminary print carries "PRELIMINARY · NOT A FINAL REPORT" in the header of every page (no diagonal watermark across the image).
- Section order (spec): patient identifiers · mode · image · quality score · AI outputs with model version · triage or risk results (with reasons and limitations) · clinician decision (who, when, confirm/override, reason) · AI-assisted disclosure · Thai/English patient summary. Use `break-inside: avoid` on each section. The footer carries the page number and the report ID in mono.
- **Patient summary:** a separate printable block, `font-thai text-[12pt] leading-[1.7]` for Thai, at most 2 short sentences plus the "when to seek emergency care" sentence in **bold**. The EN/TH language toggle is a 2-way segmented control (`ภาษาไทย / English`), and the Thai label itself is in the Thai font.

## 4. Anti-slop checklist (applied to this app)

- [ ] No gradients anywhere except the uncertain-band hatch (a pattern for meaning) and the mask-rendered heatmap. No purple-blue hero, no gradient text, no "AI glow", no sparkle icon on AI output.
- [ ] No landing page, marketing hero or "Welcome to…" splash. Login is a centred form on paper with the app name and one line on what it is for.
- [ ] No card-in-card. The result view has one containment layer per block, and the triage card is not inside another card.
- [ ] No side-stripe cards (thick coloured left border). Triage weight comes from fill and full-perimeter border thickness only.
- [ ] No pill-everything. Radii are 3/5/8 px, and the medical image is square-cornered.
- [ ] No colour-only signals: every level, band, status, alert and flag has a text label and an icon or border pattern. Check with the devtools deuteranopia/protanopia emulation and a greyscale print preview.
- [ ] No hidden clinical info: placeholders, limitations, PCE caveat, the heatmap caption and reasons are never in tooltips, accordions or "more" links.
- [ ] No toasts for errors or results. Errors are inline and next to the cause. Silent success on save, plus the status badge changes.
- [ ] No invented numbers in empty states, demos or screenshots. "Insufficient data (n of 30)" beats a fake chart.
- [ ] No emoji, stock imagery, illustrations or avatars. The only image is the patient's fundus.
- [ ] No Inter/Roboto default, no italic headings, no fake browser/phone chrome around the fundus.
- [ ] No pure `#000` / `#fff` on screen (print excepted), and no zero-chroma greys.
- [ ] Every interactive element has default · hover · focus-visible · active · disabled (with reason) · loading · error · success states. Focus rings never animate.
- [ ] No horizontal scroll at 320 / 375 / 768 px. Image grid tracks use `minmax(0,1fr)`, and buttons never wrap to two lines.

## 5. Motion targets (for the later animate pass; list only)

All under `prefers-reduced-motion: reduce`, collapse to instant or ≤ 150 ms opacity.

1. **Result arrival:** the triage card or risk headline appears first, then the overlays fade in on the stage, which shows that the decision does not depend on looking at the heatmap.
2. **PRELIMINARY → FINAL:** after signing, the status badge changes its border from dashed to solid. This is the one moment that confirms a clinician took ownership.
3. **Gauge marker:** the marker travels from 0 to `p` once, so the eye lands on the position relative to the thresholds.
4. **Layer toggle and opacity:** a short crossfade on each layer (≤ 120 ms), so the clinician sees what a layer adds.
5. **IRIS banner enter/exit:** a slide from the top edge, so a recovered store is noticed and not missed.
