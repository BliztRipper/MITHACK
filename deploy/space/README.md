---
title: Retina CVD / CRAO demo
emoji: 👁️
colorFrom: gray
colorTo: red
sdk: docker
app_port: 7860
pinned: false
license: other
short_description: Public demo API for a fundus-photo triage prototype
---

# Retina CVD / CRAO demo (API)

The back end of the public demo of the Siriraj x MIT hackathon prototype: a clinician-facing app that reads a fundus
photo for cardiovascular risk (Screening) and for possible central retinal artery occlusion (Emergency). The web app
on Vercel talks to this Space; browsers do not call it directly.

This container runs InterSystems IRIS for Health Community (the FHIR record store, private to the container) and the
demo API on port 7860. Demo mode accepts only the six curated photos, whose results are cached; the record store holds
20 fictional patients and is reset on every restart. Research prototype, not a medical device, not for clinical use.

Licences: the project code is the hackathon team's; InterSystems IRIS for Health Community is used under the
InterSystems Community licence; the demo photos are CC BY 4.0, CC BY 2.0, Apache-2.0 or public domain, credited in
`app/api/demo_cache/SOURCES.md` and with each photo in the app.
