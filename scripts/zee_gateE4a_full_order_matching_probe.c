/*
 * Gate E4A large integrated matched-Wilson interface.
 *
 * Source pinned to the same A1M isolated SuperIso v5 matching library
 * as E1/E2/E3. This is a THREE-QCD-ORDER COEFFICIENT SOURCE PROBE,
 * not a 2026 inclusive BR prediction or a calibrated 95% CL likelihood.
 *
 * At COMMON mu0=160 GeV, for each of 8 operators and each order
 * 0,1,2, emit the SM, separate Type-II H1/H2 NP shifts, their
 * coherent two-state Zee Wilson vector and exact weights.  Do not
 * combine individual Higgs branching ratios.
 *
 * A1Q independently audited NNLO dipole/four-quark conventions;
 * original-author and 2026 low-scale observable matching cannot be
 * established by compiling this source alone. Report the raw arrays
 * as vendor CW_calculator entries without renaming them physical Ceff.
 */
#include "include.h"
#include <errno.h>
#include <math.h>
#include <complex.h>
#include <stdio.h>
#include <stdlib.h>
#define N 11
struct coefficients {
    double complex c0[N],c1[N],c2[N];
};
static int finite_pos(const char *a,double *v)
{
    char *e=NULL;
    errno=0;
    *v=strtod(a,&e);
    return (errno==0 && e!=a && !*e && isfinite(*v) && *v>0.);
}
static int finite_angle(const char *a,double *v)
{
    char *e=NULL;
    errno=0;
    *v=strtod(a,&e);
    return (errno==0 && e!=a && !*e && isfinite(*v) &&
            *v>=0. && *v<=1.5707963267948967);
}
static int wc(const struct parameters *reference, double mass,
              double mu, int sm, struct coefficients *out)
{
    struct parameters p=*reference;
    p.mass_H=mass;
    p.SM=sm;
    p.THDM_model=2;
    CW_calculator(2,out->c0,out->c1,out->c2,mu,&p);
    for(int order=0;order<3;order++) {
        const double complex *arr=(order==0?out->c0:
                                   order==1?out->c1:out->c2);
        for(int k=1;k<=8;k++) {
            if(!isfinite(creal(arr[k])) || !isfinite(cimag(arr[k])) ||
               fabs(cimag(arr[k]))>1.e-10) {
                fprintf(stderr,"E4A_NONFINITE_MATCHING order=%d k=%d\n",order,k);
                return 0;
            }
        }
    }
    return 1;
}
int main(int argc,char **argv)
{
    struct parameters p;
    struct coefficients sm,h1,h2;
    double mass1,mass2,tanb,gamma;
    double mu=160.0;
    if(argc!=5 || !finite_pos(argv[1],&mass1) ||
       !finite_pos(argv[2],&mass2) ||
       !finite_pos(argv[3],&tanb) ||
       !finite_angle(argv[4],&gamma) ||
       mass1<200. || mass2<200. || mass1>10000. ||
       mass2>10000. || tanb<.25 || tanb>100.) {
        fprintf(stderr,"E4A_USAGE mass1 mass2 tanbeta gamma\n");
        return 2;
    }
    Init_param(&p);
    slha_adjust(&p);
    if(!isfinite(p.mass_W) || !isfinite(p.mtmt) ||
       p.mass_W<=0. || p.mtmt<=0.) {
        fprintf(stderr,"E4A_INVALID_STANDARD_MODEL_INPUT\n");
        return 3;
    }
    p.THDM_model=2;
    p.tan_beta=tanb;
    for(int i=1;i<=3;i++) {
        p.lambda_u[i][i]=1./tanb;
        p.lambda_d[i][i]=-tanb;
        p.lambda_l[i][i]=-tanb;
    }
    const double x=cos(gamma)*cos(gamma);
    const double y=sin(gamma)*sin(gamma);
    if(fabs(x+y-1.)>1.e-12) return 3;
    if(!wc(&p,mass1,mu,1,&sm) ||
       !wc(&p,mass1,mu,0,&h1) ||
       !wc(&p,mass2,mu,0,&h2))return 3;
    printf("STATUS E4A_FULL_ORDER_MATCHING_NOT_2026_BR_OR_EXCLUSION\n");
    printf("INPUT mH1=%.17g mH2=%.17g tanbeta=%.17g gamma=%.17g "
           "mu0=%.17g w1=%.17g w2=%.17g\n",
           mass1,mass2,tanb,gamma,mu,x,y);
    for(int order=0;order<3;order++) {
        const double complex *a=(order==0?sm.c0:order==1?sm.c1:sm.c2);
        const double complex *p1=(order==0?h1.c0:order==1?h1.c1:h1.c2);
        const double complex *p2=(order==0?h2.c0:order==1?h2.c1:h2.c2);
        for(int k=1;k<=8;k++){
            const double smv=creal(a[k]);
            const double d1=creal(p1[k]-a[k]);
            const double d2=creal(p2[k]-a[k]);
            const double mixture=smv+x*d1+y*d2;
            if(!isfinite(mixture))return 3;
            printf("MATCH order=%d op=%d sm=%.17g delta_light=%.17g "
                   "delta_heavy=%.17g zee=%.17g\n",
                   order,k,smv,d1,d2,mixture);
        }
    }
    puts("PHYSICAL_BR_2026_NOT_IMPLEMENTED true");
    puts("NNLO_MATRIX_ELEMENTS_AND_THEORY_COVARIANCE_MISSING true");
    return 0;
}
