return await runs.all([
  { key: "literature", agent: "researcher", task: "Read outputs/.plans/crao-ai-detection-prototype-T1.md and write outputs/.drafts/crao-ai-detection-prototype-research-literature.md.", output: "outputs/.drafts/crao-ai-detection-prototype-research-literature.md" },
  { key: "clinical", agent: "researcher", task: "Read outputs/.plans/crao-ai-detection-prototype-T2.md and write outputs/.drafts/crao-ai-detection-prototype-research-clinical.md.", output: "outputs/.drafts/crao-ai-detection-prototype-research-clinical.md" },
  { key: "data", agent: "researcher", task: "Read outputs/.plans/crao-ai-detection-prototype-T3.md and write outputs/.drafts/crao-ai-detection-prototype-research-data.md.", output: "outputs/.drafts/crao-ai-detection-prototype-research-data.md" },
  { key: "build", agent: "researcher", task: "Read outputs/.plans/crao-ai-detection-prototype-T4.md and write outputs/.drafts/crao-ai-detection-prototype-research-build.md.", output: "outputs/.drafts/crao-ai-detection-prototype-research-build.md" },
]);
