'use strict';
/* NeVedis front end. Untrusted text (messages, AI output) is only ever set via textContent. */
(() => {
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
function h(tag, props = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k === 'text') el.textContent = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) el.append(c.nodeType ? c : document.createTextNode(String(c)));
  return el;
}
const toast = msg => { const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => t.hidden = true, 2400); };
const pick = a => a[Math.floor(Math.random() * a.length)];
const shuffle = a => { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

/* ---------- Vedi the owl (static SVG, no user data) ---------- */
const OWL = `<svg class="vedi" viewBox="0 0 120 120" aria-hidden="true"><defs><linearGradient id="vg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a83ff"/><stop offset="1" stop-color="#5a3bf0"/></linearGradient></defs>
<g class="body-g"><path d="M27 34 L19 9 L46 24 Z" fill="#5a3bf0"/><path d="M93 34 L101 9 L74 24 Z" fill="#5a3bf0"/>
<ellipse cx="60" cy="67" rx="45" ry="46" fill="url(#vg)"/><ellipse cx="60" cy="88" rx="27" ry="20" fill="#c9bcff" opacity=".55"/>
<path d="M50 92 q4 4 8 0 M62 92 q4 4 8 0" stroke="#7c62ff" stroke-width="2" fill="none" opacity=".7"/>
<g class="eyes"><circle cx="42" cy="56" r="17" fill="#fff"/><circle cx="78" cy="56" r="17" fill="#fff"/>
<g class="pupils"><circle cx="43" cy="58" r="8" fill="#1b1530"/><circle cx="79" cy="58" r="8" fill="#1b1530"/><circle cx="46" cy="54.5" r="2.6" fill="#fff"/><circle cx="82" cy="54.5" r="2.6" fill="#fff"/></g></g>
<g class="cheeks"><circle cx="30" cy="74" r="5" fill="#ff8fab" opacity=".7"/><circle cx="90" cy="74" r="5" fill="#ff8fab" opacity=".7"/></g>
<g class="brows" stroke="#1b1530" stroke-width="4" stroke-linecap="round" fill="none"><path class="brow-l" d="M28 37 L52 43"/><path class="brow-r" d="M92 37 L68 43"/></g>
<path d="M54 70 L66 70 L60 80 Z" fill="#ffaa1d"/><ellipse cx="47" cy="112" rx="7" ry="3.5" fill="#ffaa1d"/><ellipse cx="73" cy="112" rx="7" ry="3.5" fill="#ffaa1d"/></g></svg>`;
function owls() { $$('[data-mascot]').forEach(el => { if (!el.firstChild) el.innerHTML = OWL; }); }
const owl = (cls = '') => { const d = h('div', { class: cls }); d.innerHTML = OWL; return d; };

/* ---------- tabs ---------- */
function showTab(name) {
  $$('.tab').forEach(t => t.classList.toggle('on', t.dataset.tab === name));
  $$('.view').forEach(v => v.classList.toggle('on', v.id === `tab-${name}`));
  if (name === 'game' && !game.deck) game.start();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
document.addEventListener('click', e => { const t = e.target.closest('[data-tab]'); if (t) { e.preventDefault(); showTab(t.dataset.tab); } });

/* ---------- library ---------- */
let LIB = null;
const fieldOf = id => LIB.fields.find(f => f.id === id);
async function loadLib() { LIB = await (await fetch('/api/library')).json(); $('#fam-count').textContent = LIB.families.length; guide.init(); }

/* ---------- composer ---------- */
const files = { image: null, audio: null };
const msg = $('#msg');
function autosize() { msg.style.height = 'auto'; msg.style.height = Math.min(msg.scrollHeight, 420) + 'px'; }
msg.addEventListener('input', autosize);
function addFile(f) {
  if (!f) return;
  const kind = f.type.startsWith('image/') ? 'image' : (f.type.startsWith('audio/') || /\.(m4a|mp3|wav)$/i.test(f.name)) ? 'audio' : null;
  if (!kind) return toast('Use a screenshot (PNG/JPG) or a recording (MP3/WAV/M4A).');
  if (f.size > 15 * 1024 * 1024) return toast('That file is over 15 MB.');
  files[kind] = f; drawChips();
}
function drawChips() {
  const c = $('#chips'); c.replaceChildren();
  for (const kind of ['image', 'audio']) {
    const f = files[kind]; if (!f) continue;
    const pic = kind === 'image' ? h('img', { src: URL.createObjectURL(f), alt: '' }) : h('span', { class: 'ico', text: '🎙️' });
    c.append(h('div', { class: 'fchip' }, pic, h('span', { text: f.name.length > 28 ? f.name.slice(0, 26) + '…' : f.name }),
      h('button', { type: 'button', 'aria-label': 'Remove', text: '✕', onclick: () => { files[kind] = null; drawChips(); } })));
  }
}
$('#file').addEventListener('change', e => { [...e.target.files].forEach(addFile); e.target.value = ''; });
const comp = $('#composer');
['dragenter', 'dragover'].forEach(ev => comp.addEventListener(ev, e => { e.preventDefault(); comp.classList.add('drag'); }));
['dragleave', 'drop'].forEach(ev => comp.addEventListener(ev, e => { e.preventDefault(); if (ev === 'drop' || !comp.contains(e.relatedTarget)) comp.classList.remove('drag'); }));
comp.addEventListener('drop', e => [...e.dataTransfer.files].forEach(addFile));
document.addEventListener('paste', e => {
  const img = [...(e.clipboardData?.items || [])].find(i => i.type.startsWith('image/'));
  if (img && $('#tab-check').classList.contains('on')) { e.preventDefault(); addFile(new File([img.getAsFile()], 'pasted-screenshot.png', { type: img.type })); toast('Screenshot added 📸'); }
});
$('#surprise').addEventListener('click', () => {
  const f = pick(LIB.families); msg.value = f.example.text; autosize(); msg.focus();
  toast(`${f.emoji} Example: ${f.name}`);
});
comp.addEventListener('submit', e => { e.preventDefault(); check(); });
msg.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) check(); });

