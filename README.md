# Nicotiana breeding-genomics analysis code

Code accompanying the manuscript *"&lt; manuscript title &gt;"*. It covers
the full analysis chain from public-literature mining, through genome
assembly quality assessment, functional annotation, cross-assembly
gene-ID conversion and RNA-seq quantification, to CRISPR sgRNA design.

This repository is organised so that the **RNA-seq, annotation,
assembly-quality and gene-ID-conversion workflows described in the
Methods are all present and runnable**, each reading its inputs from a
single configuration file.

---

## Workflows ↔ manuscript Methods

| Manuscript Methods section | Directory | Entry point |
|---|---|---|
| Literature mining / breeding database | [`literature_mining/`](literature_mining/) | `1.get_pubmed.py` … `4.build_tobacco_breeding_db.py` |
| Assembly quality (contiguity, completeness) | [`assembly_qc/`](assembly_qc/) | `1.run_quast.sh`, `2.run_busco_genome.sh`, `3.run_busco_cds.sh` |
| Functional annotation | [`annotation/`](annotation/) | `1.run_eggnog_mapper.sh`, `2.run_interproscan.sh`, `3.run_blastp_uniprot.sh`, `4.merge_eggnog_interproscan.py` |
| Gene-ID conversion / synteny | [`gene_id_conversion/`](gene_id_conversion/) | `1.prepare_jcvi_inputs.sh` … `4.convert_gene_ids.py` |
| RNA-seq mapping & quantification | [`rnaseq/`](rnaseq/) | `0.run_fastp.sh` … `run_pipeline.sh` |
| Gene-model statistics & sequences | [`genome_annotation_stats/`](genome_annotation_stats/) | `1.extract_gene_locations.sh`, `2.parse_genetic_information.py`, `3.extract_sequences.py` |
| sgRNA design | [`sgrna_design/`](sgrna_design/) | `sgrna_pipeline.py`, `sgrna_pipeline_for_geneID.py` |

See [`docs/workflows.md`](docs/workflows.md) for a description of each
step and the **exact software versions** (transcribed from the manuscript
Methods), plus a short list of manuscript-vs-code discrepancies that
still need to be reconciled before submission.

---

## Repository structure

```
.
├── README.md                     ← this file
├── SECURITY.md                   ← credential-handling note (read this)
├── LICENSE
├── CITATION.cff
├── environment.yml               ← conda environment
├── requirements.txt              ← Python dependencies
├── config/
│   ├── config.example.yaml       ← ALL paths & parameters (copy → config.yaml)
│   └── samples.example.tsv       ← sample-sheet template
├── docs/
│   ├── workflows.md              ← per-workflow description
│   ├── ontology_note.md          ← ontology-filename clarification
│   ├── release_checklist.md      ← steps to cut a manuscript release
│   └── methods_notes_original.txt← raw working notes (provenance)
├── literature_mining/            ← PubMed harvesting → breeding DB
├── assembly_qc/                  ← QUAST / BUSCO
├── annotation/                   ← eggNOG-mapper / InterProScan / BLASTP
├── gene_id_conversion/           ← jcvi synteny + LAST → conversion tables
├── rnaseq/                       ← fastp / STAR / featureCounts → counts, TPM, FPKM
├── genome_annotation_stats/      ← gene locations & protein properties
└── sgrna_design/                 ← GuideScan sgRNA design
```

---

## Installation

```bash
# Python environment
conda env create -f environment.yml
conda activate nt-breeding
# (or) pip install -r requirements.txt

# Configuration: copy the template and edit the paths
cp config/config.example.yaml config/config.yaml
cp config/samples.example.tsv  config/samples.tsv
```

External command-line tools (STAR, featureCounts, fastp, QUAST, BUSCO,
eggNOG-mapper, InterProScan, BLAST+, LAST, MCScanX/jcvi, GuideScan) are
installed separately; versions are listed in `docs/workflows.md`.

---

## Quick start

```bash
# 1) Assembly quality
bash assembly_qc/1.run_quast.sh
bash assembly_qc/2.run_busco_genome.sh
bash assembly_qc/3.run_busco_cds.sh

# 2) Annotation
bash annotation/1.run_eggnog_mapper.sh
bash annotation/2.run_interproscan.sh
bash annotation/3.run_blastp_uniprot.sh

# 3) Gene-ID conversion
bash gene_id_conversion/1.prepare_jcvi_inputs.sh
bash gene_id_conversion/2.run_jcvi_synteny.sh
python gene_id_conversion/4.convert_gene_ids.py

# 4) RNA-seq
bash rnaseq/0.run_fastp.sh
bash rnaseq/1.run_star.sh
bash rnaseq/2.run_featurecounts.sh
cd work/<index> && bash /path/to/rnaseq/run_pipeline.sh

# 5) sgRNA design
bash sgrna_design/1.run_guidescan.sh
```

---

## Response to reviewer comments

**1. "…the RNA-seq, annotation, assembly-quality, and gene ID conversion
workflows … were not present."**
These four workflows are now included as top-level directories
(`rnaseq/`, `annotation/`, `assembly_qc/`, `gene_id_conversion/`), each
with a README describing inputs/outputs and a scripted, parameterised
entry point. The mapping from manuscript Methods sections to code is the
table above.

**2. "The ontology filename in the Methods also differs from the file in
the repository."**
Resolved. The Methods cite `StructuredTobaccoBreedingTraitOntology.json`
while the repository shipped `config/StructuredTobaccoBreedingTargetSystem.json`;
the repository file has been **renamed to the manuscript name**, and every
reference updated. The filename is now set once
(`annotation.trait_ontology_file` in `config/config.yaml`). Details and
the alternative fix (editing the Methods instead) are in
[`docs/ontology_note.md`](docs/ontology_note.md).

**3. "Without a release tied to the manuscript's counts and analyses…"**
This repository is intended to be released as a tagged version whose tag
matches the manuscript (e.g. `v1.0.0`, recorded in `CITATION.cff`). The
release should be archived on Zenodo to obtain a DOI. Steps are listed in
[`docs/release_checklist.md`](docs/release_checklist.md).

> **Security.** The literature-mining LLM step
> (`literature_mining/3.run_breeding_evaluation.py`) previously contained a
> **hard-coded API key** (and an internal endpoint), which was exposed
> while this repository was public. The credentials are now read from the
> environment (`BREEDING_API_KEY`, `BREEDING_API_URL`); **the old key must
> be revoked and rotated**. See [`SECURITY.md`](SECURITY.md).

---

## Data availability

Large inputs (raw reads, genome/CDS/protein FASTA, GFF3, indices and the
annotation databases) are **not** committed; see `docs/workflows.md` for
where each is expected and `docs/release_checklist.md` for the
Zenodo/accession plan.

## Versioning

Releases are tagged `vMAJOR.MINOR.PATCH`. The tag cited in the manuscript
is recorded in `CITATION.cff`. Please cite the archived release.

## License and citation

Released under the MIT License (see [`LICENSE`](LICENSE)). If you use
this code, please cite the manuscript; machine-readable metadata is in
[`CITATION.cff`](CITATION.cff).

## Contact

*&lt; corresponding author / maintainer &gt;* — *&lt; email &gt;*
