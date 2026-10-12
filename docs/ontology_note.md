# Ontology filename — reviewer comment #2 (resolved)

## The reviewer's point

> "The ontology filename in the Methods also differs from the file in the
> repository."

## What the two names were

| Source | Filename |
|---|---|
| Manuscript Methods (Manuscript-v7) | `StructuredTobaccoBreedingTraitOntology.json` |
| Repository (before this fix) | `config/StructuredTobaccoBreedingTargetSystem.json` |

The manuscript sentence reads:

> "The complete ontology structure is provided in the file
> **StructuredTobaccoBreedingTraitOntology.json**, available in the
> project repository."

So the manuscript and the repository used two different names for the
same file — exactly the mismatch the reviewer flagged.

## The fix applied

The repository file has been **renamed to match the manuscript**, so no
change to the manuscript text is required:

```
literature_mining/config/StructuredTobaccoBreedingTargetSystem.json
        ↓  renamed
literature_mining/config/StructuredTobaccoBreedingTraitOntology.json
```

All references were updated at the same time:

* `config/config.example.yaml` → `annotation.trait_ontology_file`
* `literature_mining/3.run_breeding_evaluation.py` (default path)
* `literature_mining/README.md`
* `README.md`, `docs/workflows.md`

The trait ontology is therefore referenced from exactly one place, and
grepping the repository for the filename returns only the ontology file
itself plus the paths that point at it.

> **If you would rather keep the repository name**, do the reverse
> instead: revert the rename and change the Methods sentence to
> `StructuredTobaccoBreedingTargetSystem.json`. Either way, the two must
> match character-for-character, including the `.json` extension.

## Two different ontologies are involved — do not confuse them

| File | What it is | Where it appears |
|---|---|---|
| `StructuredTobaccoBreedingTraitOntology.json` | The three-tier tobacco breeding **trait** ontology (6 primary categories → secondary dimensions → tertiary traits) | Methods, "Tobacco breeding trait ontology" |
| `go-basic.obo` (`https://geneontology.org/docs/download-ontology/`) | The Gene Ontology release used for GO enrichment | Methods, "Differential gene expression analysis" |

Only the first one was mismatched. If you edit one filename in the
Methods, double-check the other still matches the file you actually used.
For `go-basic.obo`, also state the release date (e.g.
`go-basic.obo, release 2024-01-01`) so reviewers can fetch the same
release.
