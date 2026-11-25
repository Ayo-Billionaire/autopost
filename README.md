# autopost

Code that drafts and checks short text posts. `gate.mjs` holds the checks, `RULES.md` the writing rules, `fetch.py` collects public release notes, `out/drafts.json` holds drafts. Nothing here can post: the scheduler pulls drafts, checks them again and decides.
