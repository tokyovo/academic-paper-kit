#!/usr/bin/env python3
"""Look up a reference and print a BibTeX entry built from real metadata.

This is the only approved way for an agent to add an entry to refs.bib.
It never composes a reference from memory: every field comes from Crossref,
arXiv or OpenAlex.

Usage:
    python tools/find_refs.py 10.1145/3442188.3445922
    python tools/find_refs.py arXiv:1706.03762
    python tools/find_refs.py "attention is all you need"
    python tools/find_refs.py "..." --append        # write to paper/refs.bib

With a title, it prints the top three candidates and you pick one. It will
not append on a title search unless exactly one candidate is returned, so a
human or agent always sees what is being added.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_refs import clean_doi, get, normalize_title  # noqa: E402

BIB_PATH = "paper/refs.bib"


def surname(author: str) -> str:
    author = author.strip()
    if "," in author:
        return author.split(",")[0].strip()
    return author.split()[-1] if author.split() else "anon"


def make_key(authors: list[str], year: str, title: str) -> str:
    first = re.sub(r"[^a-z]", "", surname(authors[0]).lower()) if authors else "anon"
    words = [w for w in normalize_title(title).split()
             if w not in ("a", "an", "the", "on", "of", "for", "and", "in", "to", "is")]
    word = words[0] if words else "paper"
    return f"{first}{year or 'nd'}{word}"


def fmt(entry_type: str, key: str, fields: dict) -> str:
    width = max(len(f) for f in fields)
    lines = [f"@{entry_type}{{{key},"]
    for name, value in fields.items():
        if value:
            lines.append(f"  {name.ljust(width)} = {{{value}}},")
    lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def from_crossref(doi: str) -> str | None:
    status, body = get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
    if status != 200:
        print(f"find-refs: Crossref has no record for DOI {doi} (HTTP {status}).")
        print("Do not invent this reference. Check the DOI with the publisher.")
        return None
    m = json.loads(body)["message"]
    authors = [f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
               for a in m.get("author", []) if a.get("family")]
    year = ""
    for part in ("published-print", "published-online", "issued", "created"):
        parts = (m.get(part) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            year = str(parts[0][0])
            break
    title = (m.get("title") or [""])[0]
    kind = m.get("type", "")
    entry_type = {"proceedings-article": "inproceedings",
                  "book-chapter": "incollection",
                  "book": "book"}.get(kind, "article")
    container = (m.get("container-title") or [""])[0]
    fields = {
        "title": title,
        "author": " and ".join(authors),
        "booktitle" if entry_type == "inproceedings" else "journal": container,
        "volume": m.get("volume", ""),
        "number": m.get("issue", ""),
        "pages": m.get("page", ""),
        "year": year,
        "publisher": m.get("publisher", ""),
        "doi": m.get("DOI", doi),
    }
    return fmt(entry_type, make_key(authors, year, title), fields)


def from_arxiv(arxiv_id: str) -> str | None:
    arxiv_id = re.sub(r"^arxiv:", "", arxiv_id, flags=re.I)
    status, body = get("http://export.arxiv.org/api/query?max_results=1&id_list="
                       + urllib.parse.quote(arxiv_id))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    if status != 200:
        print(f"find-refs: arXiv lookup failed (HTTP {status}).")
        return None
    entry = ET.fromstring(body).find("a:entry", ns)
    title_el = entry.find("a:title", ns) if entry is not None else None
    title = " ".join((title_el.text or "").split()) if title_el is not None else ""
    if entry is None or not title or title.lower().startswith("error"):
        print(f"find-refs: no arXiv paper with ID {arxiv_id}. Do not invent it.")
        return None
    authors = []
    for a in entry.findall("a:author", ns):
        name_el = a.find("a:name", ns)
        if name_el is not None and name_el.text:
            parts = name_el.text.split()
            authors.append(f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1
                           else name_el.text)
    pub = entry.find("a:published", ns)
    year = (pub.text or "")[:4] if pub is not None else ""
    doi_el = entry.find("a:doi", ns)
    fields = {
        "title": title,
        "author": " and ".join(authors),
        "journal": "arXiv preprint",
        "year": year,
        "eprint": re.sub(r"v\d+$", "", arxiv_id),
        "archiveprefix": "arXiv",
        "doi": (doi_el.text if doi_el is not None else ""),
    }
    return fmt("article", make_key(authors, year, title), fields)


def search_openalex(title: str) -> list[dict]:
    url = ("https://api.openalex.org/works?per-page=3"
           "&select=title,doi,publication_year,authorships,type,primary_location"
           "&filter=title.search:" + urllib.parse.quote(normalize_title(title)))
    status, body = get(url)
    if status != 200:
        print(f"find-refs: OpenAlex search failed (HTTP {status}).")
        return []
    return json.loads(body).get("results") or []


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    append = "--append" in sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    query = " ".join(args)

    if re.match(r"^(https?://(dx\.)?doi\.org/|doi:)?10\.\d{4,9}/", query, re.I):
        entry = from_crossref(clean_doi(query))
    elif re.match(r"^(arxiv:)?\d{4}\.\d{4,5}(v\d+)?$", query, re.I):
        entry = from_arxiv(query)
    else:
        results = search_openalex(query)
        if not results:
            print(f'find-refs: nothing found for "{query}".')
            print("Write \\todo{CITE: ...} in the manuscript instead of guessing.")
            return 1
        print(f'Candidates for "{query}":\n')
        for n, r in enumerate(results, 1):
            doi = (r.get("doi") or "").replace("https://doi.org/", "") or "no DOI"
            print(f"  {n}. {r.get('title')}")
            print(f"     {r.get('publication_year')} · {doi}\n")
        if len(results) > 1:
            print("More than one candidate. Re-run with the DOI of the right one.")
            return 0
        doi = (results[0].get("doi") or "").replace("https://doi.org/", "")
        if not doi:
            print("The only candidate has no DOI. Import it through Zotero instead.")
            return 1
        entry = from_crossref(doi)

    if not entry:
        return 1

    print(entry)
    if append:
        key = entry.split("{", 1)[1].split(",", 1)[0]
        existing = ""
        if os.path.exists(BIB_PATH):
            with open(BIB_PATH) as fh:
                existing = fh.read()
        if f"{{{key}," in existing:
            print(f"\nfind-refs: {key} is already in {BIB_PATH}. Nothing appended.")
            return 0
        with open(BIB_PATH, "a") as fh:
            fh.write(("\n" if existing.strip() else "") + entry + "\n")
        print(f"\nfind-refs: appended {key} to {BIB_PATH}. "
              f"Now run: make check-refs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
