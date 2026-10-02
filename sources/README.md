# Sources

Put the PDFs you are citing here, one file per reference, named after its
BibTeX key: `bender2021dangers.pdf`.

Two rules:

- An agent may only draft from what is in this folder or in your Zotero
  library. It may not draft from what it remembers about a paper.

- If you have not read a paper, do not cite it. A citation says you read it.

PDFs are not committed to git (see `.gitignore`), so this folder stays local.
Keep the bibliography as the shared record instead.

## Getting a reference in

```
make find-refs Q=10.1145/3442188.3445922      # by DOI
make find-refs Q=arXiv:1706.03762             # by arXiv ID
make find-refs Q="attention is all you need"  # by title
```

Or export from Zotero with Better BibTeX straight into `paper/refs.bib`.
Either way, `make check-refs` has to pass afterwards.
