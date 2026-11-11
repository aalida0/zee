#!/usr/bin/env python3
"""Make conservative paper-level visualizations from validated *actual* MG5 data.

Plot 1: 13 TeV source LO H2->H1Z->tbZ rates for 16 scalar witnesses,
        with 2026 published LO-NP one-sided B-screen marker.
Plot 2: 13/14 TeV *actual separately integrated* rates for only three scalars.
Figures have explicit benchmark-selection and missing-theory disclaimers;
neither shows detector-level sensitivity or model-wide allowed regions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def make_figures(source:Path,out:Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data=json.loads(source.read_text())
    rows=data["rows"]
    if len(rows)!=16 or data["n_actual_14TeV_scalar_production_rates"]!=3:
        raise ValueError("Insufficient source-validated old/existing collider inputs")
    if out.exists():raise FileExistsError("Do not overwrite existing paper plots")
    out.mkdir(parents=True)
    groups=[
        ("Misiak LO-NP one-sided screen (10/16)",[r for r in rows if r["B_one_sided_Gaussian_LO_NP_screen"]],"o"),
        ("Outside one-sided LO-NP screen (6/16)",[r for r in rows if not r["B_one_sided_Gaussian_LO_NP_screen"]],"x")
    ]
    fig,ax=plt.subplots(figsize=(9.5,6.2))
    for label,arr,marker in groups:
        ax.scatter([z["mH2_GeV"] for z in arr],
                   [z["sigma13_H2_H1Z_tb_product_range_fb"][0] for z in arr],
                   s=65,marker=marker,label=label)
    for ident in (15591,15673,11016,14074):
        z=next(x for x in rows if x["scalar_id"]==ident)
        ax.annotate(str(ident),(z["mH2_GeV"],z["sigma13_H2_H1Z_tb_product_range_fb"][0]),
                    textcoords="offset points",xytext=(5,5),fontsize=9)
    ax.set_yscale("log")
    ax.set_xlabel(r"$m_{H_2^\pm}$ [GeV]")
    ax.set_ylabel(r"$\sigma_{13}^{\rm LO}(pp\to tbH_2^\pm)\,\mathrm{BR}(H_2^\pm\to H_1^\pm Z)\,\mathrm{BR}(H_1^\pm\to tb)$ [fb]")
    ax.set_title("Zee Type-II-quark source spectra: conditional 13 TeV rates")
    ax.legend(loc="best")
    ax.grid(alpha=.3)
    fig.text(.1,.01,"16 preselected D10 tree-vacuum witnesses, not globally allowed. LO 5FS; no PDF/scale band, HiggsTools or full LFV.",fontsize=8)
    fig.tight_layout(rect=(0,.035,1,1))
    fig.savefig(out/"conditional_13TeV_rates_vs_mass.png",dpi=185)
    plt.close(fig)

    true14=[z for z in rows if z["sigma14_actual_LO_5FS_fb"] is not None]
    true14.sort(key=lambda r:r["scalar_id"])
    if [z["scalar_id"] for z in true14]!=[2264,15591,15673]:
        raise ValueError("Source actual 14 TeV MG5 point set changed")
    fig,ax=plt.subplots(figsize=(8.3,5.8))
    x=list(range(3));w=.34
    y13=[r["sigma13_H2_H1Z_tb_product_range_fb"][0] for r in true14]
    y14=[r["sigma14_H2_H1Z_tb_product_range_fb"][0] for r in true14]
    ax.bar([k-w/2 for k in x],y13,width=w,label="Actual MG5 13 TeV")
    ax.bar([k+w/2 for k in x],y14,width=w,label="Actual MG5 14 TeV")
    ax.set_xticks(x,[str(r["scalar_id"]) for r in true14])
    ax.set_xlabel("Scalar source ID (same scalar card and decay prescription)")
    ax.set_ylabel(r"LO $\sigma\times\mathrm{BR}(H_2\to H_1Z\to tbZ)$ [fb]")
    ax.set_title("Actual 13/14 TeV integrated Zee cascade rates (three spectra)")
    ax.legend()
    ax.grid(axis="y",alpha=.3)
    fig.text(.08,.01,"Pre-detector LO 5FS; numerical integration errors only; no 14 TeV interpolation, PDF/scale bands or experimental reach.",fontsize=8)
    fig.tight_layout(rect=(0,.035,1,1))
    fig.savefig(out/"actual_13_vs_14TeV_three_benchmarks.png",dpi=185)
    plt.close(fig)
    print("PAPER_FIGURES_PASS",len(rows),"13TEV",len(true14),"14TEV",flush=True)
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    make_figures(args.source,args.output_dir)


if __name__=="__main__":
    main()
