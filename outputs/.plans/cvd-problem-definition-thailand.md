# Plan: CVD problem definition (5 Ws) for the Siriraj x MIT Agentic Healthcare Hackathon, Thailand

Slug: `cvd-problem-definition-thailand`
Date: 2026-10-16
Context: Hackathon "Agentic Healthcare: From Models to Trustworthy Medicine", Cardiovascular Diseases track (heart, stroke, PAD). Guiding question: detect risk earlier, respond faster, prevent CVD before it begins. Deliverable must be **problem-first** (5 Ws plus a human-scale problem pitch), not solution-first.

## Key questions
1. **What**: How big is the CVD burden (global and Thailand) across IHD, stroke, PAD? Which specific gaps in the care continuum (risk detection, emergency response, secondary prevention) cause the most avoidable deaths and disability in Thailand?
2. **What if not fixed**: What are the trends and projections (ageing society, rising hypertension, diabetes, obesity), and what are the costs (catastrophic spending, productivity loss)?
3. **What if fixed**: What evidence quantifies gains from better BP control, faster reperfusion (time is brain/muscle), AF detection, PAD detection, and adherence?
4. **Current solutions and shortcomings**: Thai NCD screening (NHSO/UCS), village health volunteers (อสม./VHV), Thai CV risk score, stroke fast track/stroke units, STEMI networks, 1669 EMS, telemedicine, AI-ECG, wearables, and what each misses.
5. **Who**: which populations (rural, elderly, low-SES, men vs women, post-stroke/MI patients, caregivers, VHVs, community hospital clinicians)?
6. **When**: life-course timing (silent risk years, symptom onset to door, post-discharge first 30-90 days), and urgency (Thailand aged society timeline, WHO/SDG 3.4 2030 targets).
7. **Where**: rural vs urban, community hospitals without PCI/CT, home, regional gaps.
8. **Why**: rationale and hackathon fit (agentic AI, trustworthiness).

## Evidence needed
- WHO / GBD / World Heart Federation global numbers; Thai MOPH / DDC / NHES / Thai Stroke Society / Thai ACS Registry numbers.
- Thai hypertension awareness/treatment/control (NHES V/VI), diabetes, dyslipidemia, smoking.
- Thai stroke: onset-to-door, thrombolysis rate, EMS use; STEMI: reperfusion rates, delays, mortality.
- PAD prevalence/underdiagnosis in Thailand/Asia; AF undiagnosed burden.
- Secondary prevention adherence, readmission, recurrence after stroke/MI in Thailand.
- Economic cost of CVD in Thailand.
- Existing digital/AI tools and documented shortcomings; trustworthy-AI concerns.
- Verify the hackathon prompt numbers ("half a billion", "one-third of Thais", "~20 million deaths", "80,000 Thai deaths").

## Scale decision
Broad, multi-faceted, multi-domain topic (epidemiology + emergency systems + prevention + solution landscape, global and Thai). Not a "what is X" explainer. **Decision: 4 `researcher` subagents in parallel**, lead does synthesis, then `verifier` then `reviewer`.

## Task ledger
| ID | Owner | Task | Output | Status |
|---|---|---|---|---|
| T1 | lead (was researcher; degraded) | Burden: global + Thailand CVD epidemiology, costs, trends, verify prompt numbers | outputs/.drafts/cvd-problem-definition-thailand-research-burden.md | done |
| T2 | lead (was researcher; degraded) | Respond faster: Thai stroke/STEMI emergency pathway delays, EMS 1669, reperfusion, rural access | outputs/.drafts/cvd-problem-definition-thailand-research-acute.md | done (gaps: national IVT rate, EMS use) |
| T3 | lead (was researcher; degraded) | Detect earlier/prevent: HTN/DM/lipid control, AF, PAD, screening, VHVs, adherence, secondary prevention | outputs/.drafts/cvd-problem-definition-thailand-research-prevention.md | done (gaps: AF/PAD population data, VHV count) |
| T4 | lead (was researcher; degraded) | Current solutions landscape (digital/AI/agentic, Thai programs) and shortcomings; trustworthy AI concerns | outputs/.drafts/cvd-problem-definition-thailand-research-solutions.md | partial (Thai digital platforms/regulation BLOCKED) |
| S1 | lead | Synthesis draft with 5 Ws + candidate problem statements + pitch | outputs/.drafts/cvd-problem-definition-thailand-draft.md | done |
| C1 | lead (verifier unavailable) | Citations + URL check | outputs/.drafts/cvd-problem-definition-thailand-cited.md | done |
| R1 | lead (reviewer unavailable) | Verification review | outputs/.drafts/cvd-problem-definition-thailand-verification.md | done (PASS WITH NOTES) |
| D1 | lead | Deliver final + provenance | outputs/cvd-problem-definition-thailand.md | done |

## Verification log
- 2026-10-16: `subagents_enable` and `web_enable` returned success, but neither the `subagent` tool nor `web_search`/`fetch_content` surfaced in the lead's tool list this turn. Workflow script written (cvd-problem-definition-thailand-workflow.js) but NOT launched. Degraded mode: lead executes T1-T4 directly with `feynman_science_database_search` (PubMed/Europe PMC/OpenAlex/Semantic Scholar) and `curl` for HTML pages (curl to who.int returned HTTP 200).

- 2026-10-16: Evidence round 1 complete (~60 queries: PubMed E-utilities, Europe PMC REST, WHO/WHF/DDC pages, WHF PDF via document_search/parse). DuckDuckGo started returning bot challenge mid-run; Bing returned off-topic results → general web search BLOCKED; Thai government platform/regulation facts left unverified.
- 2026-10-16: Hackathon prompt numbers checked: half-billion and ~20M verified (WHF 2023, WHO); Thailand 80,000 and one-third UNVERIFIED (GBD via WHF says 120,370 CVD deaths).
- 2026-10-16: URL check: 44/44 PMIDs resolved via esummary; non-PubMed URLs 200 on retry. Citation map: 0 orphans. Self-review: 0 FATAL, 5 MAJOR (disclosed), 5 MINOR. Two localized edits applied to the cited draft and confirmed with grep.

## Decision log
- 2026-10-16: Slug chosen `cvd-problem-definition-thailand`.
- 2026-10-16: Scale = 4 researchers (broad multi-domain).
- 2026-10-16: Output framed problem-first: landscape → candidate problems ranked by evidence → recommended problem with full 5 Ws → pitch in the "my father..." style. Solutions are mentioned only as "current solutions & shortcomings" plus a short, clearly labelled "solution space" note.
- 2026-10-16: DEGRADED MODE. Subagent tool unavailable → T1-T4 owner changed researcher→lead; C1 verifier and R1 reviewer become lead self-citation and self-review (per direct-mode rules). Research files keep the same paths.
- 2026-10-16: Recommended problem A (undetected/uncontrolled hypertension); B (stroke onset-to-door delay) and C (30-day post-discharge window) kept as alternates with 5W tables.
