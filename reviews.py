"""Weekly: read public reviews of automation sellers through Fiverr's official MCP server (no login) into reviews.json. No usernames are kept."""
import json, re, urllib.request, datetime, hashlib, sys
U = "https://mcp.fiverr.com/mcp"; sid = None; n = 0
def rpc(m, p, notify=False):
    global sid, n
    n += 1; b = {"jsonrpc": "2.0", "method": m, "params": p}
    if not notify: b["id"] = n
    h = {"content-type": "application/json", "accept": "application/json, text/event-stream", "user-agent": "reviews-reader/1.0"}
    if sid: h["mcp-session-id"] = sid
    r = urllib.request.urlopen(urllib.request.Request(U, data=json.dumps(b).encode(), headers=h), timeout=60)
    sid = r.headers.get("mcp-session-id") or sid; t = r.read().decode()
    if notify or not t: return None
    for l in t.splitlines():
        if l.startswith("data:"): return json.loads(l[5:])
    return json.loads(t)
def tool(name, **a):
    r = rpc("tools/call", {"name": name, "arguments": a}).get("result", {})
    if r.get("structuredContent"): return r["structuredContent"]
    for c in r.get("content", []):
        try: return json.loads(c["text"])
        except Exception: pass
    return {}
def walk(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and isinstance(v, str): yield v
            yield from walk(v, key)
    elif isinstance(o, list):
        for v in o: yield from walk(v, key)
rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "reviews-reader", "version": "1"}}); rpc("notifications/initialized", {}, notify=True)
users = []
for brief in ("Make.com automation for a small business", "n8n workflow automation and AI agents", "CRM automation and lead follow up", "AI voice agent that books appointments", "Zapier automation between business apps"):
    try:
        for u in walk(tool("find_freelancers", brief=brief), "username"):
            if u not in users and u != "usman_george": users.append(u)
    except Exception as e: print("find", str(e)[:80])
print(len(users), "sellers"); old = {}
try: old = {x["id"]: x for x in json.load(open("in/reviews.json"))}
except Exception: pass
new = 0
for u in users[:16]:
    try: res = tool("list_seller_reviews", username=u, limit=30, sort_by="recent")
    except Exception as e: print("reviews", str(e)[:80]); continue
    if "-v" in sys.argv: print(json.dumps(res)[:500])
    for rv in res.get("data", []):
        t, score = rv.get("comment") or "", rv.get("score")
        if (rv.get("created_at") or "")[:4] < str(datetime.date.today().year - 1): continue
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 40: continue
        t = re.sub(r"@\w+|https?://\S+|[\w.+-]+@[\w-]+\.\w+", "", t).replace(u, "the seller")
        t = re.sub(r"(?<=[a-z,;] )(?!I\b|AI\b|API\b|CRM\b|Make\b|Zapier\b|Airtable\b|Google\b|Gmail\b|Slack\b|Notion\b|Shopify\b|HubSpot\b|OpenAI\b)[A-Z][a-z]+", "the seller", t)
        t = re.sub(r"^[A-Z][a-z]+ (?=is|was|did|has|delivered|made|helped|went|took|understood|knows|provided|really|built)", "The seller ", t)
        t = re.sub(r"\b(?!The\b|This\b|He\b|She\b|It\b|They\b|We\b|Work\b|Service\b|Everything\b|Communication\b|There\b|That\b|Delivery\b|Quality\b|Seller\b|Project\b|Who\b|Which\b|AI\b)[A-Z][a-z]{2,}(?= (?:is|was|did|has|went|took|solved|showed|exceeded|delivered|made|helped|understood|knows|provided|really|built|clearly|kept|set|fixed|and)\b)", "the seller", t)
        i = hashlib.sha1(t.encode()).hexdigest()[:12]
        if i not in old: old[i] = {"id": i, "at": datetime.date.today().isoformat(), "seller": hashlib.sha1(u.encode()).hexdigest()[:6], "score": score, "text": t[:220]}; new += 1
json.dump(sorted(old.values(), key=lambda x: x["at"])[-400:], open("in/reviews.json", "w"), indent=0, ensure_ascii=False); print(len(old), "reviews,", new, "new")
