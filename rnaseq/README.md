# RNA-seq quantification workflow

Reads are quality-trimmed with **fastp**, aligned with **STAR** against
each reference genome, summarised per gene with **featureCounts**, and
finally converted to clean counts / FPKM / TPM matrices, together with
sample-level QC figures (PCA, correlation heatmap).

```
raw fastq.gz
   │  0.run_fastp.sh
   ▼
clean fastq.gz
   │  1.run_star.sh
   ▼
Aligned.sortedByCoord.out.bam  +  Log.final.out  +  gene_counts.txt
   │  run_pipeline.sh  (steps 3-7)
   ▼
gene_counts.clean.txt · gene_fpkm.txt · gene_tpm.txt · RNAseq_QC.csv
QC_PCA_logCPM.png · QC_Correlation_Clustermap_logCPM.png
```

## Files

| Script | Purpose |
|---|---|
| `0.run_fastp.sh` | Adapter/quality trimming (fastp) + MultiQC |
| `1.run_star.sh` | STAR alignment (shared-memory genome loading) |
| `2.run_featurecounts.sh` | Gene-level counting (featureCounts) |
| `3.parse_star_log.py` | STAR `Log.final.out` → `STAR_mapping_summary.csv` |
| `4.format_featurecounts_summary.py` | featureCounts summary → `gene_counts_for_db.csv` |
| `5.merge_summary.py` | Merge counts + mapping + labels → `RNAseq_QC.csv` |
| `6.gene_counts_qc.py` | Filtering, PCA, correlation heatmap |
| `7.count_tpm_fpkm.py` | Clean counts, FPKM, TPM |
| `run_pipeline.sh` | Runs steps 3–7 in the featureCounts output folder |

## Inputs needed

* Paired-end `*_1.fastq.gz` / `*_2.fastq.gz` raw reads.
* A one-column `name` file listing sample IDs.
* A two-column `rename` file mapping each sample ID to a readable label
  of the form `Tissue#Species` (e.g. `Leaf#Ntab_K326`), used by
  `5.merge_summary.py`, `6.gene_counts_qc.py` and `7.count_tpm_fpkm.py`.
* Pre-built STAR indices and the matching transcript-level GTF files
  (the index → GTF mapping is set in `2.run_featurecounts.sh`).

See `../config/config.example.yaml` for the parameter defaults and the
`../config/samples.example.tsv` sample-sheet template.

## Running

```bash
# heavy steps (once per reference index)
bash 0.run_fastp.sh
bash 1.run_star.sh          # INDICES="NtSR1Index149 NtZY300Index149"
bash 2.run_featurecounts.sh

# downstream steps from inside the featureCounts output directory
cd work/<index>
cp /path/to/rename .
bash /path/to/rnaseq/run_pipeline.sh
```

## Notes

* `3.parse_star_log.py` and `6/7` are run **per reference assembly**
  (one STAR index / one featureCounts run at a time).
* The `rename` file is the single source of sample labels; keep it with
  the manuscript's supplementary sample table so the mapping is traceable.
