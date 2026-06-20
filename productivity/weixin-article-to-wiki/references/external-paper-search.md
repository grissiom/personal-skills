# Finding Referenced External Papers

When a WeChat article references a paper by title (e.g., "《A CPU-Centric Perspective on Agentic AI》")
but does not provide a direct URL, follow this workflow to locate and ingest it.

## Search Strategy (try in order until found)

### 1. arXiv API (best for CS/ML papers)

```bash
curl -sL --max-time 15 \
  "https://export.arxiv.org/api/query?search_query=all:KEYWORD1+AND+all:KEYWORD2&max_results=5"
```

Parse the Atom XML response for `<entry>` elements. Key fields:
- `<title>` — paper title (exact match may differ slightly from citation)
- `<id>` — arxiv identifier (e.g., `https://arxiv.org/abs/2511.00739v3`)
- `<author><name>` — authors
- `<summary>` — abstract

Example: the cited title "A CPU-Centric Perspective on Agentic AI" matched:
- arxiv title: "Towards Understanding, Analyzing, and Optimizing Agentic AI Execution: A CPU-Centric Perspective"
- arxiv ID: 2511.00739

Use broad boolean queries (`AND`/`OR`) with distinctive title words rather than exact phrase matching.

### 2. Semantic Scholar API (fallback — rate-limited)

```bash
curl -sL "https://api.semanticscholar.org/graph/v1/paper/search?query=QUERY&limit=5"
```

Has a `429 Too Many Requests` rate limit without an API key. Use only if arXiv returns nothing.

### 3. OpenAlex API (broader coverage)

```bash
curl -sL "https://api.openalex.org/works?search=QUERY"
```

Covers more disciplines but less precise for CS papers.

## Ingestion

Once the paper is found:

1. **Download PDF:**
   ```bash
   curl -sL -o "$WIKI/raw/papers/<arxiv_id>.pdf" "https://arxiv.org/pdf/<arxiv_id>"
   ```

2. **Convert to Markdown** using pymupdf4llm (preferred for CJK/English):
   ```bash
   cd "$WIKI" && .venv-pdf/bin/python -c "
   import pymupdf4llm
   md = pymupdf4llm.to_markdown('raw/papers/<id>.pdf')
   with open('raw/papers/<id>.md', 'w') as f: f.write(md)
   "
   ```

3. **Add to index** — use the `reading_notes` section with a link to the arxiv abstract page:
   ```markdown
   - [<slug>](https://arxiv.org/abs/<id>) — <full title>（<first author> et al., <year>, arXiv <id>）
     *<thesis-level summary: core finding, method, and key result>*
   ```

## Pitfalls

- **Title discrepancies**: cited titles in WeChat articles may be abbreviated or translated. Use distinctive keywords rather than exact matches.
- **arXiv API timeout**: the export.arxiv.org API sometimes times out. Retry once if it does.
- **Not a paper at all**: some quoted titles like 《联系方式》or 《AI与机器人月报》 are not academic papers — skip them without searching.
