// Static page behaviour: entrances, the stage layers, the output index, the risk bands, the flow slider.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // Hero headline: split into masked lines (one per comma clause).
  const h1 = $('.hero h1');
  h1.innerHTML = h1.textContent.split(/(?<=,)\s/).map((t) => `<span class="ln"><span>${t}</span></span>`).join(' ');

  // Entrances: parts of each section rise in reading order, staggered, once.
  const groups = [
    ['.intro', 'p'], ['.features', 'h2, .panel, .module-text'], ['.showcase', '.index button, .sheet-stage'],
    ['.flow', '.flow-clause, .flow-frag, .flow-control'], ['.records', '.stepped span, .records-lead, tbody tr:not(.gap), .records-note'],
    ['.limits', 'h2, .answers p'], ['.cta', 'p, .btn'], ['.foot', '.credits, .foot-line'],
  ];
  const parts = [];
  for (const [sec, sel] of groups) {
    $$(sel, $(sec)).forEach((el, i) => { el.classList.add('rv'); el.style.transitionDelay = `${Math.min(i, 8) * 75}ms`; parts.push(el); });
  }
  if (reduce || !('IntersectionObserver' in window)) {
    parts.forEach((el) => el.classList.add('in')); $('.hero').classList.add('in');
  } else {
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    parts.forEach((el) => io.observe(el));
    requestAnimationFrame(() => requestAnimationFrame(() => $('.hero').classList.add('in')));
  }

  // The stage: the fixed fundus photo crossfades to the layer that matches the section in view.
  const labels = {
    'photo only': 'photo only · quality gate passed',
    vessel: 'layer: all vessels · AutoMorph M2',
    'artery-vein': 'layer: artery / vein · AVR 0.59 · reference 0.67–1.0 (placeholder)',
    disc: 'layer: optic disc · heatmap: none, no model loaded',
  };
  const layers = $$('.stage-pic .layer[data-name]');
  const nameEl = $('#layer-name');
  const show = (name) => {
    layers.forEach((l) => l.classList.toggle('on', l.dataset.name === name || (name === 'disc' && l.dataset.name === 'artery-vein')));
    nameEl.textContent = labels[name] || name;
  };
  if ('IntersectionObserver' in window) {
    const so = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) show(e.target.dataset.layer); }), { rootMargin: '-45% 0px -45% 0px' });
    $$('[data-layer]').forEach((el) => so.observe(el));
  }

  // Output index: tabs swap the sheet with a short crossfade.
  const tabs = $$('.index [role="tab"]');
  const select = (tab) => {
    const next = $('#' + tab.getAttribute('aria-controls'));
    const cur = $('.sheet:not([hidden])');
    tabs.forEach((t) => { const on = t === tab; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; });
    if (cur === next) return;
    const swap = () => { cur.hidden = true; cur.classList.remove('fading'); next.hidden = false; };
    if (reduce) return swap();
    cur.classList.add('fading');
    setTimeout(() => { swap(); next.classList.add('fading'); requestAnimationFrame(() => requestAnimationFrame(() => next.classList.remove('fading'))); }, 200);
  };
  $$('.sheet').forEach((sh, i) => { sh.hidden = i > 0; }); // no-JS shows every sheet
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => select(t));
    t.addEventListener('keydown', (e) => {
      const d = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
      const j = e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : d ? (i + d + tabs.length) % tabs.length : -1;
      if (j < 0) return;
      e.preventDefault(); tabs[j].focus(); select(tabs[j]);
    });
  });

  // The live thing: band edges and suggestion texts copied from app/api/config.yaml and rules/templates/en.json.
  const EDGES = [5.0, 7.5, 20.0];
  const BANDS = ['low', 'borderline', 'intermediate', 'high'];
  const SUG = {
    low: 'Emphasise lifestyle change; reassess risk factors every 4–6 years.',
    borderline: 'Discuss risk. If risk enhancers are present, a moderate-intensity statin may be considered after shared decision-making.',
    intermediate: 'A moderate-intensity statin is reasonable; risk enhancers favour starting. Reinforce lifestyle change.',
    high: 'Consider a high-intensity statin to lower LDL-C by at least 50%; reassess lipids 4–12 weeks after starting.',
  };
  const band = (r) => BANDS[EDGES.filter((e) => r >= e).length]; // same as rules/risk.py _band
  console.assert(band(4.9) === 'low' && band(5) === 'borderline' && band(7.5) === 'intermediate' && band(19.9) === 'intermediate' && band(20) === 'high', 'band edges');
  const rin = $('#risk-in');
  const setRisk = () => {
    const r = +rin.value, b = band(r);
    $('#risk-out').textContent = r.toFixed(1);
    $('#band-out').textContent = b;
    $('#sug-out').textContent = SUG[b];
    $('#enh-out').hidden = b !== 'borderline';
    $$('.band-bar span').forEach((s) => s.classList.toggle('on', s.dataset.band === b));
    rin.parentElement.style.setProperty('--f', r / 40);
    rin.setAttribute('aria-valuetext', `${r.toFixed(1)} percent, ${b}`);
  };
  rin.addEventListener('input', setRisk); setRisk();

  // The flow: one slider drives the clause and the interface fragment.
  const STAGES = [
    ['Consent', 'First, consent is recorded.', 'Retinal photos are biometric health data under Thai PDPA section 26. Care use and model improvement are separate ticks, and refusing the second changes nothing about care.',
      'assets/img/consent-gate.png', 684, 442, "Screenshot of the consent step: care use (required), use for model improvement (optional), retention in years, right to withdraw explained."],
    ['Quality gate', 'Then the photo is checked.', 'EXIF and GPS are stripped, and a dark or blurred photo is refused with a reason to retake, plus a note never to delay referral for it.',
      'assets/img/retake-card.png', 684, 332, 'Screenshot of the retake card: underexposed and blurred, quality 0.03 below a placeholder threshold, refer urgently if no gradable photo within minutes.'],
    ['Preliminary', 'Next, a result with reasons.', 'The level arrives with every reason behind it and the label AI-assisted, not a diagnosis. Nothing is final yet.',
      'assets/img/triage-card.png', 436, 562, 'Screenshot of the Emergency triage card: ESCALATE, specialist review, with reasons and limitation sentences.'],
    ['Signed', 'Last, a clinician signs.', 'Confirm or override, with a reason. An override is kept as a labelled case for offline retraining; the deployed model never learns at runtime.',
      'assets/img/sign-dialog.png', 560, 543, 'Screenshot of the sign dialog: confirm the AI result or override it, and answer whether this is CRAO before signing as final.'],
  ];
  const sin = $('#stage-in'), frag = $('#frag'), clause = $('#clause'), note = $('#clause-note');
  const names = $$('.stage-names li');
  let cur = 0, timer;
  const setStage = () => {
    const i = +sin.value; if (i === cur) return; cur = i;
    const [n, c, t, src, w, h, alt] = STAGES[i];
    sin.parentElement.style.setProperty('--f', i / 3);
    sin.setAttribute('aria-valuetext', n);
    names.forEach((li, k) => li.classList.toggle('on', k === i));
    const apply = () => { clause.textContent = c; note.textContent = t; frag.src = src; frag.width = w; frag.height = h; frag.alt = alt; [frag, clause, note].forEach((el) => el.classList.remove('fading')); };
    if (reduce) return apply();
    [frag, clause, note].forEach((el) => el.classList.add('fading'));
    clearTimeout(timer); timer = setTimeout(apply, 200);
  };
  sin.addEventListener('input', setStage);
  names.forEach((li, k) => li.addEventListener('click', () => { sin.value = k; setStage(); }));
  STAGES.forEach(([, , , src]) => { const im = new Image(); im.src = src; });

  // Pause the drifting photo when the tab is hidden.
  document.addEventListener('visibilitychange', () => { $('.stage-pic').style.animationPlayState = document.hidden ? 'paused' : 'running'; });
})();
