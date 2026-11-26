"""Still cards. python3 render.py posts.json outdir. Each post: {id, lane, text, colour}. Only motivation and opinion become cards. A card that fails its layout check is not written."""
import json,sys,pathlib
from playwright.sync_api import sync_playwright
H=pathlib.Path(__file__).resolve().parent;posts=json.load(open(sys.argv[1]));O=pathlib.Path(sys.argv[2]);O.mkdir(parents=True,exist_ok=True);rep=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome")
    for x in posts:
        r={"id":x["id"],"lane":x["lane"],"ok":False}
        try:
            if x["lane"] not in ("motivation","opinion"): raise ValueError("not a card post")
            g=b.new_page(viewport={"width":1080,"height":1350},device_scale_factor=2);g.goto((H/"card.html").as_uri());s=g.evaluate("p=>setup(p)",x);r.update(s)
            if not s["ok"] or not s["font"] or s["photo"]<300: r["ok"]=False;raise ValueError(", ".join(s["why"]) or "font or photo missing")
            g.screenshot(path=str(O/f"{x['id']}.jpg"),type="jpeg",quality=92);g.close()
        except Exception as e: r["error"]=str(e)[:160]
        rep.append(r);print(r["id"],r["ok"],r.get("size"),r.get("margin"),r.get("error",""),flush=True)
    b.close()
json.dump(rep,open(O/"report.json","w"),indent=1);sys.exit(0 if any(r["ok"] for r in rep) else 1)
