#!/usr/bin/env python3
"""Download open-access PDFs for the entries in refs.bib into sources/.

An agent may only draft from a paper whose PDF is in sources/<bibkey>.pdf.
This fetches the ones that are legally free to download: arXiv papers, and
papers with an open-access copy listed by OpenAlex. It never guesses a URL
for a paywalled paper; it lists those so the human can add them.

Usage:
    python tools/fetch_pdfs.py [paper/refs.bib] [--dir sources]

Exit status is 0 even when some PDFs are missing: a missing PDF is work for
the human, not an error. Read the list it prints. It is 1 when a PDF does
not show the entry's title on its first two pages (checked with pdftotext
when it is installed), because that PDF may be a different paper.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_refs import (USER_AGENT, arxiv_id_from_doi, clean_doi, get,  # noqa: E402
                        normalize_title, parse_bib)


def openalex_pdf_urls(doi: str) -> list[str]:
    status, body = get("https://api.openalex.org/works/doi:"
                       + urllib.parse.quote(doi, safe="/")
                       + "?select=best_oa_location,locations")
    if status != 200:
        return []
    work = json.loads(body)
    locations = [work.get("best_oa_location") or {}] + (work.get("locations") or [])
    urls = []
    for loc in locations:
        url = loc.get("pdf_url")
        if url and loc.get("is_oa", True) and url not in urls:
            urls.append(url)
    return urls


def download(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except OSError:
        return None
    # Publishers often answer a PDF link with an HTML login or captcha page.
    return data if data.startswith(b"%PDF") else None


def squash(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", normalize_title(text))


def title_in_pdf(path: str, title: str) -> bool | None:
    """True if the first pages contain the title. None if pdftotext is absent.

    A repository link can point at the wrong file, and drafting from the
    wrong paper is a fabricated citation with extra steps.
    """
    if not shutil.which("pdftotext"):
        return None
    text = subprocess.run(["pdftotext", "-l", "2", path, "-"],
                          capture_output=True, text=True, errors="replace").stdout
    # Line breaks and hyphens split titles, so compare without any spacing.
    return squash(title)[:40] in squash(text)


def main() -> int:
    argv = sys.argv[1:]
    out_dir = "sources"
    if "--dir" in argv:
        i = argv.index("--dir")
        out_dir = argv[i + 1]
        del argv[i:i + 2]
    bib_path = argv[0] if argv else "paper/refs.bib"
    with open(bib_path, encoding="utf-8") as fh:
        entries = parse_bib(fh.read())
    os.makedirs(out_dir, exist_ok=True)

    missing, wrong = [], []
    for entry in entries:
        key, fields = entry["key"], entry["fields"]
        path = os.path.join(out_dir, f"{key}.pdf")
        if os.path.exists(path):
            label = {True: "have    ", False: "WRONG?  ", None: "have    "}[
                title_in_pdf(path, fields.get("title", ""))]
            print(f"  [{label}] {key}")
            if label.startswith("WRONG"):
                wrong.append(key)
            continue
        doi = clean_doi(fields.get("doi", ""))
        arxiv_id = fields.get("eprint") or arxiv_id_from_doi(doi)
        urls = [f"https://arxiv.org/pdf/{arxiv_id}"] if arxiv_id else []
        if doi and not arxiv_id:
            try:
                urls += openalex_pdf_urls(doi)
            except RuntimeError:
                pass
        data = None
        for url in urls:
            data = download(url)
            if data:
                break
            time.sleep(1)
        if data:
            with open(path, "wb") as fh:
                fh.write(data)
            ok = title_in_pdf(path, fields.get("title", ""))
            if ok is False:
                os.remove(path)
                wrong.append(key)
                print(f"  [WRONG?  ] {key}  the PDF from {url} does not show the "
                      "title; not kept")
            else:
                note = "" if ok else ", title not checked: no pdftotext"
                print(f"  [saved   ] {key}  ({len(data) // 1024} KB from {url}{note})")
        else:
            missing.append(key)
            print(f"  [missing ] {key}  no open-access PDF found")
        time.sleep(1)

    print(f"\n  {len(entries) - len(missing)} of {len(entries)} PDFs in {out_dir}/")
    if missing:
        print("\nPut these in by hand (library access), named <bibkey>.pdf:")
        for key in missing:
            print(f"  - {out_dir}/{key}.pdf")
        print("Until then, do not draft from them: write \\todo{CITE: ...} or "
              "cite them only for facts you checked yourself.")
    if wrong:
        print("\nThese PDFs do not show the entry's title on their first pages. "
              "Check them by hand:")
        for key in wrong:
            print(f"  - {key}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