/* ---------- checking ---------- */
const SCAN_STEPS = ['Reading the message', 'X-raying every link', 'Checking sender tricks', 'Comparing with 28 scam playbooks', 'Writing your answer'];
let last = null;
async function check() {
  const text = msg.value.trim();
  last = { text: msg.value, image: files.image, audio: files.audio };
  if (!text && !files.image && !files.audio) { toast('Paste a message or add a screenshot first 👆'); msg.focus(); return; }
  $('#go').disabled = true;
  $('#composer-view').hidden = true; $('#result-view').hidden = true; $('#scan-view').hidden = false;
  $('#scan-view').classList.add('scanning');
  const list = $('#scan-steps'); list.replaceChildren(...SCAN_STEPS.map(s => h('li', {}, h('span', { class: 'tick', text: '·' }), s)));
  const lis = [...list.children]; let i = 0;
  const stepT = setInterval(() => { if (i > 0) { lis[i - 1].classList.add('done'); lis[i - 1].firstChild.textContent = '✓'; } if (i < lis.length) lis[i++].classList.add('show'); }, 900);
  const tips = shuffle(LIB.families.map(f => `${f.emoji} ${f.tell}`));
  let ti = 0; const tip = () => $('#scan-tip').textContent = 'Did you know? ' + tips[ti++ % tips.length];
  tip(); const tipT = setInterval(tip, 4200);
  const fd = new FormData(); fd.append('text', text);
  if (files.image) fd.append('files', files.image); if (files.audio) fd.append('files', files.audio);
  let data, err;
  try {
    const ctrl = new AbortController(); const kill = setTimeout(() => ctrl.abort(), 80000);
    const r = await fetch('/api/check', { method: 'POST', body: fd, signal: ctrl.signal }); clearTimeout(kill);
    data = await r.json(); if (!r.ok) err = data.detail || 'Something went wrong.';
  } catch (e) { err = e.name === 'AbortError' ? 'That took too long. Please try again.' : 'Could not reach NeVedis. Is the server running?'; }
  clearInterval(stepT); clearInterval(tipT);
  $('#scan-view').hidden = true; $('#scan-view').classList.remove('scanning'); $('#go').disabled = false;
  if (err) { $('#composer-view').hidden = false; toast(err); return; }
  renderResult(data);
}

