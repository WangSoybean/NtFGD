# Ontology filename — reviewer comment #2

## The issue

> "The ontology filename in the Methods also differs from the file in the
> repository."

The manuscript's Methods cite an ontology file under one name, while the
repository shipped a file under a different name. Because the ontology
defines the term set used for annotation/enrichment, a mismatch makes the
reported results hard to trace.

## The fix applied here

The ontology file is now referenced from **exactly one place**:

```yaml
# config/config.yaml
annotation:
  ontology_file: "<the exact filename used in the manuscript>"
```

The template value in `config/config.example.yaml` is deliberately a
placeholder (`TODO_replace_with_manuscript_ontology_filename.obo`).

## What you still need to do

1. Decide the single canonical filename (the one that will appear in the
   revised Methods).
2. Put the ontology file in the repository (small `.obo`/`.tab` files can
   be committed directly; large ones should go to the archived release /
   Zenodo) and set `annotation.ontology_file` to that name.
3. Update the Methods text so the filename matches this value **exactly**
   (including extension and any version suffix).
4. If the file has a version, state it explicitly (e.g.
   `go-basic.obo` release `2024-01-01`) so reviewers can fetch the same
   release.

> The exact name cannot be inferred from the code alone; please fill it in
> before the release. Once set, grepping the repository for the filename
> should return only the config entry and the Methods text.
