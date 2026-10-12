# Release checklist (tying the code to the manuscript)

Reviewer comment #3 asks for a release tied to the manuscript's counts
and analyses. Work through this list before submitting the revision.

- [x] **Literature-mining scripts** — the four scripts and `config/` are
      now in `literature_mining/` (normalised; `2.merge_pubmed.py`
      re-encoded GBK → UTF-8).
- [ ] **Revoke & rotate the previously hard-coded API key** — the old
      key was committed publicly; see `SECURITY.md`. Required before the
      release.
- [x] **Set the ontology filename** — the repository file was renamed to
      `StructuredTobaccoBreedingTraitOntology.json`, exactly as cited in
      the Methods (`docs/ontology_note.md`). Nothing left to edit unless
      you prefer to change the manuscript instead.
- [x] **Fill the version table** in `docs/workflows.md` — done, using the
      versions stated in the manuscript Methods (Manuscript-v7).
- [ ] **Reconcile the manuscript-vs-code discrepancies** listed at the
      end of `docs/workflows.md`:
      - [ ] gene-ID conversion: Methods say MCScanX + BLASTP, the code
            uses jcvi (LAST) + LAST fallback.
      - [ ] InterProScan version: Methods v5.77 vs notes 5.76-107.0.
      - [ ] QUAST `--large` / BUSCO lineage sets vs "default parameters".
      - [ ] name the sgRNA tool (GuideScan) and LAST in the Methods.
- [ ] **Add a `config.yaml` snapshot** used for the manuscript run
      (or record the parameters in the Methods).
- [ ] **Add a `CHANGELOG.md`** describing this release.
- [ ] **Tag the release**: `git tag -a v1.0.0 -m "manuscript release"` and
      `git push origin v1.0.0`.
- [ ] **Archive on Zenodo** to mint a DOI and add it to `CITATION.cff`.
- [ ] **Data availability statement**: list the accessions / repositories
      for raw reads, assemblies and annotation resources.
- [ ] **Update `CITATION.cff`**: authors, repository URL, DOI, version.
- [ ] **Cite the tag/DOI in the manuscript** (e.g. "code available at
      https://github.com/<user>/<repo>, tag v1.0.0, DOI 10.xxxx/xxxxx").

## Suggested Zenodo / data deposition

| Item | Where |
|---|---|
| Code | this GitHub repo (tagged) + Zenodo DOI |
| Raw RNA-seq reads | SRA/ENA (BioProject accession) |
| Genome / CDS / protein FASTA, GFF3 | Zenodo or a genome portal |
| Annotation databases (eggNOG, InterPro) | public releases; record versions |

Record every accession in the manuscript's Data Availability section and
in `docs/workflows.md`.
