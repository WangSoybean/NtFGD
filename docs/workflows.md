# Workflow descriptions

This document describes each workflow, its inputs/outputs and the
software versions used, so that the analysis can be reproduced
independently.

All paths and parameters are read from `config/config.yaml`; the shell
scripts expose the important values as environment variables, so a run
can be overridden without editing files, e.g.
`PROTEIN_DIR=/abs/path THREADS=32 bash annotation/1.run_eggnog_mapper.sh`.

The software versions below are those reported in the **Methods section
of the manuscript (Manuscript-v7)**. See the note at the end of this file
for three places where the manuscript wording and the working notes do
not agree.

---

## 0. Literature mining (`literature_mining/`)

`1.get_pubmed.py` downloads plant gene-function records from PubMed
(NCBI E-utilities) year by year. `2.merge_pubmed.py` validates and merges
the yearly TSVs. `3.run_breeding_evaluation.py` sends each record to
Qwen3-14B through a LangFlow pipeline with the tobacco breeding-target
prompt (`config/Prompt.txt`) restricted to the trait ontology in
`config/StructuredTobaccoBreedingTraitOntology.json`, and stores valid
results in `breeding_results.db`. `4.build_tobacco_breeding_db.py` joins
those results with the literature metadata and produces
`tobacco_breeding_knowledge.db` and `target_statistics.json`. The
gene-trait network is then laid out in Cytoscape.

> The LLM credentials are supplied via `BREEDING_API_KEY` /
> `BREEDING_API_URL` environment variables (see `SECURITY.md`).

## 1. Assembly quality assessment (`assembly_qc/`)

| Step | Tool | Input | Output |
|---|---|---|---|
| Contiguity | QUAST v5.3.0 | `<asm>.genome.fasta` | `results/quast/<asm>/` |
| Completeness (genome) | BUSCO v6.0.0, eudicotyledons_odb12 (+ embryophyta_odb12) | `<asm>.genome.fasta` | `results/busco/tobacco_genome_*/` |
| Completeness (CDS) | BUSCO v6.0.0, eudicotyledons_odb12 (+ embryophyta_odb12) | `<asm>.cds.fasta` | `results/busco/tobacco_cds_*/` |

Metrics: total assembly size, number of contigs/scaffolds, contig and
scaffold N50, largest scaffold, GC content and gap proportion (QUAST);
complete (single-copy / duplicated), fragmented and missing orthologs
(BUSCO). BUSCO is run offline (`--offline`) against the Odb12 lineage
sets; MultiQC aggregates the QUAST report with the fastp/STAR QC reports.

## 2. Functional annotation (`annotation/`)

| Step | Tool | Output |
|---|---|---|
| eggNOG | eggNOG-mapper v2.1.13 (DIAMOND, `--tax_scope Viridiplantae`, Pfam realign, ortholog reporting) | `<name>.emapper.annotations` |
| Domains | InterProScan v5.77 (`-t p -goterms -iprlookup -pa`) | `<name>.tsv` |
| Homology | BLAST+ v2.17.0, BLASTP vs UniProt/Swiss-Prot (E ≤ 1e-5, best hit by bit score) | `<name>.swissprot.blastp.tsv` |
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

> **Manuscript wording.** The Methods describe this step as "MCScanX
> collinearity analysis … verified by BLASTP similarity searches". The
> code actually run (see `docs/methods_notes_original.txt`) uses
> `jcvi.compara.catalog` — which drives **LAST** internally — plus a LAST
> fallback. Please reconcile the Methods text with the code (see the
> note at the end of this file).

## 4. RNA-seq quantification (`rnaseq/`)

SRA Toolkit v3.30 (`fastq-dump`) → fastp v1.1.0 (QC) → STAR v2.7.11b
(alignment against the SR1 and ZY300 reference indices, shared-memory
genome loading) → featureCounts v2.1.1 from the Subread package
(`-p --countReadPairs -t exon -g transcript_id --primary`) → downstream
Python steps:

* `3.parse_star_log.py` — STAR mapping summary;
* `4.format_featurecounts_summary.py` — featureCounts summary → DB table;
* `5.merge_summary.py` — combined QC table (`RNAseq_QC.csv`);
* `6.gene_counts_qc.py` — CPM filter (CPM ≥ 1 in ≥ 1 sample), log2(CPM+1),
  PCA + Pearson correlation clustered heatmap;
* `7.count_tpm_fpkm.py` — clean counts, FPKM, TPM.

