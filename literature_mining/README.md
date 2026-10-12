# Literature mining & tobacco-breeding knowledge base

Harvests the plant gene-function literature from PubMed, then uses an LLM
to decide whether each study is relevant to tobacco breeding and to
extract the matched breeding targets with supporting evidence. The
results are assembled into a queryable knowledge base.

```
1.get_pubmed.py               PubMed  →  plant_gene_function_<year>.tsv
        │
2.merge_pubmed.py             validate + merge → meraged_plant_gene_function.tsv
        │
3.run_breeding_evaluation.py  LLM curation     → breeding_results.db
        │
4.build_tobacco_breeding_db.py  join metadata → tobacco_breeding_knowledge.db
                                              → target_statistics.json
```

## Files

| Script | Purpose |
|---|---|
| `1.get_pubmed.py` | Download PubMed records year by year |
| `2.merge_pubmed.py` | Validate & merge the yearly TSVs |
| `3.run_breeding_evaluation.py` | LLM-based breeding-relevance curation |
| `4.build_tobacco_breeding_db.py` | Build the target knowledge base + statistics |
| `config/Prompt.txt` | LLM prompt template (defines the output JSON schema) |
| `config/StructuredTobaccoBreedingTargetSystem.json` | Primary / secondary / tertiary breeding-target list |

`1.get_pubmed.py`, `3.run_breeding_evaluation.py` and
`4.build_tobacco_breeding_db.py` were originally UTF-8; `2.merge_pubmed.py`
was GBK-encoded and has been re-saved as UTF-8. All code logic is
unchanged; comments are in English and a shebang/header was added.

## Running

```bash
pip install requests lxml tqdm pandas openpyxl

python 1.get_pubmed.py
python 2.merge_pubmed.py

# the LLM endpoint requires credentials (see below)
export BREEDING_API_KEY="<your key>"
export BREEDING_API_URL="https://<host>/api/v1/run/<flow-id>"
python 3.run_breeding_evaluation.py

python 4.build_tobacco_breeding_db.py
```

## ⚠️ Security — API key

`3.run_breeding_evaluation.py` reads the model API key and endpoint from
the environment (`BREEDING_API_KEY`, `BREEDING_API_URL`). **Do not
hard-code them.** Earlier versions of the repository contained a
hard-coded key; if that key is still active it must be **revoked and
rotated**. See the repository root `SECURITY.md`.

## Notes on inputs not produced here

`4.build_tobacco_breeding_db.py` expects a `literature.db` containing a
`literature_metadata` table (`pmid, doi, title, abstract, pub_date,
journal`). If that database is built elsewhere in your workflow, record
how it is produced so the pipeline is reproducible end to end.

## Dependencies

`requests`, `lxml`, `tqdm`, `pandas`, `openpyxl`.
