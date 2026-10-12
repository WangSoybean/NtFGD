# Assembly quality assessment

Contiguity and completeness of every genome assembly are evaluated with
**QUAST** (contiguity) and **BUSCO** (completeness, using both the
Embryophyta and eudicotyledons single-copy ortholog lineages, in genome
mode for assemblies and in transcriptome mode for the predicted CDS).

## Files

| Script | Purpose | Output |
|---|---|---|
| `1.run_quast.sh` | QUAST contiguity stats (large-genome mode) | `results/quast/<asm>/` |
| `2.run_busco_genome.sh` | BUSCO on genome FASTA (2 lineages) | `results/busco/tobacco_genome_*/` |
| `3.run_busco_cds.sh` | BUSCO on CDS FASTA (2 lineages) | `results/busco/tobacco_cds_*/` |

## Required inputs

* `data/annotation/<asm>.genome.fasta` — genome assemblies
* `data/annotation/<asm>.cds.fasta` — predicted coding sequences
* `software/busco_db/embryophyta_odb12`, `.../eudicotyledons_odb12` —
  BUSCO lineage datasets (download with `busco --download embryophyta_odb12`)

## Running

```bash
bash 1.run_quast.sh
bash 2.run_busco_genome.sh
bash 3.run_busco_cds.sh
```

All paths can be overridden with environment variables, e.g.
`GENOME_DIR=/abs/path THREADS=32 bash 2.run_busco_genome.sh`.
