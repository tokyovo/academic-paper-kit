---
name: find-literature
description: Find and add verified references for any subject. Use when the paper needs a source, when a \todo{CITE} marker needs resolving, or when the user asks for background reading on a topic. Never produces a reference from memory.
---

# Find literature

Your job is to turn a research question into verified entries in
`paper/refs.bib` and PDFs in `sources/`. This works for any field: the search
APIs cover all of them.

## Steps

1. Turn the need into two or three search phrases in the field's own
   vocabulary. If the subject is unfamiliar, ask the user for the terms their
   field uses. Do not guess at jargon.

2. Search. Use whichever of these is available:

   - `make find-refs Q="<phrase>"` — OpenAlex title search, all disciplines.

   - A Zotero MCP server, if the user has one connected, to search their own
     library first.

   - A web search tool for recent work, then confirm each hit with
     `make find-refs Q=<doi>`.

3. For each candidate, report to the user: title, authors, year, venue, DOI.
   Do not add anything to `refs.bib` until the user has seen the list.

4. Add the ones the user approves:
   `make find-refs Q=<doi> ` appends a real entry.

5. Ask the user to put the PDF in `sources/<bibkey>.pdf`. You may only draft
   from a paper whose PDF is there.

6. Run `make check-refs`. It must pass.

## Rules

- Every field of every entry comes from a lookup. If a lookup fails, say so
  and leave `\todo{CITE: ...}` in the manuscript.

- A search result is a candidate, not a citation. The user decides what gets
  cited, because citing means having read it.

- Never fill a gap with a paper you believe exists. The model failure rate on
  recalled citations is between 14% and 95%.
