#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime
from urllib.request import Request, urlopen

ORCID_ID = os.environ.get("ORCID_ID", "0000-0002-0097-6738")
API_BASE = "https://pub.orcid.org/v3.0"

UA = "hbrleelab.github.io (GitHub Actions) - publications sync"

def http_json(url: str) -> dict:
    req = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": UA,
    })
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def pick_year(work: dict) -> int | None:
    # ORCID work schema varies; try several common fields
    # publication-date (year/month/day) is often in work["publication-date"]["year"]["value"]
    pub = work.get("publication-date") or {}
    y = (pub.get("year") or {}).get("value")
    if y:
        try:
            return int(y)
        except:
            pass

    # created-date as fallback
    created = work.get("created-date") or {}
    y2 = (created.get("year") or {}).get("value")
    if y2:
        try:
            return int(y2)
        except:
            pass
    return None

def normalize_doi(doi: str) -> str:
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    return doi

def extract_ids(work: dict) -> dict:
    out = {"doi": None, "url": None}
    ext = work.get("external-ids") or {}
    for eid in ext.get("external-id", []) or []:
        t = (eid.get("external-id-type") or "").lower()
        v = (eid.get("external-id-value") or "").strip()
        if t == "doi" and v:
            out["doi"] = normalize_doi(v)
            break

    # work URL (sometimes present)
    urlv = (work.get("url") or {}).get("value")
    if urlv:
        out["url"] = urlv.strip()
    return out

def extract_title(work: dict) -> str:
    title = (((work.get("title") or {}).get("title") or {}).get("value") or "").strip()
    if title:
        return title
    # fallback
    return "(No title)"

def extract_journal(work: dict) -> str | None:
    j = (work.get("journal-title") or {}).get("value")
    return j.strip() if isinstance(j, str) and j.strip() else None

def extract_type(work: dict) -> str | None:
    t = work.get("type")
    return t.strip() if isinstance(t, str) and t.strip() else None

def main():
    # 1) summary list
    summary_url = f"{API_BASE}/{ORCID_ID}/works"
    works = http_json(summary_url)

    groups = works.get("group", []) or []
    pubs = []
    seen_keys = set()

    for g in groups:
        # group -> work-summary list
        summaries = (g.get("work-summary") or [])
        if not summaries:
            continue

        # pick "best" summary: prefer one with DOI; else first
        best = None
        for s in summaries:
            ids = extract_ids(s)
            if ids.get("doi"):
                best = s
                break
        if best is None:
            best = summaries[0]

        title = extract_title(best)
        year = pick_year(best)
        ids = extract_ids(best)
        journal = extract_journal(best)
        wtype = extract_type(best)

        # stable key for de-dup
        key = ids.get("doi") or (title.lower(), year, journal)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        pubs.append({
            "title": title,
            "year": year,
            "journal": journal,
            "type": wtype,
            "doi": ids.get("doi"),
            "url": ids.get("url"),
        })

    # sort: year desc, then title
    pubs.sort(key=lambda x: (x["year"] is None, -(x["year"] or 0), x["title"].lower()))

    payload = {
        "orcid": ORCID_ID,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "items": pubs
    }

    os.makedirs("_data", exist_ok=True)
    out_path = "_data/publications.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {out_path} with {len(pubs)} items.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
