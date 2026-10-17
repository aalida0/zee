/*
 * Gate A1S: 2026 Misiak et al. Eq.(4) EXACT matching-scale LO probes.
 *
 * Build with the already-validated isolated A1M SuperIso v5
 * src/libsuperiso.a and its include.h. No vendor physics source change.
 *
 * Reference: arXiv:2608.29863, Eq.(4), mu0=160 GeV:
 *   B(Bbar->Xs gamma) * 1e4 = 3.54 - 8.51*dC7 - 2.16*dC8
 * where dC7,8 are LO BSM coefficients in the paper's Q7,Q8 basis;
 * quadratic terms are NEGLECTED. This C program prints matching
 * deltas only, NOT a branching ratio or flavour exclusion.
 */
#include "include.h"
#include <errno.h>
#include <math.h>
#include <complex.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int parse_pos(const char *raw, double *out)
{
    char *end=NULL;
    errno=0;
    *out=strtod(raw,&end);
    return !errno && end!=raw && !*end && isfinite(*out) && *out>0.;
}

int main(int argc,char **argv)
{
    struct parameters p;
    double mass,tanb,mu=160.0,mt;
    double complex sm0[11],sm1[11],sm2[11];
    double complex h0[11],h1[11],h2[11];
    double complex d7,d8;
    int i;
    if(argc!=3 || !parse_pos(argv[1],&mass)
       || !parse_pos(argv[2],&tanb)
       || mass<200. || tanb<.25 || tanb>100.) {
        fprintf(stderr,"A1S_INPUT_ERROR usage: a1s_probe massH_GeV tanbeta\n");
        return 2;
    }
    Init_param(&p);
    slha_adjust(&p);
    if(!isfinite(p.mass_W)||p.mass_W<=0. ||
       !isfinite(p.mtmt)||p.mtmt<=0. ||
       !isfinite(p.mass_b)||p.mass_b<=0.) {
        fprintf(stderr,"A1S_VENDOR_INPUTS_INVALID\n");return 3;
    }
    p.THDM_model=2;
    p.tan_beta=tanb;
    p.mass_H=mass;
    for(i=1;i<=3;i++) {
        p.lambda_u[i][i]=1./tanb;
        p.lambda_d[i][i]=-tanb;
        p.lambda_l[i][i]=-tanb;
    }
    mt=running_mass(p.mtmt,p.mtmt,mu,p.mass_top_pole,p.mass_b,&p);
    if(!isfinite(mt)||mt<100.||mt>250.) {
        fprintf(stderr,"A1S_RUNNING_TOP_INVALID\n");return 3;
    }
    p.SM=1;
    CW_calculator(2,sm0,sm1,sm2,mu,&p);
    p.SM=0;
    CW_calculator(2,h0,h1,h2,mu,&p);
    d7=h0[7]-sm0[7];
    d8=h0[8]-sm0[8];
    for(i=1;i<=10;i++) {
        if(!isfinite(creal(sm0[i]))||!isfinite(cimag(sm0[i]))||
           !isfinite(creal(h0[i]))||!isfinite(cimag(h0[i]))||
           fabs(cimag(sm0[i]))>1.e-10||
           fabs(cimag(h0[i]))>1.e-10) {
            fprintf(stderr,"A1S_UNEXPECTED_COMPLEX_LO_COEFFICIENT op=%d\n",i);
            return 3;
        }
    }
    printf("STATUS A1S_SOURCE_PINNED_LO_MATCHING_NO_BR_OR_EXCLUSION\n");
    printf("INPUT mH_GeV=%.17g tanbeta=%.17g mu0_GeV=%.17g "
           "running_mt_mu0_GeV=%.17g\n",mass,tanb,mu,mt);
    printf("DELTA_C7_LO=%.17g\n",creal(d7));
    printf("DELTA_C8_LO=%.17g\n",creal(d8));
    printf("NO_THEORY_LIKELIHOOD_VALIDATED true\n");
    return 0;
}