/* ---------- result ---------- */
const TITLES = { high: ['🚨 Scam alert!', "Don't reply, click, or pay."], medium: ['🤔 Hmm, be careful.', 'Some warning signs here.'], low: ['👍 No strong red flags', 'Still verify through the official phone number or app.'], unknown: ["🤷 Couldn't check this yet", "The AI check didn't go through this time."] };
const COLOR = { high: '#ff4d5e', medium: '#ffaa1d', low: '#12b886', unknown: '#9a93b5' };
function retry() { if (!last) return; msg.value = last.text; files.image = last.image; files.audio = last.audio; drawChips(); autosize(); check(); }
function gauge(score, v) {
  const wrap = h('div', { class: 'gauge' }); const len = 172.8;
  wrap.innerHTML = `<svg viewBox="0 0 132 76"><path d="M11 70 A55 55 0 0 1 121 70" fill="none" stroke="#efe7f7" stroke-width="14" stroke-linecap="round"/><path class="arc" d="M11 70 A55 55 0 0 1 121 70" fill="none" stroke="${COLOR[v]}" stroke-width="14" stroke-linecap="round" stroke-dasharray="0 ${len}"/></svg>`;
  const num = h('div', { class: 'num', text: '0' }); wrap.append(num, h('small', { text: 'risk score' }));
  requestAnimationFrame(() => {
    const t0 = performance.now(), arc = wrap.querySelector('.arc');
    const step = now => { const p = Math.min(1, (now - t0) / 1100), e = 1 - Math.pow(1 - p, 3), val = Math.round(score * e);
      arc.setAttribute('stroke-dasharray', `${(len * val / 100).toFixed(1)} ${len}`); num.textContent = val; if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  });
  return wrap;
}
function reportLink(rep, cls = 'rep') {
  const href = rep.kind === 'link' ? rep.target : rep.kind === 'email' ? `mailto:${rep.target}` : rep.kind === 'sms' ? `sms:${rep.target}` : /^[\d-]+$/.test(rep.target.replace(/\s/g, '')) ? `tel:${rep.target.replace(/\D/g, '')}` : null;
  const el = h(href ? 'a' : 'div', { class: cls, href, target: rep.kind === 'link' ? '_blank' : null, rel: 'noopener noreferrer' },
    h('b', { text: rep.label }), h('small', { text: rep.note }), h('span', { class: 'tgt', text: rep.target }));
  return el;
}
function stepLink(rep) {
  if (!rep) return null;
  const href = rep.kind === 'link' ? rep.target : rep.kind === 'email' ? `mailto:${rep.target}` : rep.kind === 'sms' ? `sms:${rep.target}` : /^[\d-]+$/.test(rep.target) ? `tel:${rep.target.replace(/\D/g, '')}` : null;
  return href ? h('a', { class: 'act', href, target: rep.kind === 'link' ? '_blank' : null, rel: 'noopener noreferrer', text: `${rep.label} →` }) : h('span', { class: 'act ghost', text: `${rep.label}: ${rep.target}` });
}
const XR = {
  lookalike: l => [['looks', `Looks like ${l.pretends}`], ['real', `Really goes to ${l.domain}`], 'bad'],
  brand_mismatch: l => [['looks', `Message says ${l.pretends}`], ['real', `Link goes to ${l.domain}`], 'bad'],
  punycode: l => [['real', `Fake look-alike letters: ${l.host}`], null, 'bad'],
  shortener: l => [['meh', `🙈 Shortened link (${l.domain}) hides where it goes`], null, ''],
  official: l => [['okay', `✓ Official ${l.domain} website`], null, ''],
  unknown: l => [['meh', `Goes to ${l.domain}`], null, ''],
};
function renderResult(r) {
  const box = $('#result-view'); box.replaceChildren(); box.hidden = false;
  const v = r.verdict, fam = r.family;
  box.append(h('div', { class: 'res-top' }, h('button', { class: 'back', text: '← Check another', onclick: reset })));
  if (r.notice) box.append(h('div', { class: 'notice', text: '⚠️ ' + r.notice.trim() }));

  // 0. could not check: never pretend it's fine
  if (v === 'unknown') {
    box.append(h('div', { class: 'card verdict unknown' },
      h('div', { class: 'v-row' }, owl('v-owl mood-medium'), h('div', {}, h('div', { class: 'v-title', text: TITLES.unknown[0] }), h('div', { class: 'v-sub', text: TITLES.unknown[1] }))),
      h('p', { class: 'summary', text: r.summary }),
      h('div', { class: 'row' }, h('button', { class: 'btn big', text: '🔄 Try again', onclick: retry }), h('button', { class: 'btn soft big', text: 'Check something else', onclick: reset }))));
    box.append(h('div', { class: 'card', style: 'animation-delay:.1s' }, h('h3', {}, '🛡️ Until then'),
      h('ul', { class: 'todo' }, r.what_to_do.map(s => h('li', { onclick: e => e.currentTarget.classList.toggle('done') }, h('span', { class: 'box', text: '✓' }), h('span', { text: s }))))));
    if (r.links?.length) box.append(xrayCard(r.links));
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }

  // 1. verdict
  const vOwl = owl(`v-owl mood-${v}`);
  const card = h('div', { class: `card verdict ${v}` },
    h('div', { class: 'v-row' }, vOwl, h('div', {}, h('div', { class: 'v-title', text: TITLES[v][0] }), h('div', { class: 'v-sub', text: TITLES[v][1] })), gauge(r.final_score, v)));
  if (fam) card.append(h('button', { class: 'fam-badge', onclick: () => guide.open(fam.id) }, h('span', { class: 'e', text: fam.emoji }), fam.name, h('small', { text: `· ${fam.field.name}` })));
  card.append(h('p', { class: 'summary', text: r.summary }));
  if (r.three_p) {
    const P = [['pretext', '🎭 Fake story'], ['pressure', '⏰ Pressure'], ['payoff_ask', '💰 Wants something']];
    card.append(h('div', { class: 'threep' }, P.map(([k, l]) => { const p = r.three_p[k] || {}; return h('div', { class: `pp ${p.present ? 'on' : ''}`, title: p.evidence || '' }, `${l} ${p.present ? '✓' : '–'}`); })));
  }
  box.append(card);

  // 2. their game plan
  if (fam) {
    const plan = h('ol', { class: 'plan' }, fam.steps.map((s, i) => h('li', { class: i === 0 ? 'here' : i === 1 ? 'next' : 'later' },
      h('span', { class: 'n', text: i + 1 }), h('span', { class: 't' }, s, i === 0 ? h('span', { class: 'pin', text: '📍 You are here' }) : i === 1 ? h('span', { class: 'pin', text: '⚠️ Next, if you reply' }) : null))));
    box.append(h('div', { class: 'card', style: 'animation-delay:.08s' }, h('h3', {}, '🧠 Their game plan', h('small', { text: fam.name })), plan,
      r.next_move ? h('div', { class: 'nextmove' }, h('span', { text: '🔮' }), h('span', {}, h('b', { text: 'Their next move: ' }), r.next_move)) : null,
      h('div', { class: 'tell' }, h('span', { text: '💡' }), h('span', { text: fam.tell }))));
  }

  // 3. red flags
  const flags = r.red_flags.length ? r.red_flags.map(f => ({ ...f, src: null }))
    : r.rule_signals.map(s => ({ type: s.id, quote: s.evidence, explanation: s.label, src: 'instant check' }));
  if (flags.length) box.append(h('div', { class: 'card', style: 'animation-delay:.14s' }, h('h3', {}, '🚩 Red flags we spotted', h('small', { text: `${flags.length}` })),
    flags.map(f => h('div', { class: 'flag' }, h('div', { class: 'quote' }, '“', h('mark', { text: f.quote }), '”', f.src ? h('span', { class: 'src', text: '⚡ ' + f.src }) : null), h('div', { class: 'why', text: f.explanation })))));

  // 4. link x-ray
  if (r.links?.length) box.append(xrayCard(r.links));

  // 5. what to do
  box.append(h('div', { class: 'card', style: 'animation-delay:.26s' }, h('h3', {}, '✅ What to do now'),
    h('ul', { class: 'todo' }, r.what_to_do.map(s => h('li', { onclick: e => e.currentTarget.classList.toggle('done') }, h('span', { class: 'box', text: '✓' }), h('span', { text: s }))))));

  // 6. uh-oh
  if (v !== 'low') box.append(uhOh());

  // 7. report it
  const reps = fam ? fam.report : [LIB.reports.ftc, LIB.reports.spam_text];
  if (v !== 'low') box.append(h('div', { class: 'card', style: 'animation-delay:.34s' }, h('h3', {}, '📣 Report it', h('small', { text: 'helps stop them' })), h('div', { class: 'reports' }, reps.map(x => reportLink(x)))));

  // 8. warn your family
  if (r.share_warning) {
    const share = async () => { if (navigator.share) { try { await navigator.share({ text: r.share_warning + '\n\nChecked with NeVedis 🦉' }); } catch {} } else copy(); };
    const copy = async () => { try { await navigator.clipboard.writeText(r.share_warning); toast('Copied! Paste it in your family chat 💬'); } catch { toast('Select the text and copy it.'); } };
    box.append(h('div', { class: 'card', style: 'animation-delay:.4s' }, h('h3', {}, '💬 Warn your family'), h('div', { class: 'share-bubble', text: r.share_warning }),
      h('div', { class: 'row' }, h('button', { class: 'btn', text: '📤 Share', onclick: share }), h('button', { class: 'btn soft', text: '📋 Copy', onclick: copy }))));
  }

  // score details
  box.append(h('details', { class: 'how' }, h('summary', { text: 'How was this scored?' }),
    h('p', { text: r.gemini_score == null ? `Built-in checks only: rule score ${r.rule_score}.` : (r.rule_signals.length ? `AI score ${r.gemini_score} and instant-check score ${r.rule_score}, combined 60/40.` : `AI score ${r.gemini_score}. The instant checks found nothing to add, so the AI score is used alone.`) }),
    h('p', { text: `${r.hard ? 'A hard red flag was found, so the score is at least 80. ' : ''}70–100 high · 40–69 medium · 0–39 low. Model: ${r.model} · ${r.seconds}s.` })));
  box.append(h('div', { class: 'row', style: 'justify-content:center;margin-bottom:10px' }, h('button', { class: 'btn big', text: '🔍 Check another message', onclick: reset })));
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if (v === 'high') setTimeout(() => vOwl.classList.add('mood-high'), 50);
}
function xrayCard(links) {
  return h('div', { class: 'card', style: 'animation-delay:.2s' }, h('h3', {}, '🔬 Link X-ray', h('small', { text: 'checked instantly, no AI guessing' })),
    h('div', { class: 'xray' }, links.map(l => { const [a, b, cls] = XR[l.status](l);
      return h('div', { class: `xr ${cls}` }, h('div', { class: 'u', text: l.url }), h('div', { class: 'lr' }, h('span', { class: `pill ${a[0]}`, text: a[1] }), b ? '→' : null, b ? h('span', { class: `pill ${b[0]}`, text: b[1] }) : null)); })));
}
function uhOh() {
  const D = LIB.damage, help = h('div', { class: 'help' });
  const keys = ['clicked', 'shared_info', 'shared_card', 'paid', 'gave_code', 'installed_app'];
  const bar = h('div', { class: 'pick' });
  const show = key => {
    bar.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.k === key));
    help.replaceChildren();
    const d = D[key];
    if (key === 'paid') {
      const mbar = h('div', { class: 'pick', style: 'margin-top:4px' }), mhelp = h('div', { class: 'help' });
      for (const [m, label] of Object.entries(LIB.pay_methods)) mbar.append(h('button', { 'data-m': m, text: label, onclick: () => {
        mbar.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.m === m));
        mhelp.replaceChildren(...[...d.methods[m], ...d.steps].map((s, i) => h('div', { class: 'hs' }, h('span', { class: 'k', text: i + 1 }), h('div', {}, h('div', { text: s.text }), stepLink(s.report)))));
      } }));
      help.append(h('div', { style: 'font-weight:700', text: 'How did you pay?' }), mbar, mhelp);
    } else {
      help.append(...d.steps.map((s, i) => h('div', { class: 'hs' }, h('span', { class: 'k', text: i + 1 }), h('div', {}, h('div', { text: s.text }), stepLink(s.report)))));
    }
  };
  keys.forEach(k => bar.append(h('button', { 'data-k': k, text: `${D[k].emoji} ${D[k].label}`, onclick: () => show(k) })));
  return h('div', { class: 'card uh', style: 'animation-delay:.3s' }, h('h3', {}, '🆘 Uh-oh… already did something?'),
    h('p', { style: 'margin:0 0 12px;color:var(--ink2)', text: "Don't panic. Tap what happened and we'll show you exactly what to do, right now." }), bar, help);
}
function reset() { $('#result-view').hidden = true; $('#composer-view').hidden = false; msg.value = ''; files.image = files.audio = null; drawChips(); autosize(); window.scrollTo({ top: 0, behavior: 'smooth' }); msg.focus(); }

