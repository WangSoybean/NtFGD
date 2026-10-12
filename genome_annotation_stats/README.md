# Genome annotation statistics & sequence utilities

Helpers that summarise gene models and extract sequences / coordinates
for downstream analyses and the web database.

| Script | Purpose | Output |
|---|---|---|
| `1.extract_gene_locations.sh` | gene coordinates from GFF3 (normalised chromosome names) | `results/gene_location/<asm>.genelocation` |
| `2.parse_genetic_information.py` | per-gene structural + protein physicochemical stats | `result.xls` |
| `3.extract_sequences.py` | genomic sequence for a chosen gene set | printed FASTA |

## `2.parse_genetic_information.py`

Combines GFF3 coordinates with CDS and protein FASTA to produce a table
with, per gene: chromosome, start/end, strand, gene length, CDS length,
protein length, isoelectric point, molecular weight, instability index,
aromaticity, GRAVY and molar extinction coefficient. Edit the `CONFIG`
block (top of the file) to point at your assembly and gene list.

## `3.extract_sequences.py`

Extracts the genomic (`gDNA`) region spanning a list of gene IDs. Set
`GFF_FILE`, `GENOME_FILE` and `GENES` in the `CONFIG` block.

## Dependencies

`gff3-parser`, `pyfaidx`, `biopython` (see `../requirements.txt`).
