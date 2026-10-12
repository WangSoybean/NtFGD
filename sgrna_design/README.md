# sgRNA design (GuideScan)

Designs and scores sgRNAs for CRISPR targets and packages them for the
web database.

| Script | Purpose |
|---|---|
| `1.run_guidescan.sh` | example wrapper around `sgrna_pipeline.py` |
| `sgrna_pipeline.py` | kmers → filtering → off-target enumeration → summary → JSON/CSV |
| `sgrna_pipeline_for_geneID.py` | per-gene sgRNA JSON from the SQLite database |

## `sgrna_pipeline.py`

```
generate_kmers.py  →  filter  →  guidescan enumerate  →  summarize  →  JSON + CSV
```

Usage:

```bash
python sgrna_pipeline.py <input.fasta> <genome.index> <prefix> <pam> <mismatch>
# example:
python sgrna_pipeline.py Input.fasta genome.fasta.index sgRNA NGG 1
```

Filtering rules applied to each 20-nt candidate:
* GC content 20–80 %;
* no `N`;
* no homopolymer run ≥ 4 (`A/T/C/G`);
* no dinucleotide repeat ≥ 4 (`AT/TA/CG/GC`);
* no `TTTT`;
* PAM-proximal 12-nt seed GC 20–80 %.

Set `GUIDESCAN_BIN` and `GENERATE_KMERS` in the CONFIG block at the top
of the script to your GuideScan installation.

## `sgrna_pipeline_for_geneID.py`

Reads a per-gene table (`Input.xls`) plus the genome SQLite database
(`<GenomeName>.db`, table `sgrna`) and writes `sgRNA.json` (gDNA + CDS +
sgRNA annotations) and `sgRNA.table.csv`.

```bash
python sgrna_pipeline_for_geneID.py --GenomeName <assembly>
```

## Dependencies

GuideScan (with `generate_kmers.py`), `pandas`. `sgrna_pipeline_for_geneID.py`
additionally needs `sqlite3` (standard library).
