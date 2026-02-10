import re
import sys
from pathlib import Path

def parse_bibtex_entries(text: str):
    # Minimal BibTeX parser good for common entries.
    # It won’t cover every exotic BibTeX edge case, but works for typical Scholar/LaTeX exports.
    entries = []
    parts = re.split(r'(?=@\w+\s*{)', text, flags=re.M)
    for p in parts:
        p = p.strip()
        if not p.startswith("@"):
            continue
        m = re.match(r'@(\w+)\s*{\s*([^,]+)\s*,', p, flags=re.S)
        if not m:
            continue
        entry_type = m.group(1).lower()
        key = m.group(2).strip()

        body = p[m.end():].rsplit("}", 1)[0]
        fields = {}

        # Match: field = {value} OR field = "value"
        for fm in re.finditer(r'\b(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|"[^"]*")\s*,?', body, flags=re.S):
            k = fm.group(1).lower()
            v = fm.group(2).strip()
            if v.startswith("{") and v.endswith("}"):
                v = v[1:-1]
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            v = re.sub(r'\s+', ' ', v).strip()
            fields[k] = v

        entries.append({"type": entry_type, "key": key, "fields": fields})
    return entries

def bib_author_to_text(authors: str) -> str:
    # BibTeX uses "and" between authors.
    return ", ".join([a.strip() for a in authors.split(" and ") if a.strip()])

def guess_links(fields: dict) -> dict:
    # Common fields you might have: url, doi, eprint, arxiv, pdf (sometimes), code (rare)
    out = {"pdf": "", "doi": "", "code": ""}
    if "doi" in fields and fields["doi"]:
        doi = fields["doi"]
        out["doi"] = doi if doi.startswith("http") else f"https://doi.org/{doi}"
    if "url" in fields and fields["url"]:
        # If you store direct PDF in url, it will become pdf link. Otherwise keep blank.
        if fields["url"].lower().endswith(".pdf"):
            out["pdf"] = fields["url"]
    # If you use "pdf = {...}" or "file = {...}" (Zotero export)
    if "pdf" in fields and fields["pdf"]:
        out["pdf"] = fields["pdf"]
    if "file" in fields and ".pdf" in fields["file"].lower() and not out["pdf"]:
        # Zotero "file" sometimes includes a path; not usable on web. Leave blank.
        pass
    if "code" in fields and fields["code"]:
        out["code"] = fields["code"]
    return out

def yml_escape(s: str) -> str:
    s = s.replace('"', '\\"')
    return f'"{s}"'

def main():
    if len(sys.argv) != 3:
        print("Usage: bib2yml.py <input.bib> <output.yml>")
        sys.exit(2)

    bib_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    text = bib_path.read_text(encoding="utf-8", errors="replace")
    entries = parse_bibtex_entries(text)

    # Convert to YAML list for _data/publications.yml
    items = []
    for e in entries:
        f = e["fields"]
        title = f.get("title", "").strip("{} ").strip()
        if not title:
            continue

        year = f.get("year", "")
        year_num = int(re.findall(r'\d{4}', year)[0]) if re.findall(r'\d{4}', year) else 0

        authors = bib_author_to_text(f.get("author", ""))
        venue = f.get("journal") or f.get("booktitle") or f.get("publisher") or ""
        ptype = e["type"]  # article/inproceedings/etc.

        links = guess_links(f)

        items.append({
            "title": title,
            "authors": authors,
            "venue": venue,
            "year": year_num,
            "type": ptype,
            "pdf": links["pdf"],
            "doi": links["doi"],
            "code": links["code"],
        })

    # Sort newest first
    items.sort(key=lambda x: x.get("year", 0), reverse=True)

    lines = []
    for it in items:
        lines.append("- title: " + yml_escape(it["title"]))
        lines.append("  authors: " + yml_escape(it["authors"]))
        lines.append("  venue: " + yml_escape(it["venue"]))
        lines.append(f"  year: {it['year']}")
        lines.append("  type: " + yml_escape(it["type"]))
        lines.append("  pdf: " + yml_escape(it["pdf"]))
        lines.append("  doi: " + yml_escape(it["doi"]))
        lines.append("  code: " + yml_escape(it["code"]))
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