Downstream differential expression: DESeq2 v1.50.0 in R v4.5 (Wald test,
apeglm log2FC shrinkage, FDR < 0.05 and |log2FC| > 1); enrichment with
clusterProfiler v4.18.4 against `go-basic.obo` (GO) and `ko2name.txt`
(KEGG); figures with ggplot2 / pheatmap / enrichplot.

## 5. Gene-model statistics (`genome_annotation_stats/`)

* `1.extract_gene_locations.sh` — normalised gene locations from GFF3
  (gene chromosomal positions; tool: `Genes_on_Chr`).
* `2.parse_genetic_information.py` — gene length, CDS/protein length and
  protein physicochemical properties (pI, MW, instability index,
  aromaticity, GRAVY, molar extinction coefficient).
* `3.extract_sequences.py` — genomic sequence extraction for a gene set.

## 6. sgRNA design (`sgrna_design/`)

`GuideScan`-based: `generate_kmers.py` → filtering → `guidescan
enumerate` → off-target summary → JSON + CSV.
`sgrna_pipeline_for_geneID.py`: per-gene sgRNA JSON from the SQLite
database for the website.

> The manuscript does not name GuideScan; it refers to "an integrated
> sgRNA design module". Keeping the tool name in the code is fine, but it
> should be mentioned in the Methods for full traceability.

---

## Software versions

Versions exactly as stated in the manuscript Methods (Manuscript-v7).

| Tool | Version | Where it is used |
|---|---|---|
| NCBI SRA Toolkit | v3.30 | RNA-seq (FASTQ conversion) |
| fastp | v1.1.0 | RNA-seq (QC / trimming) |
| STAR | v2.7.11b | RNA-seq (alignment) |
| featureCounts (Subread) | v2.1.1 | RNA-seq (read counting) |
| QUAST | v5.3.0 | Assembly quality (contiguity) |
| BUSCO | v6.0.0 | Assembly quality (completeness) |
| eggNOG-mapper | v2.1.13 | Functional annotation |
| InterProScan | v5.77 | Functional annotation (domains) |
| BLAST+ (BLASTP) | v2.17.0 | Annotation (Swiss-Prot) & gene-ID conversion |
| MCScanX | not stated | Synteny / gene-ID conversion |
| JCVI toolkit | not stated | Synteny plots / karyotype |
| DESeq2 | v1.50.0 | Differential expression |
| R | v4.5 | Differential expression / enrichment |
| clusterProfiler | v4.18.4 | GO / KEGG enrichment |
| Genes_on_Chr | not stated | Gene chromosomal positions |
| SequenceServer | v3.0.1 | Web BLAST service |
| JBrowse | 2 | Genome browser |
| Cytoscape | not stated | Gene-trait network |
| Qwen3-14B | — | Literature mining (LLM) |
| Django / Vue 3 / SQLite3 | not stated | Web platform |

Tools that appear in the code / working notes but are **not named in the
manuscript** (they must still be listed in the Methods for the counts to
be traceable):

| Tool | Version | Where it is used |
|---|---|---|
| LAST | not stated | `jcvi.compara.catalog` and `3.run_last.sh` |
| GuideScan | not stated | sgRNA design |
| MultiQC | not stated | QC report aggregation |

---

## Known manuscript-vs-code discrepancies (please reconcile)

These were found while transcribing versions out of the manuscript and
should be resolved before the revision is submitted:

1. **Gene-ID conversion method.** Methods: "MCScanX collinearity … verified
   by BLASTP". Code/notes: `jcvi.compara.catalog` (LAST-based) + LAST
   fallback. Either name MCScanX **and** LAST/jcvi in the Methods, or
   change the text to describe the jcvi/LAST pipeline that was run.
2. **InterProScan version.** Methods: v5.77. Working notes:
   `interproscan-5.76-107.0`. One of the two is wrong.
3. **QUAST / BUSCO settings.** Methods: QUAST "with default parameters"
   and BUSCO in genome mode against `eudicotyledons_odb12`. Notes:
   `quast.py --large` and BUSCO against **both** `embryophyta_odb12` and
   `eudicotyledons_odb12` (plus transcriptome mode on the CDS). State the
   parameters actually used.
4. **sgRNA design tool.** Code uses GuideScan; the Methods do not name it.
5. **Ontology file.** Methods cite `StructuredTobaccoBreedingTraitOntology.json`;
   the repository now ships exactly that filename (see
   `docs/ontology_note.md`).