/* ---------- Spot the scam game ---------- */
const game = {
  deck: null, i: 0, score: 0, streak: 0,
  best: (() => { try { return +localStorage.getItem('nv.best') || 0; } catch { return 0; } })(),
  start() {
    const scams = LIB.families.map(f => ({ ...f.example, scam: true, fam: f }));
    const legit = LIB.legit.map(l => ({ ...l, scam: false }));
    this.deck = shuffle([...scams, ...legit]); this.i = 0; this.score = 0; this.streak = 0; this.draw();
  },
  hud() {
    $('#g-score').textContent = this.score; $('#g-streak').textContent = this.streak; $('#g-best').textContent = this.best;
    $('#g-progress').style.width = `${(this.i / this.deck.length) * 100}%`;
  },
  view(c, marks) {
    const ICON = { sms: '💬', email: '✉️', phone_call: '📞', voicemail: '📼', messenger: '💭', social_media: '📣' };
    const LABEL = { sms: 'Text message', email: 'Email', phone_call: 'Phone call', voicemail: 'Voicemail', messenger: 'Chat message', social_media: 'Ad / pop-up' };
    const t = h('div', { class: 'mv-text' });
    if (marks?.length) highlight(t, c.text, marks.map(m => m[0])); else t.textContent = c.text;
    return h('div', { class: `msgview ${c.channel}` }, h('div', { class: 'mv-from' }, h('span', { class: 'av', text: ICON[c.channel] || '💬' }), h('div', {}, c.from, h('small', { text: LABEL[c.channel] || 'Message' }))), t);
  },
  draw() {
    this.hud(); const box = $('#game-card'); box.className = 'game-card';
    if (this.i >= this.deck.length) return this.end();
    const c = this.deck[this.i];
    box.replaceChildren(h('div', { style: 'color:var(--mut);font-weight:700;margin-bottom:10px', text: `Message ${this.i + 1} of ${this.deck.length} · Scam or real?` }), this.view(c),
      h('div', { class: 'choices' }, h('button', { class: 'choice scam', text: '🚩 Scam', onclick: () => this.answer(true) }), h('button', { class: 'choice real', text: '👍 Real', onclick: () => this.answer(false) })));
  },
  answer(saidScam) {
    const c = this.deck[this.i], right = saidScam === c.scam, box = $('#game-card');
    if (right) { this.streak++; this.score += 10 + Math.min(this.streak, 10) * 2; if (this.streak % 5 === 0) confetti(); }
    else this.streak = 0;
    if (this.score > this.best) { this.best = this.score; try { localStorage.setItem('nv.best', this.best); } catch {} }
    box.classList.add(right ? 'correct' : 'wrong'); this.i++; this.hud();
    const reveal = h('div', { class: `reveal ${right ? 'good' : 'bad'}` }, h('h3', { text: right ? pick(['Nailed it! 🎉', 'Sharp eyes! 👀', 'Correct! 🦉', 'You got it! ✨']) : pick(['Tricky one! 😬', 'Not quite! 🙈', 'They got you there 😅']) }));
    if (c.scam) {
      reveal.append(h('p', {}, h('b', { text: `It's a scam: ${c.fam.emoji} ${c.fam.name}. ` }), c.fam.tell), h('ul', {}, c.flags.map(([q, why]) => h('li', {}, h('b', { text: `“${q}”` }), ` ${why}`))));
    } else reveal.append(h('p', {}, h('b', { text: "It's real. " }), c.why));
    box.replaceChildren(h('div', { style: 'color:var(--mut);font-weight:700;margin-bottom:10px', text: c.scam ? 'The giveaways, highlighted:' : 'Why it checks out:' }), this.view(c, c.scam ? c.flags : null), reveal,
      h('div', { class: 'row', style: 'justify-content:flex-end' }, h('button', { class: 'btn big', text: this.i >= this.deck.length ? 'See my score →' : 'Next message →', onclick: () => this.draw() })));
  },
  end() {
    const total = this.deck.length, pct = Math.round(this.score / (total * 30) * 100);
    const title = pct > 60 ? 'Scam-spotting legend 🏆' : pct > 35 ? 'Sharp scam radar 🦉' : 'Getting there! Keep practicing 💪';
    $('#game-card').replaceChildren(h('div', { class: 'end' }, owl('hero-owl mood-low'), h('div', { class: 'big', text: this.score }), h('h2', { text: title }),
      h('p', { text: 'Share the game with your family. The more people know the tricks, the fewer get fooled.' }),
      h('div', { class: 'row', style: 'justify-content:center' }, h('button', { class: 'btn big', text: '🔁 Play again', onclick: () => this.start() }))));
    confetti();
  },
};
function highlight(el, text, quotes) {
  const qs = quotes.filter(q => q && text.includes(q)).sort((a, b) => text.indexOf(a) - text.indexOf(b));
  let pos = 0;
  for (const q of qs) { const at = text.indexOf(q, pos); if (at < 0) continue; el.append(text.slice(pos, at), h('mark', { text: q })); pos = at + q.length; }
  el.append(text.slice(pos));
}

