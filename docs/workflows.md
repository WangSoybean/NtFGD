# Workflow descriptions

This document describes each workflow, its inputs/outputs and the
software versions used, so that the analysis can be reproduced
independently.

All paths and parameters are read from `config/config.yaml`; the shell
scripts expose the important values as environment variables, so a run
can be overridden without editing files, e.g.
`PROTEIN_DIR=/abs/path THREADS=32 bash annotation/1.run_eggnog_mapper.sh`.

---

## 0. Literature mining (`literature_mining/`)

`1.get_pubmed.py` downloads plant gene-function records from PubMed
(NCBI E-utilities) year by year. `2.merge_pubmed.py` validates and merges
the yearly TSVs. `3.run_breeding_evaluation.py` sends each record to an
LLM with the tobacco breeding-target prompt
(`config/Prompt.txt`) restricted to the target list in
`config/StructuredTobaccoBreedingTargetSystem.json`, stores valid results
in `breeding_results.db`. `4.build_tobacco_breeding_db.py` joins those
results with the literature metadata and produces
`tobacco_breeding_knowledge.db` and `target_statistics.json`.

> The LLM credentials are supplied via `BREEDING_API_KEY` /
> `BREEDING_API_URL` environment variables (see `SECURITY.md`).

## 1. Assembly quality assessment (`assembly_qc/`)

| Step | Tool | Input | Output |
|---|---|---|---|
| Contiguity | QUAST (`--large`) | `<asm>.genome.fasta` | `results/quast/<asm>/` |
| Completeness (genome) | BUSCO, Embryophyta + eudicots | `<asm>.genome.fasta` | `results/busco/tobacco_genome_*/` |
| Completeness (CDS) | BUSCO, Embryophyta + eudicots | `<asm>.cds.fasta` | `results/busco/tobacco_cds_*/` |

BUSCO is run offline (`--offline`) against `embryophyta_odb12` and
`eudicotyledons_odb12`; MultiQC aggregates the QUAST report with the
fastp/STAR QC reports.

## 2. Functional annotation (`annotation/`)

| Step | Tool | Output |
|---|---|---|
| eggNOG | eggNOG-mapper 2.1.13 (DIAMOND, `--tax_scope Viridiplantae`, Pfam realign, ortholog reporting) | `<name>.emapper.annotations` |
| Domains | InterProScan 5.76-107.0 (`-t p -goterms -iprlookup -pa`) | `<name>.tsv` |
| Homology | BLASTP vs UniProt/Swiss-Prot (E ≤ 1e-5) | `<name>.swissprot.blastp.tsv` |
| Merge | `4.merge_eggnog_interproscan.py` | `<name>.annotation` |

## 3. Gene-ID conversion (`gene_id_conversion/`)

1. `1.prepare_jcvi_inputs.sh` — derive `<asm>.bed` (gene coordinates)
   and `<asm>.cds` (transcript suffixes stripped) from the GFF3/CDS.
2. `2.run_jcvi_synteny.sh` — all-vs-all `jcvi.compara.catalog ortholog`
   (`--cscore 0.99`) followed by `compara.synteny screen`
   (`--minspan 30 --simple`).
3. `3.run_last.sh` — LAST whole-transcriptome alignment, reduced to the
   best hit per query (`<pair>.last.filtered`).
4. `4.convert_gene_ids.py` — merge synteny anchors (primary) with the
   LAST fallback into `<a>.<b>.gene_conversion.tsv`
   (`query_gene, hit_gene, method, score, identity, aln_len`).
5. `5.plot_karyotype.sh` — `jcvi.graphics.karyotype seqids layout`.

## 4. RNA-seq quantification (`rnaseq/`)

fastp (QC) → STAR (alignment against each reference index, shared-memory
genome loading) → featureCounts (`-p --countReadPairs -t exon
-g transcript_id --primary`) → downstream Python steps:

* `3.parse_star_log.py` — STAR mapping summary;
* `4.format_featurecounts_summary.py` — featureCounts summary → DB table;
* `5.merge_summary.py` — combined QC table (`RNAseq_QC.csv`);
* `6.gene_counts_qc.py` — CPM filter (CPM ≥ 1 in ≥ 1 sample), log2(CPM+1),
  PCA + Pearson correlation clustered heatmap;
* `7.count_tpm_fpkm.py` — clean counts, FPKM, TPM.

## 5. Gene-model statistics (`genome_annotation_stats/`)

* `1.extract_gene_locations.sh` — normalised gene locations from GFF3.
* `2.parse_genetic_information.py` — gene length, CDS/protein length and
  protein physicochemical properties (pI, MW, instability index,
  aromaticity, GRAVY, molar extinction coefficient).
* `3.extract_sequences.py` — genomic sequence extraction for a gene set.

## 6. sgRNA design (`sgrna_design/`)

`sgrna_pipeline.py`: `generate_kmers.py` → filtering → `guidescan
enumerate` → off-target summary → JSON + CSV.
`sgrna_pipeline_for_geneID.py`: per-gene sgRNA JSON from the SQLite
database for the website.

---

## Software versions

| Tool | Version used |
|---|---|
| fastp | (fill in) |
| STAR | (fill in) |
| featureCounts (Subread) | (fill in) |
| QUAST | (fill in) |
| BUSCO | (fill in) |
| eggNOG-mapper | 2.1.13 |
| InterProScan | 5.76-107.0 |
| BLAST+ | (fill in) |
| LAST | (fill in) |
| MCScanX / jcvi | (fill in) |
| GuideScan | (fill in) |
| Python | 3.10 |

Record the exact versions used for the manuscript release so the reported
numbers can be reproduced.
