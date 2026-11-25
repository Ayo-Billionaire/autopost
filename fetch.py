"""Collect recent public release notes into in/news.json and the scheduler's state into in/status.json. Fails when the scheduler reports a problem, so GitHub sends an email."""
import datetime, html, json, os, re, sys, urllib.request
UA = {"user-agent": "Mozilla/5.0 (compatible; release-notes-reader)"}
def get(u, t=25, **h):
    with urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **h}), timeout=t) as r: return r.read(8000000).decode("utf8", "replace")
def text(h):
    h = re.sub(r"(?is)<(script|style|nav|header|footer|svg|noscript|form)[^>]*>.*?</\1>", " ", h)
    m = re.search(r"(?is)<(article|main)[^>]*>(.*?)</\1>", h); h = m.group(2) if m else h
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", h))).strip()
SKIP = re.compile(r"customer-stor|/business/|/learn/|/careers|policy|safety|election|government|defen[cs]e|military|election|nonprofit|partner|raises|funding|hires|appoint|sports?|golden-state", re.I)
now = datetime.datetime.now(datetime.timezone.utc); out = []
old = {}
try: old = {x["url"]: x for x in json.load(open("in/news.json"))}
except Exception: pass
try: feed = json.loads(get("https://release-watch.noqodepro.workers.dev/news?days=4"))
except Exception as e: feed = []; print("feed", e)
feed = feed if isinstance(feed, list) else feed.get("items") or feed.get("news") or []
for x in sorted(feed, key=lambda x: x["at"], reverse=True):
    if x.get("tier") != "alert" or SKIP.search(x["link"] + " " + x["title"]) or not x["link"].startswith("https://"): continue
    if x["link"] in old: out.append(old[x["link"]]); continue
    try: t = text(get(x["link"]))
    except Exception as e: print("skip", x["link"], str(e)[:60]); continue
    if len(t) < 350: continue
    out.append({"url": x["link"], "by": x["name"], "title": x["title"][:140], "at": x["at"], "kind": "news", "text": (x["title"] + ". " + t)[:1800]})
    if len(out) >= 12: break
auth = {"authorization": "Bearer " + os.environ["GITHUB_TOKEN"]} if os.environ.get("GITHUB_TOKEN") else {}
for repo, by in (("anthropics/claude-code", "Claude Code"), ("n8n-io/n8n", "n8n"), ("openai/codex", "OpenAI's Codex")):
    try:
        for r in json.loads(get(f"https://api.github.com/repos/{repo}/releases?per_page=6", **auth)):
            if r.get("prerelease") or len(r.get("body") or "") < 200: continue
            out.append({"url": r["html_url"], "by": by, "title": r["name"] or r["tag_name"], "at": r["published_at"], "kind": "builder", "text": f"{by} {r['tag_name']} published {r['published_at'][:10]}. " + re.sub(r"\s+", " ", r["body"])[:1700]}); break
    except Exception as e: print("skip", repo, str(e)[:60])
json.dump(out, open("in/news.json", "w"), indent=0); print(len(out), "pages")
try: st = json.loads(get("https://noqode-scheduler.noqodepro.workers.dev/auto/status"))
except Exception as e: st = {"problems": ["scheduler did not answer: " + str(e)[:80]], "on": None}
json.dump(st, open("in/status.json", "w"), indent=0)
try:
    last = max(x["at"] for x in json.load(open("out/drafts.json")) if x.get("at"))
    if st.get("on") and now - datetime.datetime.fromisoformat(last.replace("Z", "+00:00")) > datetime.timedelta(days=3): st["problems"].append("the writer has not added a draft for 3 days")
except ValueError: pass
print("problems:", st["problems"])
try: a = json.load(open("in/alert.json"))
except Exception: a = {}
fresh = a.get("problems") != st["problems"] or now.timestamp() - a.get("ts", 0) > 43200
if st["problems"] and fresh: json.dump({"problems": st["problems"], "ts": now.timestamp()}, open("in/alert.json", "w")); open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a").write("alert=1\n")
elif not st["problems"] and a: os.remove("in/alert.json")