/* ---------- field guide ---------- */
const guide = {
  field: 'all',
  init() {
    const chips = $('#g-fields');
    chips.replaceChildren(h('button', { class: 'on', 'data-f': 'all', text: '✨ All' }), ...LIB.fields.map(f => h('button', { 'data-f': f.id, text: `${f.emoji} ${f.name}` })));
    chips.addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; this.field = b.dataset.f; chips.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b)); this.draw(); });
    $('#g-search').addEventListener('input', () => this.draw());
    this.draw();
  },
  draw() {
    const q = $('#g-search').value.toLowerCase().trim();
    const L = LIB.families.filter(f => (this.field === 'all' || f.field.id === this.field) && (!q || [f.name, f.hook, f.tell, f.field.name, f.example.text].join(' ').toLowerCase().includes(q)));
    $('#g-grid').replaceChildren(...(L.length ? L.map(f => h('button', { class: 'fam', onclick: () => this.open(f.id) }, h('span', { class: 'e', text: f.emoji }), h('small', { text: f.field.name }), h('b', { text: f.name }), h('p', { text: f.hook })))
      : [h('div', { class: 'empty', text: 'No scam matches that. Try another word.' })]));
  },
  open(id) {
    const f = LIB.families.find(x => x.id === id); if (!f) return;
    const sheet = $('#sheet'), card = sheet.firstElementChild;
    card.replaceChildren(h('button', { class: 'x', text: '✕', 'aria-label': 'Close', onclick: () => sheet.hidden = true }),
      h('div', { style: 'font-size:46px', text: f.emoji }), h('small', { style: 'color:var(--mut);font-weight:700', text: f.field.name }), h('h2', { text: f.name }), h('p', { text: f.hook }),
      h('h3', { style: 'margin:16px 0 8px', text: '🧠 Their game plan' }), h('ol', { class: 'plan' }, f.steps.map((s, i) => h('li', {}, h('span', { class: 'n', text: i + 1 }), h('span', { class: 't', text: s })))),
      h('div', { class: 'tell' }, h('span', { text: '💡' }), h('span', {}, h('b', { text: 'The giveaway: ' }), f.tell)),
      h('div', { class: 'nextmove', style: 'background:var(--mint-soft);color:#0b6b4f' }, h('span', { text: '🛡️' }), h('span', {}, h('b', { text: 'Remember: ' }), f.never)),
      h('h3', { style: 'margin:18px 0 8px', text: '👀 What it looks like' }), game.view(f.example, f.example.flags),
      h('h3', { style: 'margin:18px 0 8px', text: '📣 Where to report it' }), h('div', { class: 'reports' }, f.report.map(x => reportLink(x))),
      h('div', { class: 'row' }, h('button', { class: 'btn big', text: '🔍 Check this example', onclick: () => { sheet.hidden = true; showTab('check'); reset(); msg.value = f.example.text; autosize(); } })));
    sheet.hidden = false; card.scrollTop = 0;
  },
};
$('#sheet').addEventListener('click', e => { if (e.target.id === 'sheet') e.target.hidden = true; });
document.addEventListener('keydown', e => { if (e.key === 'Escape') $('#sheet').hidden = true; });

/* ---------- confetti ---------- */
function confetti() {
  const cv = $('#confetti'), ctx = cv.getContext('2d'); cv.width = innerWidth; cv.height = innerHeight;
  const C = ['#6c4cff', '#ff4d5e', '#ffaa1d', '#12b886', '#3fb5f0', '#c04cff'];
  const P = Array.from({ length: 140 }, () => ({ x: innerWidth / 2, y: innerHeight / 3, vx: (Math.random() - .5) * 16, vy: Math.random() * -14 - 4, s: 4 + Math.random() * 6, c: pick(C), r: Math.random() * 6, vr: (Math.random() - .5) * .3 }));
  let f = 0; (function frame() {
    ctx.clearRect(0, 0, cv.width, cv.height);
    for (const p of P) { p.vy += .45; p.x += p.vx; p.y += p.vy; p.r += p.vr; ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r); ctx.fillStyle = p.c; ctx.fillRect(-p.s / 2, -p.s / 2, p.s, p.s * .6); ctx.restore(); }
    if (++f < 110) requestAnimationFrame(frame); else ctx.clearRect(0, 0, cv.width, cv.height);
  })();
}

owls(); loadLib();
})();
