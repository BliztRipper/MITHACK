# Provenance: CVD problem definition (5 Ws) for the Siriraj x MIT Agentic Healthcare Hackathon, Thailand

- **Date:** 2026-10-16
- **Rounds:** 1 evidence round (about 60 queries) plus 1 citation/URL-verification pass
- **Mode:** DEGRADED. The `subagent`, `web_search` and `fetch_content` tools never surfaced after enabling, so the lead ran all research, citation and review directly. Tools: NCBI E-utilities and Europe PMC REST via curl; WHO/WHF/DDC/ThaiJo pages via curl; WHF PDF via document_search/document_parse; DuckDuckGo HTML (worked for 3 queries, then bot-challenged); Bing (off-topic results, not used).
- **Sources consulted:** ~110 records surfaced across searches (PubMed/Europe PMC hits, 9 web pages, 1 PDF)
- **Sources accepted:** 45 (listed in the final report's Sources: 7 web pages/PDFs from WHO, WHF, DDC and ThaiJo; 38 PubMed-indexed papers)
- **Sources rejected:** off-topic search hits (non-Thai cohorts, unrelated GBD papers, Bing junk results); one Research Square preprint (DOI 10.21203/rs.3.rs-8568478/v1) kept in the research notes but not cited in the final, as it is not peer reviewed; a Thai news aggregator (thethaiger, aseannow) not used, as it is secondary with unclear figures. No dead links among accepted sources (all 44 PMIDs resolved via esummary; non-PubMed URLs returned 200).
- **Verification:** PASS WITH NOTES. Self-review only (no independent reviewer). MAJOR notes: single-source NHES control figures; Thai digital-platform and regulatory landscape unverified (web search blocked); hackathon brief's "80,000" and "one-third" figures unverified; no national IVT or EMS-use data. See outputs/.drafts/cvd-problem-definition-thailand-verification.md
- **Plan:** outputs/.plans/cvd-problem-definition-thailand.md
- **Research files:** outputs/.drafts/cvd-problem-definition-thailand-research-burden.md, -research-acute.md, -research-prevention.md, -research-solutions.md; draft outputs/.drafts/cvd-problem-definition-thailand-draft.md; cited outputs/.drafts/cvd-problem-definition-thailand-cited.md
- **Not launched:** outputs/.plans/cvd-problem-definition-thailand-workflow.js and T1–T4 briefs (written for the 4-researcher workflow; subagent tool unavailable)
