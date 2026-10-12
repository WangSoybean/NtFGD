#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 1.get_pubmed.py  —  Harvest literature records from PubMed
# ---------------------------------------------------------------------
# Queries the NCBI E-utilities API with a fixed plant gene-function
# search string and downloads the matching records (PMID, DOI, title,
# abstract, publication date, journal) one year at a time.
#
# Years with < 9000 hits are fetched in one request; years with more are
# split into two half-year requests to stay within the E-utilities
# record limit.
#
# Output
#   plant_gene_function_<year>.tsv          (or _H1 / _H2 for big years)
#
# Usage
#   pip install requests lxml tqdm pandas
#   python 1.get_pubmed.py
#
# To change the covered period, edit the `range(...)` in the year loop
# at the bottom of this file.
# =====================================================================
import requests
from lxml import etree
from tqdm import tqdm
from io import BytesIO
import time
import os
import pandas as pd

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

BASE_QUERY = '''(
  "Plants"[MeSH Terms]
  OR plant*[Title/Abstract]
  OR Arabidopsis
  OR rice
  OR maize
  OR tobacco
  OR wheat
  OR barley
)
AND
(
  gene[Title/Abstract]
  OR genetic[Title/Abstract]
  OR transgenic[Title/Abstract]
)
AND
(
  mutant*[Title/Abstract]
  OR knockout[Title/Abstract]
  OR knock-out[Title/Abstract]
  OR CRISPR[Title/Abstract]
  OR Cas9[Title/Abstract]
  OR RNAi[Title/Abstract]
  OR "RNA interference"[Title/Abstract]
  OR overexpression[Title/Abstract]
  OR function*[Title/Abstract]
  OR phenotype*[Title/Abstract]
  OR role[Title/Abstract]
)
'''

session = requests.Session()


# =========================
# Fetch a single period
# =========================
def fetch_by_period(query, label, outfile):
    print(f"  > Processing {label}")
    r = session.get(
        BASE + "esearch.fcgi",
        params={
            "db": "pubmed",
            "term": query,
            "retmax": 10000
        },
        timeout=300
    )
    root = etree.fromstring(r.content)
    pmids = [x.text for x in root.findall(".//Id")]
    print(f"    Found {len(pmids)} papers")
    if not pmids:
        return
    records = []
    for i in tqdm(range(0, len(pmids), 200), desc=label):
        ids = ",".join(pmids[i:i + 200])
        r = session.get(
            BASE + "efetch.fcgi",
            params={
                "db": "pubmed",
                "id": ids,
                "retmode": "xml"
            },
            timeout=60
        )
        if not r.content.strip():
            print("    WARNING: empty response, skipping batch")
            continue
        for _, art in etree.iterparse(BytesIO(r.content), tag="PubmedArticle"):
            # PMID
            pmid = art.findtext(".//PMID") or ""
            # DOI
            doi = ""
            for aid in art.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text or ""
                    break
            # ---------- Title (itertext, avoids truncation) ----------
            title_node = art.find(".//ArticleTitle")
            title = "".join(title_node.itertext()).strip() if title_node is not None else ""
            # ---------- Abstract (itertext, avoids truncation) ----------
            abstract_parts = []
            for abs_node in art.findall(".//AbstractText"):
                text = "".join(abs_node.itertext()).strip()
                if text:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts)
            # ---------- PubDate ----------
            pub_date = ""
            # 1. ArticleDate (highest priority)
            date_node = art.find(".//ArticleDate")
            if date_node is not None:
                y = date_node.findtext("Year")
                m = date_node.findtext("Month", "01")
                d = date_node.findtext("Day", "01")
                if y:
                    pub_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
            # 2. Journal PubDate
            if not pub_date:
                y = art.findtext(".//JournalIssue/PubDate/Year")
                m = art.findtext(".//JournalIssue/PubDate/Month")
                if y:
                    if m and m.isdigit():
                        pub_date = f"{y}-{m.zfill(2)}-01"
                    elif m:
                        month_map = {
                            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
                        }
                        pub_date = f"{y}-{month_map.get(m[:3], '01')}-01"
                    else:
                        pub_date = f"{y}-01-01"
            # 3. MedlineDate (fallback)
            if not pub_date:
                medline = art.findtext(".//JournalIssue/PubDate/MedlineDate")
                if medline:
                    year = "".join(c for c in medline if c.isdigit())[:4]
                    if year:
                        pub_date = f"{year}-01-01"
            # Journal
            journal = art.findtext(".//Journal/Title") or ""
            records.append({
                "PMID": pmid,
                "DOI": doi,
                "Title": title,
                "Abstract": abstract,
                "PubDate": pub_date,
                "Journal": journal
            })
            art.clear()
        time.sleep(0.34)
    # ---------- Write TSV ----------
    df = pd.DataFrame(records)
    df.to_csv(outfile, sep="\t", index=False)
    print(f"    Saved {len(df)} records to {outfile}")


# =========================
# Year loop
# =========================
for year in range(2025, 2026):
    print(f"\n> Year {year}")
    year_query = f"{BASE_QUERY} AND {year}[PDAT]"
    r = session.get(
        BASE + "esearch.fcgi",
        params={
            "db": "pubmed",
            "term": year_query,
            "retmax": 0
        },
        timeout=30
    )
    root = etree.fromstring(r.content)
    count = int(root.findtext("Count"))
    print(f"  Total papers: {count}")
    if count < 9000:
        out = f"plant_gene_function_{year}.tsv"
        fetch_by_period(year_query, str(year), out)
    else:
        q1 = f'{BASE_QUERY} AND ("{year}/01/01"[PDAT] : "{year}/06/30"[PDAT])'
        q2 = f'{BASE_QUERY} AND ("{year}/07/01"[PDAT] : "{year}/12/31"[PDAT])'
        fetch_by_period(q1, f"{year}_H1", f"plant_gene_function_{year}_H1.tsv")
        fetch_by_period(q2, f"{year}_H2", f"plant_gene_function_{year}_H2.tsv")
