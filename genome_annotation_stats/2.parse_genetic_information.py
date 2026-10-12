#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 2.parse_genetic_information.py  —  Per-gene structural / sequence stats
# ---------------------------------------------------------------------
# For a given assembly, combine GFF3 gene coordinates with CDS and
# protein properties into one per-gene table:
#   Chr, Start, End, Strand, gene length, CDS length, protein length,
#   isoelectric point, molecular weight, instability index, aromaticity,
#   GRAVY and molar extinction coefficient.
#
# Inputs (edit the paths in the CONFIG block below)
#   <assembly>.gff3     gene models
#   <assembly>.cds      coding sequences (FASTA)
#   <assembly>.pep      protein sequences (FASTA)
#   gene_list           optional list of gene IDs to report
#
# Output
#   result.xls          tab-separated per-gene statistics table
#
# Usage
#   python 2.parse_genetic_information.py
# =====================================================================
import pandas as pd
from pyfaidx import Fasta
from pathlib import Path
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import gff3_parser

# ----------------------------- CONFIG --------------------------------
gff_file = "Nicotiana_tabacum-K326.gff3"
cds_file = "Nicotiana_tabacum-K326.cds"
pep_file = "Nicotiana_tabacum-K326.pep"
gene_list = "gene_list"
# ---------------------------------------------------------------------

# 1. Parse the GFF3 (cached to <gff>.xls on first run)
gff_file_parser = gff_file + ".xls"
if not Path(gff_file_parser).exists():
    full_data = gff3_parser.parse_gff3(gff_file, verbose=True,
                                        parse_attributes=True)
    full_data["Lenght"] = list(map(
        lambda x, y: int(y) - int(x) + 1, full_data["Start"], full_data["End"]
    ))
    full_data.to_csv(gff_file_parser, sep="\t")

# 2. Parse the CDS and protein FASTA files
cds = Fasta(cds_file)
pep = Fasta(pep_file)
cds_parser = cds_file + ".xls"
pep_parser = pep_file + ".xls"

if not Path(cds_parser).exists():
    with open(cds_parser, "w") as f:
        for i in cds.keys():
            print("{}\t{}".format(i, len(cds[i])), file=f)

if not Path(pep_parser).exists():
    with open(pep_parser, "w") as f:
        for i in pep.keys():
            seq = str(pep[i])
            if seq.endswith("*"):
                seq = seq[:-1]
            print("{}\t{}\t{}".format(i, len(seq), seq), file=f)


def PepAnalysis(seq):
    """Return the six protein physicochemical properties as a TSV row."""
    x = ProteinAnalysis(seq)
    return ("{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}\t{}\t{}".format(
        x.isoelectric_point(),
        x.molecular_weight() / 1000,
        x.instability_index(),
        x.aromaticity(),
        x.gravy(),
        x.molar_extinction_coefficient(),
    ))


# 3. Assemble the statistics table
gene_list_df = pd.DataFrame(pd.read_csv(gene_list, sep="\t", header=None))
gene_list_df["ID"] = list(map(lambda x: x.replace("TU", "model"),
                              gene_list_df[0]))
gff_file_parser_df = pd.DataFrame(pd.read_csv(gff_file_parser, sep="\t",
                                              index_col=0))
cds_parser_df = pd.DataFrame(pd.read_csv(cds_parser, sep="\t"))
cds_parser_df.columns = ["ID", "cds length"]
pep_parser_df = pd.DataFrame(pd.read_csv(pep_parser, sep="\t"))
pep_parser_df.columns = ["ID", "pep length", "pep seq"]

gene_list_df = pd.merge(gene_list_df, gff_file_parser_df, how="left",
                        on=["ID"])
gene_list_df = pd.merge(gene_list_df, cds_parser_df, how="left", on=["ID"])
gene_list_df = pd.merge(gene_list_df, pep_parser_df, how="left", on=["ID"])

gene_list_df["pI"] = list(map(lambda x: PepAnalysis(x).split("\t")[0],
                              gene_list_df["pep seq"]))
gene_list_df["MW(kDa)"] = list(map(lambda x: PepAnalysis(x).split("\t")[1],
                                   gene_list_df["pep seq"]))
gene_list_df["instability_index"] = list(map(
    lambda x: PepAnalysis(x).split("\t")[2], gene_list_df["pep seq"]))
gene_list_df["aromaticity"] = list(map(
    lambda x: PepAnalysis(x).split("\t")[3], gene_list_df["pep seq"]))
gene_list_df["gravy"] = list(map(lambda x: PepAnalysis(x).split("\t")[4],
                                 gene_list_df["pep seq"]))
gene_list_df["molar_extinction_coefficient"] = list(map(
    lambda x: PepAnalysis(x).split("\t")[5], gene_list_df["pep seq"]))

columns1 = ["ID", "Seqid", "Start", "End", "Strand", "Lenght",
            "cds length", "pep length", "pI", "MW(kDa)",
            "instability_index", "aromaticity", "gravy",
            "molar_extinction_coefficient"]
columns2 = ["Gene ID", "Chr", "Start", "End", "Strand", "Lenght",
            "CDS Length", "Protein Length", "Isoelectric Point", "MW(kDa)",
            "Instability Index", "Aromaticity", "GRAVY",
            "Molar Extinction Coefficient"]
gene_list_df = gene_list_df[columns1]
gene_list_df.columns = columns2
gene_list_df.to_csv("result.xls", sep="\t", index=False)

print("OK: wrote result.xls")
