"""Draw every card the scheduler is waiting for. Cards hold text that is already public on X and Threads."""
import json,subprocess,sys,urllib.request,pathlib,time
H=pathlib.Path(__file__).resolve().parent;O=H/"out";O.mkdir(exist_ok=True);U="https://noqode-scheduler.noqodepro.workers.dev"
def get(p): return json.load(urllib.request.urlopen(urllib.request.Request(U+p,headers={"User-Agent":"autocards"}),timeout=60))
load=lambda n,d:json.loads((O/n).read_text()) if (O/n).exists() else d
plan=get("/meta/plan");rep=load("report.json",[]);seen=load("seen.json",{})
todo=[x for x in plan if not any(r["id"]==x["id"] and r.get("text")==x["text"] for r in rep)]
if todo:
    (H/"todo.json").write_text(json.dumps(todo))
    subprocess.run([sys.executable,str(H/"render.py"),str(H/"todo.json"),str(H/"new")],check=False)
    for r in json.loads((H/"new/report.json").read_text()):
        t=next(x for x in todo if x["id"]==r["id"]);r.update(text=t["text"],at=int(time.time()));rep=[x for x in rep if x["id"]!=r["id"]]+[r];seen.pop(r["id"],None)
        if r["ok"]: (O/f"{r['id']}.jpg").write_bytes((H/f"new/{r['id']}.jpg").read_bytes())
for r in [x for x in rep if time.time()-x["at"]>21*86400]: (O/f"{r['id']}.jpg").unlink(missing_ok=True)
rep=[x for x in rep if time.time()-x["at"]<=21*86400]
(O/"report.json").write_text(json.dumps(rep,indent=1,ensure_ascii=False))
(O/"seen.json").write_text(json.dumps({k:v for k,v in seen.items() if any(r["id"]==k for r in rep)},indent=1))
s=get("/meta/status");bad=[r["id"] for r in rep if r["ok"] and r["id"] not in seen and time.time()-r["at"]>30*3600]
START=1795824000 # 28 Nov 2026 00:00 UTC: until then few bookings are normal, the lane is new
prob=[p for p in s["problems"] if not (p.startswith("only") and time.time()<START)]+([f"{len(bad)} card(s) drawn over 30 hours ago and nobody looked: {bad[:3]}"] if bad and s["on"] else [])
(O/"alert.json").write_text(json.dumps(prob));print("plan",len(plan),"drawn",len(todo),"problems",prob)
