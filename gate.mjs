// The checks every post must pass. The writer runs this before it pushes, and the scheduler runs the same code again before it queues.
export const LANES = ["motivation", "lesson", "builder", "opinion", "news", "session", "buyers"];
const BANNED = "leverage utilize delve foster streamline robust seamless comprehensive dynamic innovative scalable landscape ecosystem paradigm tapestry realm groundbreaking transformative pivotal crucial meticulous unlock empower harness elevate revolutionize navigate underscore".split(" ");
const FILLER = /\b(game changer|at the end of the day|needless to say|in today's|move the needle|circle back|that being said|it's important to note|let that sink in|hot take|unpopular opinion|read that again|here's the thing|the truth is|most people)\b/i;
const POLITICS = /\b(politic\w*|president\w*|elections?|votes?|voters?|voting|ballots?|senat\w+|congress\w*|parliament\w*|democrats?|republicans?|conservatives?|liberals?|labour party|trump|biden|harris|obama|putin|zelensky\w*|tinubu|obi|atiku|buhari|netanyahu|israel\w*|gaza|palestin\w*|ukrain\w*|russia\w*|iran\w*|immigra\w*|abortion|gun control|war|wars|military|minister|governor|government|protest\w*)\b/i;
const RELIGION = /\b(god|gods|lord|jesus|christ\w*|church\w*|bible|biblical|scripture|pray\w*|prayer\w*|allah|islam\w*|muslim\w*|quran|koran|mosque|imam|pastor|priest|prophet\w*|heaven|hell|angels?|devil|satan|sins?|sinner|bless\w*|faith|holy|spiritual\w*|religio\w*|hindu\w*|buddh\w*|jewish|judaism|torah|gospel|amen|hallelujah|miracles?|soul|karma|ramadan|easter|christmas)\b/i;
const RULES = [
  [/[–—]/, "long dash"], [/(?<=[A-Za-z])-(?=[A-Za-z])/, "hyphen inside a word"], [/\s-\s/, "spaced hyphen"], [/(?:^|\n)\s*[-*•]\s/, "bullet"],
  [/(?:^|\n)\s*\d+[.)]\s/, "numbered list"], [/\bsources?\b\s*[:)]|\(source|\bsource\b/i, "the word source"], [/#\w/, "hashtag"],
  [/https?:\/\/|www\./i, "link"], [/@\w/, "mention"], [/\p{Extended_Pictographic}/u, "emoji"], [/!/, "exclamation mark"], [/[;]/, "semicolon"],
  [/\b[Aa] client(?:'s)?\b/, "say my client or your client"], [/\b(?:past|former|old) client/i, "past client"], [/\bMake\b(?!\.com)/, "bare Make, say Make.com"],
  [/\bAI key\b/, "say API key"], [/\bUpwork\b|\bFiverr\b|\bConnects\b|\bfreelanc\w*\b/i, "marketplace talk"], [/(?:^|\n)\s*Ask:/, "Ask line"],
  [/\b(?:hormozi|cardone|goal billionaire|brian tracy|maxwell)\b/i, "borrowed name"], [/\b(?:fuck\w*|shit\w*|damn|bitch\w*|ass)\b/i, "swearing"],
  [/\b(?:guarantee\w*|get rich|passive income|double your|triple your|10x)\b/i, "promise of results"], [/\b(?:i am|i'm) (?:an ai|a bot)\b/i, "bot line"],
  [/\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|June?|July?|Aug|Sept?|Oct|Nov|Dec)[a-z]*\b/, "date, write the 2nd of August"],
  [/\b(?:January|February|March|April|June|July|August|September|October|November|December) \d{1,2}\b(?!\d|st|nd|rd|th)/, "date, write the 2nd of August"],
  [/(?:[.!?]\s+|\n)(?:Yet|Still|However|Although)\b/, "contrast word after a full stop"], [/\b[\w.+]+@[\w-]+\.\w+|\+?\d[\d ()]{8,}\d/, "email or phone"],
  [/(?:^|\n)(?:Picture|Imagine|Think of)\b/i, "comparison opener"], [/\b(?:lead magnet|DM me|link in bio|comment below|follow for)\b/i, "engagement bait"],
];
const LINK = /\b(?:[A-Za-z0-9-]+\.)+(?:com|dev|md|io|ai|app|net|org|co|me|sh|so|to|xyz|gg|ly|tv|info|us|uk|ng)\b(?:\/\S*)?/gi;
export const xlen = (t) => t.length + [...t.matchAll(LINK)].reduce((n, m) => n + 23 - m[0].length, 0);
const STOP = new Set("the and that this with from your you they them their have has had will would can could what when where which who how not but for are was were its it's into than then there here been being about because only just one our out over after before more most some any all each every does did done".split(" "));
export const terms = (t) => new Set((t.toLowerCase().match(/[a-z0-9']{4,}/g) || []).filter((w) => !STOP.has(w)).map((w) => w.replace(/(?:ing|ed|es|s)$/, "")));
export function similarity(a, b) {
  const A = terms(a), B = terms(b); if (!A.size || !B.size) return 0;
  let n = 0; for (const w of A) if (B.has(w)) n++;
  return n / Math.min(A.size, B.size);
}
export const index = (t) => ({ o: opening(t), w: [...terms(t)], h: t.slice(0, 60) });
const opening = (t) => (t.toLowerCase().match(/[a-z0-9']+/g) || []).slice(0, 5).join(" ");
const sents = (p) => (p.replace(/\b(?:\d+\.\d+(?:\.\d+)*|Make\.com|n8n\.io|e\.g\.|i\.e\.)/g, (m) => m.replace(/\./g, "_")).match(/[^.!?]+[.!?]+["')]*/g) || [p]).map((s) => s.trim()).filter(Boolean);
export const numbers = (t) => [...new Set((t.match(/\d[\d,]*(?:\.\d+)*/g) || []).map((n) => n.replace(/,/g, "")))];
// seedText: what the writer was given for this post (seed or vendor page). Motivation and opinion posts carry none.
export function check(p, { history = [], seedText = null, batch = [], priv = [] } = {}) {
  const bad = [], t = p && p.text;
  if (!p || typeof t !== "string" || !t.trim()) return ["no text"];
  if (!/^[a-z0-9][a-z0-9-]{3,40}$/.test(p.id || "")) bad.push("bad id");
  if (!LANES.includes(p.lane)) bad.push("unknown lane");
  if (t !== t.trim() || /\n{3,}|[^\n]\n[^\n]|[ \t]{2,}/.test(t)) bad.push("layout: one blank line between paragraphs");
  if (xlen(t) > 280) bad.push(`too long for X: ${xlen(t)}`);
  if (t.length < 60) bad.push("too short to say anything");
  for (const [rx, why] of RULES) { const m = t.match(rx); if (m) bad.push(`${why}: ${m[0].trim()}`); }
  for (const w of BANNED) if (new RegExp(`\\b${w}\\w*`, "i").test(t)) bad.push(`AI word: ${w}`);
  if (FILLER.test(t)) bad.push(`filler: ${t.match(FILLER)[0]}`);
  if (POLITICS.test(t)) bad.push(`politics: ${t.match(POLITICS)[0]}`);
  if (RELIGION.test(t)) bad.push(`religion: ${t.match(RELIGION)[0]}`);
  for (const rx of priv) { const m = t.match(new RegExp(rx, "i")); if (m) bad.push("private name or killed story"); }
  const paras = t.split("\n\n"), all = paras.flatMap(sents);
  if (paras.length > 4) bad.push("more than 4 paragraphs");
  paras.forEach((x) => { if (sents(x).length > 1 && !/["”]$/.test(sents(x)[0])) bad.push("two sentences in one paragraph"); if (!/[.?]["')]?$/.test(x)) bad.push("paragraph does not end in a full stop"); });
  for (let i = 0; i + 2 < all.length; i++) if (all.slice(i, i + 3).every((s) => s.split(/\s+/).length <= 5)) bad.push("three short sentences in a row");
  if (all.some((s) => s.split(/\s+/).length > 34)) bad.push("sentence over 34 words");
  const last = all[all.length - 1] || "";
  if (/\?["')]?$/.test(last)) bad.push("ends on a question");
  if (p.lane === "motivation" || p.lane === "opinion") {
    const claim = t.match(/\b(?:I|we|my|our)\b[^.]{0,40}\b(?:built|saw|found|told|asked|lost|earned|made|had|was|were|worked|tested|checked|learned|learnt|watched|spoke|met|paid|charged|hired|fired|started|quit|closed|won|signed|read|wrote|spent|said|did|went|got)\b/);
    if (claim) bad.push(`invented event: ${claim[0]}`);
    const n = numbers(t); if (n.length) bad.push(`number with nothing behind it: ${n[0]}`);
    if (/\b(?:research|stud(?:y|ies)|statistics?|data shows|percent|survey)\b/i.test(t)) bad.push("claims evidence");
  } else {
    if (!seedText) bad.push("no seed or page behind it");
    else { const s = seedText.replace(/,/g, ""); for (const n of numbers(t)) if (!new RegExp(`(?<![\\d.])${n.replace(/\./g, "\\.")}(?!\\d)`).test(s)) bad.push(`number not in the seed: ${n}`); for (const m of t.matchAll(/"([^"]{4,})"/g)) if (!s.toLowerCase().includes(m[1].replace(/[.,]$/, "").toLowerCase())) bad.push(`quote not in the seed: ${m[1]}`); }
  }
  if (typeof p.means !== "string" || p.means.trim().split(/\s+/).length < 10) bad.push("no plain answer to 'what does this mean?'");
  else if (similarity(p.means, t) > 0.85 && terms(p.means).size <= terms(t).size) bad.push("plain answer only repeats the post");
  const mine = terms(t), open = opening(t);
  for (const raw of [...history, ...batch]) {
    const h = typeof raw === "string" ? index(raw) : raw;
    if (h.o === open) { bad.push(`same opening as a live post: ${h.o}`); break; }
    let n = 0; for (const w of h.w) if (mine.has(w)) n++;
    const s = n / Math.max(1, Math.min(mine.size, h.w.length)); if (s >= 0.55 && mine.size >= 5 && h.w.length >= 5) { bad.push(`too close to a live post (${s.toFixed(2)}): ${h.h}`); break; }
  }
  return [...new Set(bad)];
}
