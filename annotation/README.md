# Functional annotation

Every predicted protein set is annotated with three complementary tools
and the eggNOG + InterProScan results are merged into a single per-gene
annotation table.

| Script | Tool | Output |
|---|---|---|
| `1.run_eggnog_mapper.sh` | eggNOG-mapper v2.1.13 (DIAMOND mode) | `work/emapper_out/<name>.emapper.annotations` |
| `2.run_interproscan.sh` | InterProScan v5.77 | `work/interproscan_out/<name>.tsv` |
| `3.run_blastp_uniprot.sh` | BLASTP v2.17.0 vs UniProt/Swiss-Prot (E ≤ 1e-5) | `work/blastp_out/<name>.swissprot.blastp.tsv` |
| `4.merge_eggnog_interproscan.py` | merge eggNOG + InterProScan | `<name>.annotation` |

## Running

```bash
bash 1.run_eggnog_mapper.sh
bash 2.run_interproscan.sh
bash 3.run_blastp_uniprot.sh

# merge per assembly (example)
python 4.merge_eggnog_interproscan.py \
    -e work/emapper_out/<name>.emapper \
    -i work/interproscan_out/<name>.tsv \
    -o <name>.annotation
```

## Required inputs

* `data/annotation/<asm>.pep.fasta` — predicted proteins
* eggNOG database (`EGGNOG_DATA_DIR`), an InterProScan installation, and
  a Swiss-Prot BLAST database (auto-downloaded by `3.run_blastp_uniprot.sh`
  if missing).

## `4.merge_eggnog_interproscan.py`

Reads the eggNOG `#query` header (version-agnostic) and the 15-column
InterProScan TSV, aggregates InterPro domains / pathways / GO terms per
gene, and merges the two tables on the gene ID. GO terms from both
sources are combined and de-duplicated in the `GO_combined` column.
