#!/usr/bin/env python3
"""Verify every entry in a BibTeX file against public bibliographic databases.

This is the gate that stops a hallucinated citation from reaching a submission.
It mirrors what ICLR, ACL and arXiv now run on submitted papers.

For each entry it tries, in order:
  1. DOI  -> Crossref  (api.crossref.org)
  2. arXiv eprint -> arXiv API  (export.arxiv.org)
  3. Title -> OpenAlex  (api.openalex.org)

An entry passes when the record exists AND its stored title matches the title
in the database. A DOI that resolves to a different paper is still a bad
citation, so the title comparison is not optional.

Usage:
    python tools/check_refs.py [paper/refs.bib] [--no-cache] [--quiet]

Exit status is 1 if any entry fails, so it can gate a Makefile or CI job.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

# A title has to match this closely to count as the same paper.
TITLE_MATCH_THRESHOLD = 0.82
USER_AGENT = "academic-paper-kit/1.0 (reference verification; +https://github.com/tokyovo/academic-paper-kit)"
CACHE_PATH = ".cache/refs.json"
TIMEOUT = 20
PAUSE = 0.34  # be polite to the public APIs


# --------------------------------------------------------------------------
# BibTeX parsing
# --------------------------------------------------------------------------

def strip_braces(value: str) -> str:
    value = value.strip().strip(",").strip()
    while value and value[0] in "{\"" and value[-1] in "}\"":
        value = value[1:-1].strip()
    return value


def parse_bib(text: str) -> list[dict]:
    """Return a list of entries: {key, type, fields{}}.

    Written by hand so the repo needs no BibTeX library. It handles nested
    braces, quoted values and @comment/@string blocks, which is everything a
    normal refs.bib contains.
    """
    entries = []
    i = 0
    while True:
        at = text.find("@", i)
        if at == -1:
            break
        m = re.match(r"@(\w+)\s*[{(]", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        body_start = at + m.end()
        depth = 1
        j = body_start
        while j < len(text) and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        body = text[body_start:j - 1]
        i = j
        if etype in ("comment", "string", "preamble"):
            continue

        key, _, rest = body.partition(",")
        fields = {}
        pos = 0
        while pos < len(rest):
            fm = re.compile(r"\s*([A-Za-z][\w-]*)\s*=\s*").match(rest, pos)
            if not fm:
                break
            name = fm.group(1).lower()
            pos = fm.end()
            if pos < len(rest) and rest[pos] == "{":
                d, k = 1, pos + 1
                while k < len(rest) and d:
                    if rest[k] == "{":
                        d += 1
                    elif rest[k] == "}":
                        d -= 1
                    k += 1
                value, pos = rest[pos:k], k
            elif pos < len(rest) and rest[pos] == '"':
                k = pos + 1
                while k < len(rest) and rest[k] != '"':
                    k += 2 if rest[k] == "\\" else 1
                value, pos = rest[pos:k + 1], k + 1
            else:
                k = pos
                while k < len(rest) and rest[k] != ",":
                    k += 1
                value, pos = rest[pos:k], k
            fields[name] = strip_braces(value)
            while pos < len(rest) and rest[pos] in ", \n\r\t":
                pos += 1
        entries.append({"key": key.strip(), "type": etype, "fields": fields})
    return entries


# --------------------------------------------------------------------------
# Title comparison
# --------------------------------------------------------------------------

def normalize_title(title: str) -> str:
    title = re.sub(r"\$[^$]*\$", " ", title)          # drop inline math
    title = re.sub(r"\\[a-zA-Z]+", " ", title)        # drop LaTeX commands
    title = title.replace("{", " ").replace("}", " ")
    title = re.sub(r"[^a-z0-9]+", " ", title.lower())
    return " ".join(title.split())


def titles_match(a: str, b: str) -> float:
    na, nb = normalize_title(a), normalize_title(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    # A stored title is often the subtitle-free form, so containment counts.
    if na in nb or nb in na:
        return 0.95
    return SequenceMatcher(None, na, nb).ratio()


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def get(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"network error: {exc}") from exc


# --------------------------------------------------------------------------
# Lookups. Each returns (found, db_title, source, note)
# --------------------------------------------------------------------------

def clean_doi(raw: str) -> str:
    doi = raw.strip()
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi, flags=re.I)
    return doi.strip().rstrip(".")


def lookup_doi(doi: str):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    status, body = get(url)
    if status == 404:
        return False, None, "crossref", "DOI does not exist"
    if status != 200:
        return None, None, "crossref", f"HTTP {status}"
    msg = json.loads(body).get("message", {})
    titles = msg.get("title") or []
    return True, (titles[0] if titles else ""), "crossref", ""


def lookup_arxiv(eprint: str):
    arxiv_id = re.sub(r"^arxiv:", "", eprint.strip(), flags=re.I)
    arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
    url = ("http://export.arxiv.org/api/query?id_list="
           + urllib.parse.quote(arxiv_id) + "&max_results=1")
    status, body = get(url)
    if status != 200:
        return None, None, "arxiv", f"HTTP {status}"
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(body)
    entry = root.find("a:entry", ns)
    if entry is None:
        return False, None, "arxiv", "no such arXiv ID"
    title_el = entry.find("a:title", ns)
    title = " ".join((title_el.text or "").split()) if title_el is not None else ""
    # The arXiv API answers a bad ID with an entry titled "Error".
    if title.lower().startswith("error"):
        return False, None, "arxiv", "no such arXiv ID"
    return True, title, "arxiv", ""


def lookup_title(title: str):
    url = ("https://api.openalex.org/works?per-page=1&select=id,title,doi"
           "&filter=title.search:" + urllib.parse.quote(normalize_title(title)))
    status, body = get(url)
    if status != 200:
        return None, None, "openalex", f"HTTP {status}"
    results = json.loads(body).get("results") or []
    if not results:
        return False, None, "openalex", "no title match found"
    return True, (results[0].get("title") or ""), "openalex", ""


# --------------------------------------------------------------------------
# Checking one entry
# --------------------------------------------------------------------------

def check_entry(entry: dict) -> dict:
    fields = entry["fields"]
    key = entry["key"]
    title = fields.get("title", "")
    result = {"key": key, "title": title, "status": "FAIL",
              "source": "-", "detail": ""}

    if entry["type"] in ("misc", "software", "online") and not any(
            fields.get(f) for f in ("doi", "eprint", "archiveprefix")):
        if fields.get("url"):
            result.update(status="MANUAL",
                          detail="URL-only entry: open the link and confirm it yourself")
            return result

    if not title:
        result["detail"] = "entry has no title field"
        return result

    doi = fields.get("doi")
    eprint = fields.get("eprint") or fields.get("arxivid")
    try:
        if doi:
            found, db_title, source, note = lookup_doi(clean_doi(doi))
        elif eprint:
            found, db_title, source, note = lookup_arxiv(eprint)
        else:
            found, db_title, source, note = lookup_title(title)
    except RuntimeError as exc:
        result.update(status="ERROR", detail=str(exc))
        return result

    result["source"] = source
    if found is None:
        result.update(status="ERROR", detail=note)
        return result
    if not found:
        result["detail"] = note
        return result

    score = titles_match(title, db_title or "")
    if score >= TITLE_MATCH_THRESHOLD:
        result.update(status="OK", detail=f"title match {score:.2f}")
    else:
        result.update(status="MISMATCH",
                      detail=f'record exists but its title is "{db_title}" '
                             f"(match {score:.2f})")
    return result


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------

def load_cache(use_cache: bool) -> dict:
    if not use_cache or not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_cache(cache: dict, use_cache: bool) -> None:
    if not use_cache:
        return
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as fh:
        json.dump(cache, fh, indent=1, sort_keys=True)


def fingerprint(entry: dict) -> str:
    f = entry["fields"]
    return "|".join([entry["key"], f.get("title", ""), f.get("doi", ""),
                     f.get("eprint", "")])


# --------------------------------------------------------------------------

LABELS = {
    "OK": "ok      ",
    "FAIL": "NOT FOUND",
    "MISMATCH": "MISMATCH",
    "MANUAL": "manual  ",
    "ERROR": "error   ",
}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = {a for a in sys.argv[1:] if a.startswith("-")}
    path = args[0] if args else "paper/refs.bib"
    use_cache = "--no-cache" not in flags
    quiet = "--quiet" in flags

    if not os.path.exists(path):
        print(f"check-refs: no such file: {path}")
        return 1

    with open(path, encoding="utf-8", errors="replace") as fh:
        entries = parse_bib(fh.read())

    if not entries:
        print(f"check-refs: {path} has no entries yet. Nothing to verify.")
        return 0

    cache = load_cache(use_cache)
    results = []
    print(f"check-refs: verifying {len(entries)} entries in {path}\n")

    for entry in entries:
        fp = fingerprint(entry)
        cached = cache.get(fp)
        if cached and cached.get("status") in ("OK", "MANUAL"):
            result = dict(cached, key=entry["key"], detail=cached["detail"] + " (cached)")
        else:
            result = check_entry(entry)
            if result["status"] in ("OK", "MANUAL", "FAIL", "MISMATCH"):
                cache[fp] = result
            time.sleep(PAUSE)
        results.append(result)
        if not quiet or result["status"] != "OK":
            print(f"  [{LABELS[result['status']]}] {result['key']:<28} "
                  f"{result['source']:<9} {result['detail']}")

    save_cache(cache, use_cache)

    bad = [r for r in results if r["status"] in ("FAIL", "MISMATCH")]
    errors = [r for r in results if r["status"] == "ERROR"]
    manual = [r for r in results if r["status"] == "MANUAL"]

    print()
    print(f"  verified : {sum(1 for r in results if r['status'] == 'OK')}")
    print(f"  bad      : {len(bad)}")
    print(f"  manual   : {len(manual)}")
    print(f"  errors   : {len(errors)}")

    if bad:
        print("\nThese references did not check out. Do not submit until each one is\n"
              "either corrected from a real lookup or removed:\n")
        for r in bad:
            print(f"  - {r['key']}: {r['detail']}")
        print("\nA failure here is not always fabrication. Translated titles and "
              "non-English\nvenues do produce false alarms, so confirm each one by hand "
              "before deciding.")
    if errors:
        print("\nSome entries could not be checked (network or API trouble). "
              "Re-run before\nyou submit; an unchecked reference is not a verified one.")

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
