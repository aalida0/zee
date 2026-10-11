/* Gate A1L: external SuperIso v5 Zee Type-II charged-Higgs Wilson matching PILOT.
 *
 * NOT a physical BR(B->Xs gamma) or publication-ready matching. The native
 * vendor CW_calculator has an NLO C7/C8 charged-Higgs zeroing issue (see
 * gateA1l_superiso_nlo_audit.py); this diagnostic deliberately reproduces
 * existing vendor behavior and NEVER repairs or edits the vendor library.
 *
 * Construct three matching vectors at identical input and muW:
 *  SM, SM+single charged H1 and SM+single charged H2.
 * Superpose w1*(H1-SM)+w2*(H2-SM) at LO, NLO and NNLO.
 * QCD RG and inclusive BR are intentionally NOT run at this gate.
 *
 * Florentino arXiv:2106.08332: quark doublet projection
 * w1=cos(gamma)^2, w2=sin(gamma)^2;
 * type-II Yukawa: lambda_u=cot(beta), lambda_d=-tan(beta).
 *
 * Compile via gateA1l_superiso_matching_pilot.sh, using original
 * SuperIso_v5.0/src/libsuperiso.a. Source is not modified.
 */
#include "include.h"
#include <math.h>
#include <complex.h>
#include <stdio.h>
#include <stdlib.h>

#define NCOEFF 11

struct coefficient_vector {
  double complex C0[NCOEFF];
  double complex C1[NCOEFF];
  double complex C2[NCOEFF];
};

static int compute(struct coefficient_vector *out,
                   const struct parameters *base,
                   double mass_hplus, int is_sm, double muW)
{
  struct parameters p = *base;
  p.mass_H = mass_hplus;
  p.SM = is_sm;
  p.THDM_model = 2;  /* Native THDM_model nonzero; Type-II lambdas explicitly set */
  CW_calculator(2, out->C0, out->C1, out->C2, muW, &p);
  for (int i=1;i<=10;i++) {
    if (!isfinite(creal(out->C0[i])) || !isfinite(cimag(out->C0[i])) ||
        !isfinite(creal(out->C1[i])) || !isfinite(cimag(out->C1[i])) ||
        !isfinite(creal(out->C2[i])) || !isfinite(cimag(out->C2[i]))) {
      fprintf(stderr, "Non-finite coefficient order/index for mass=%g i=%d\n",
              mass_hplus, i);
      return 0;
    }
  }
  return 1;
}

int main(int argc, char **argv)
{
  if (argc != 5) {
    fprintf(stderr, "Usage: %s mH1_GeV mH2_GeV gamma_rad beta_rad\n",argv[0]);
    return 2;
  }
  char *end;
  double inputs[4];
  for (int i=0;i<4;i++) {
    end=NULL;
    inputs[i]=strtod(argv[i+1], &end);
    if (end==argv[i+1] || *end!='\0' || !isfinite(inputs[i])) {
      fprintf(stderr, "Invalid numeric argument %s\n",argv[i+1]);
      return 2;
    }
  }
  double m1=inputs[0], m2=inputs[1], gamma=inputs[2], beta=inputs[3];
  if (!(m1>0. && m2>m1 && gamma>=0. && gamma<=1.570796326794897 &&
        beta>0. && beta<1.570796326794897)) {
    fputs("Require mH2>mH1>0, 0<=gamma<=pi/2, 0<beta<pi/2\n",stderr);
    return 2;
  }
  struct parameters p;
  Init_param(&p);
  slha_adjust(&p);
  const double tanbeta = tan(beta);
  p.tan_beta=tanbeta;
  p.THDM_model=2;
  for (int i=1;i<=3;i++) {
    p.lambda_u[i][i]=1./tanbeta;
    p.lambda_d[i][i]=-tanbeta;
    p.lambda_l[i][i]=-tanbeta;
  }
  if (!(isfinite(p.mass_W) && p.mass_W>0 &&
        isfinite(p.mass_top_pole) && p.mass_top_pole>0)) {
    fputs("SM base parameters missing; cannot call CW_calculator\n", stderr);
    return 1;
  }
  double muW=2.*p.mass_W;
  double cg=cos(gamma), sg=sin(gamma);
  double w1=cg*cg, w2=sg*sg;
  struct coefficient_vector sm, h1, h2;
  if(!compute(&sm, &p, m1, 1, muW) ||
     !compute(&h1, &p, m1, 0, muW) ||
     !compute(&h2, &p, m2, 0, muW)) {
    return 1;
  }
  if(fabs(w1+w2-1.)>1e-13) {
    fputs("Mixing unitarity failed\n",stderr);
    return 1;
  }

  printf("STATUS MATCHING_WILSON_PILOT_NO_PHYSICAL_BR_VENDOR_NLO_C7_C8_AUDIT_REQUIRED\n");
  printf("INPUT mH1=%.17g mH2=%.17g beta=%.17g gamma=%.17g "
         "tanbeta=%.17g muW=%.17g w1=%.17g w2=%.17g\n",
         m1,m2,beta,gamma,tanbeta,muW,w1,w2);
  for (int order=0;order<=2;order++) {
    const double complex *S = order==0 ? sm.C0 : order==1 ? sm.C1 : sm.C2;
    const double complex *L = order==0 ? h1.C0 : order==1 ? h1.C1 : h1.C2;
    const double complex *H = order==0 ? h2.C0 : order==1 ? h2.C1 : h2.C2;
    for (int i=1;i<=10;i++) {
      double complex dL=L[i]-S[i],dH=H[i]-S[i];
      double complex zee=S[i]+w1*dL+w2*dH;
      if (fabs(cimag(S[i]))>1e-10 || fabs(cimag(dL))>1e-10 ||
          fabs(cimag(dH))>1e-10 || fabs(cimag(zee))>1e-10) {
        fprintf(stderr,"Unexpected imaginary matching coefficient %d/%d\n",order,i);
        return 1;
      }
      printf("COEFF order=%d i=%d sm=%.17g delta1=%.17g "
             "delta2=%.17g zee=%.17g\n",
             order,i,creal(S[i]),creal(dL),creal(dH),creal(zee));
    }
  }
  puts("WARNING Native SuperIso 5.0 NLO charged-Higgs C7/C8 clipping "
       "is under independent audit; DO NOT interpret as BR or exclusion");
  return 0;
}
