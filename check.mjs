// node check.mjs seeds.json   checks every draft in out/drafts.json that the scheduler has not judged yet, and prints why any fail
import fs from "fs"; import { check, index } from "./gate.mjs";
const J = (f, d) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return d; } };
const drafts = J("out/drafts.json", []), news = J("in/news.json", []), seeds = J(process.argv[2] || "", {}), only = new Set((process.argv[3] || "").split(",").filter(Boolean));
let bad = 0; const ok = [];
for (const p of drafts) {
  if (only.size && !only.has(p.id)) { ok.push(index(p.text)); continue; }
  const seedText = p.url ? (news.find((n) => n.url === p.url) || {}).text || null : ["motivation", "opinion"].includes(p.lane) ? null : seeds[p.seed] || null;
  const r = check(p, { history: ok, seedText });
  if (r.length) { bad++; console.log("FAIL", p.id, p.lane, r.join(" | ")); } else ok.push(index(p.text));
}
console.log(`${drafts.length} drafts, ${bad} failing`); process.exit(bad ? 1 : 0);
