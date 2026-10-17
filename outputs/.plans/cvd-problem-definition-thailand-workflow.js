return await runs.all([
  { key: "burden", agent: "researcher", task: "Read outputs/.plans/cvd-problem-definition-thailand-T1.md and write outputs/.drafts/cvd-problem-definition-thailand-research-burden.md.", output: "outputs/.drafts/cvd-problem-definition-thailand-research-burden.md" },
  { key: "acute", agent: "researcher", task: "Read outputs/.plans/cvd-problem-definition-thailand-T2.md and write outputs/.drafts/cvd-problem-definition-thailand-research-acute.md.", output: "outputs/.drafts/cvd-problem-definition-thailand-research-acute.md" },
  { key: "prevention", agent: "researcher", task: "Read outputs/.plans/cvd-problem-definition-thailand-T3.md and write outputs/.drafts/cvd-problem-definition-thailand-research-prevention.md.", output: "outputs/.drafts/cvd-problem-definition-thailand-research-prevention.md" },
  { key: "solutions", agent: "researcher", task: "Read outputs/.plans/cvd-problem-definition-thailand-T4.md and write outputs/.drafts/cvd-problem-definition-thailand-research-solutions.md.", output: "outputs/.drafts/cvd-problem-definition-thailand-research-solutions.md" },
]);
