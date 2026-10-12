# Gene-ID conversion (synteny + sequence alignment)

Because the manuscript compares gene sets annotated under different gene
naming schemes across several *Nicotiana* assemblies, a conversion table
is built for every assembly pair using two independent evidence sources:

1. **Synteny anchors** (jcvi/MCScan) — primary evidence.
2. **Sequence alignment** (LAST best hit) — fallback for genes not
   covered by an anchor.

## Files

| Script | Purpose | Output |
|---|---|---|
| `1.prepare_jcvi_inputs.sh` | GFF3 + CDS → `.bed` / `.cds` | `work/jcvi/<asm>.bed`, `.cds` |
| `2.run_jcvi_synteny.sh` | pairwise orthologs + anchor screening | `<a>.<b>.anchors[.simple]` |
| `3.run_last.sh` | LAST alignment → best hit per query | `<a>.<b>.last.filtered` |
| `4.convert_gene_ids.py` | build the conversion tables | `<a>.<b>.gene_conversion.tsv` |
| `5.plot_karyotype.sh` | synteny karyotype figure | `karyotype.pdf` |

## Conversion-table logic

For each ordered assembly pair `a → b`:
* every gene in `a` that has a synteny anchor in `b` is taken from
  `<a>.<b>.lifted.anchors` (columns: `query_gene, hit_gene, method, score,
  identity, aln_len`);
* remaining genes are filled from the best LAST hit
  (`identity × aln_len` as the ranking score);
* the result is written to `<a>.<b>.gene_conversion.tsv`.

## Running

```bash
bash 1.prepare_jcvi_inputs.sh
bash 2.run_jcvi_synteny.sh
bash 3.run_last.sh
python 4.convert_gene_ids.py --list name --workdir work/jcvi
bash 5.plot_karyotype.sh
```

## Notes

* `name` is a one-column file listing assembly names; jcvi and LAST are
  run for **all ordered pairs** (n × m).
* `3.run_last.sh` uses nucleotide CDS by default (`SEQTYPE=dna`); set
  `SEQTYPE=protein` for a more sensitive protein-level alignment. Hits
  can be filtered with `MIN_IDENTITY` / `MIN_ALN_LEN`, and only the
  highest bit-score hit per query is retained.

> ⚠️ **Manuscript wording differs.** The revised Methods describe this
> step as "MCScanX collinearity analysis … verified by BLASTP similarity
> searches", but the pipeline that was actually run (see
> `../docs/methods_notes_original.txt`) is `jcvi.compara.catalog` — which
> uses **LAST** internally for the pairwise homology search — followed by
> `jcvi.compara.synteny screen` and a LAST-based fallback in
> `4.convert_gene_ids.py`. Please make the Methods and the code agree:
> either describe the jcvi/LAST pipeline that was run, or add an MCScanX
> step and state which one produced the released tables.
