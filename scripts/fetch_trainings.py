"""Fetch faculty training programmes from public sources into _data/trainings.json.

Runs every morning through .github/workflows/update-trainings.yml. Plain Python, no extra packages.
Each source is a function that returns a list of programmes. To add a source, write one more
function and add it to SOURCES. If a source fails, the others still run and its last good
entries are kept, so one broken site never empties the page.

We only list programmes and link to the organiser's own page. We do not copy coordinator
names, phone numbers or emails.
"""
import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "_data" / "trainings.json"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
TODAY = dt.datetime.now(IST).date()
UA = "Mozilla/5.0 (compatible; TeacharchaTrainingList/1.0; +https://vicharanashala.github.io/teacharcha/)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "X-Requested-With": "XMLHttpRequest"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", errors="ignore")


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


# ---- UGC Malaviya Mission Teacher Training Programme (all MMTTCs) ----
UGC_TYPES = {
    "3": "Faculty Induction Programme",
    "4": "Refresher Course",
    "5": "Short Term Programme / FDP",
    "6": "Capacity Building: Cyber Security",
    "7": "Capacity Building: Administrative Staff",
    "8": "Capacity Building: Artificial Intelligence",
    "9": "Capacity Building: STEM",
    "10": "Capacity Building: Science Communication",
    "11": "Indian Knowledge Systems",
}


def ugc_date(value):
    ms = int(re.search(r"-?\d+", value).group())
    return (dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).astimezone(IST)).date()


def ugc():
    out = []
    for cat, label in UGC_TYPES.items():
        data = json.loads(get(f"https://mmc.ugc.ac.in/RFSEvent/GetEvents?Category={cat}"))["Data"]
        for v in data:
            start = ugc_date(v["theStart"])
            end = ugc_date(v["theEnd"]) if v.get("theEnd") else start
            brochure = (v.get("Description") or "").strip()
            out.append({
                "title": clean(v.get("CategoryTitle")) or label,
                "organiser": clean(v.get("Subject")),
                "type": label,
                "mode": clean(v.get("mode")) or "Not stated",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "brochure": f"https://mmc.ugc.ac.in/{brochure.lstrip('/')}" if brochure else "",
                "link": "https://mmc.ugc.ac.in/",
                "apply_note": "Apply on the UGC MMTTP portal",
                "source": "UGC MMTTP portal",
            })
    return out


# ---- NITTTR Chandigarh ----
def nitttr_chd():
    base = "https://fdp.nitttrchd.ac.in/fdp2025/"
    page = get(base + "latestcourses.php")
    out = []
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", page):
        cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)
        if len(cells) < 7:
            continue
        try:
            start = dt.datetime.strptime(clean(cells[3]), "%d/%m/%Y").date()
            end = dt.datetime.strptime(clean(cells[4]), "%d/%m/%Y").date()
        except ValueError:
            continue
        mode = clean(cells[1])
        pdf = re.search(r"href='([^']+\.pdf)'", cells[10] if len(cells) > 10 else "", re.I)
        out.append({
            "title": clean(cells[2]),
            "organiser": "NITTTR Chandigarh",
            "type": "Short Term Programme / FDP",
            "mode": {"Contact": "Physical", "ICT": "Online"}.get(mode, mode) or "Not stated",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "brochure": urllib.request.quote(base + pdf.group(1), safe=":/") if pdf else "",
            "link": base + "latestcourses.php",
            "apply_note": "Apply on the NITTTR Chandigarh site",
            "source": "NITTTR Chandigarh",
        })
    return out


SOURCES = {"UGC MMTTP portal": ugc, "NITTTR Chandigarh": nitttr_chd}


def main():
    old = json.loads(OUT.read_text()) if OUT.exists() else {"programmes": []}
    programmes, status = [], {}
    for name, fetch in SOURCES.items():
        try:
            got = fetch()
            if not got:
                raise RuntimeError("no programmes found")
            status[name] = {"ok": True, "count": len(got)}
        except Exception as exc:  # keep last good entries for this source
            print(f"WARNING {name}: {exc}", file=sys.stderr)
            got = [p for p in old["programmes"] if p["source"] == name]
            status[name] = {"ok": False, "count": len(got), "error": str(exc)[:200]}
        programmes += got

    # Only what is still running or yet to start, without repeats.
    seen, live = set(), []
    for p in programmes:
        key = (p["organiser"].lower(), p["title"].lower(), p["start"])
        if p["end"] >= TODAY.isoformat() and key not in seen:
            seen.add(key)
            p["running"] = p["start"] <= TODAY.isoformat()
            live.append(p)
    live.sort(key=lambda p: (p["start"], p["organiser"]))

    if old.get("programmes") == live:
        print("No change.")
        return
    OUT.write_text(json.dumps({"updated": TODAY.isoformat(), "sources": status, "programmes": live},
                              ensure_ascii=False, indent=1) + "\n")
    print(f"Wrote {len(live)} programmes. {status}")


if __name__ == "__main__":
    main()
