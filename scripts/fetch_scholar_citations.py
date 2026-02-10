# scripts/fetch_scholar_citations.py
import sys
import time
import traceback
from pathlib import Path

import yaml
from scholarly import scholarly

TIMEOUT_SECONDS = 60  # hard stop

def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_scholar_citations.py SCHOLAR_ID")
        return 1

    scholar_id = sys.argv[1]
    out_path = Path("_data/citations.yml")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    start = time.time()
    try:
        author = scholarly.search_author_id(scholar_id)

        if time.time() - start > TIMEOUT_SECONDS:
            raise TimeoutError("Timeout while searching author")

        author = scholarly.fill(author, sections=["counts"])

        if time.time() - start > TIMEOUT_SECONDS:
            raise TimeoutError("Timeout while filling counts")

        cites = author.get("cites_per_year", {})
        if not cites:
            raise RuntimeError("No cites_per_year returned (possibly blocked)")

        data = [{"year": int(y), "count": int(c)} for y, c in sorted(cites.items(), reverse=True)]

        # Write YAML
        out_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        print(f"Updated {out_path} with {len(data)} years.")
        return 0

    except Exception as e:
        print("ERROR: Google Scholar fetch failed.")
        print("Reason:", repr(e))
        print("Traceback:")
        traceback.print_exc()

        # IMPORTANT: Don't break your site build. Keep last known citations.yml.
        # Exit 0 so workflow succeeds even if Scholar blocks today.
        if out_path.exists():
            print(f"Keeping existing {out_path} (not overwritten).")
        else:
            print(f"{out_path} does not exist yet. Creating a placeholder.")
            out_path.write_text(yaml.safe_dump([], sort_keys=False), encoding="utf-8")
        return 0  # <-- Do NOT fail the workflow

if __name__ == "__main__":
    sys.exit(main())
