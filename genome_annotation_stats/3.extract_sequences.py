#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 3.extract_sequences.py  —  Extract genomic sequences for a gene set
# ---------------------------------------------------------------------
# Given a GFF3 and the matching genome FASTA, extract the genomic
# (gDNA) sequence spanning a list of genes of interest.
#
# Inputs (edit the CONFIG block)
#   <assembly>.gff3        gene models
#   <assembly>.genome.fa   genome sequence
#   GENES                  list of gene IDs to extract
#
# Output
#   printed FASTA records (redirect to a file as needed)
#
# Usage
#   python 3.extract_sequences.py > cd_region.fasta
# =====================================================================
import pandas as pd
from pyfaidx import Fasta

# ----------------------------- CONFIG --------------------------------
GFF_FILE = "Nicotiana_tabacum-HD.gff3"
GENOME_FILE = "Nicotiana_tabacum-HD.genome.fa"
GENES = ["Ntab0107370", "Ntab0107380", "Ntab0107390",
         "Ntab0107400", "Ntab0107410"]
# ---------------------------------------------------------------------

GenomeFast = Fasta(GENOME_FILE)

GffTable = pd.DataFrame(pd.read_csv(GFF_FILE, sep="\t", header=None))
GffTable = GffTable[GffTable[2] == "gene"]
GffTable[8] = [x.split(";")[0].replace("ID=", "") for x in list(GffTable[8])]

Info = GffTable[GffTable[8].isin(GENES)]

Sequence = ""
for index, row in Info.iterrows():
    Chr, Start, End, Gene = row[0], int(row[3]), int(row[4]), row[8]
    Sequence += ">{}\n{}\n".format(Gene + "_gDNA", GenomeFast[Chr][Start:End])

print(GffTable.head())
print(Info)
print(Sequence)
