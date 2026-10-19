/*
 * Gate F3 source-locked Wilson RGE probe, NOT an NNLO branching ratio.
 * Uses isolated A1M SuperIso v5 CW_calculator + C_calculator_base1.
 * Compiles ONLY against the SHA-checked isolated libsuperiso.a.
 *
 * For each physical charged Higgs pair, match at common muW=160GeV:
 * C^Zee=CSM+cos²gamma*(CH1-CSM)+sin²gamma*(CH2-CSM).
 * Compare three high-scale choices: 0=LO NP only, 1=LO+NLO dipoles
 * only, 2=LO+FULL source NLO C1..C8. In ALL cases keep NNLO BSM zero
 * and retain SM C2 order2. Evolve all through the same original
 * SuperIso NLO RGE and print raw low-coefficient NP shifts.
 *
 * This does not change the vendor code or provide a WCxf mapping.
 * No bsgamma() observable is called (avoids its hidden CW reload).
 */
#include "include.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <complex.h>
#include <errno.h>

#define NC 11
struct trip {double complex a[NC],b[NC],c[NC];};
static int readnum(const char *s,double *v) {
    char *end=NULL; errno=0;*v=strtod(s,&end);
    return errno==0 && end!=s && *end==0 && isfinite(*v);
}
static int good(struct trip *x) {
    for(int j=1;j<=8;j++)
        if(!isfinite(creal(x->a[j]))||!isfinite(creal(x->b[j]))||
           !isfinite(creal(x->c[j]))||
           fabs(cimag(x->a[j]))>1e-10||
           fabs(cimag(x->b[j]))>1e-10||
           fabs(cimag(x->c[j]))>1e-10) return 0;
    return 1;
}
static int match(const struct parameters *base, double mass,
                 int sm,double muW,struct trip *out) {
    struct parameters p=*base;
    p.mass_H=mass;p.SM=sm;p.THDM_model=2;
    CW_calculator(2,out->a,out->b,out->c,muW,&p);
    return good(out);
}
static int evolve(const struct parameters *base,const struct trip *high,
                  double mass,double muW,double mub,struct trip *low) {
    struct parameters p=*base;
    double complex a[NC],b[NC],c[NC];
    p.mass_H=mass;p.SM=1;p.THDM_model=2;
    for(int j=0;j<NC;j++){a[j]=high->a[j];b[j]=high->b[j];c[j]=high->c[j];}
    C_calculator_base1(a,b,c,muW,low->a,low->b,low->c,mub,&p);
    return good(low);
}
int main(int argc,char **argv) {
    double mass1,mass2,tanb,gamma,muW,mub;
    struct parameters p;
    struct trip sm={0},l={0},h={0},z={0},lowSM={0},lowZ={0};
    if(argc!=7||!readnum(argv[1],&mass1)||!readnum(argv[2],&mass2)||
       !readnum(argv[3],&tanb)||!readnum(argv[4],&gamma)||
       !readnum(argv[5],&muW)||!readnum(argv[6],&mub)||
       mass1<200||mass2<mass1||mass2>10000||tanb<.25||tanb>100||
       gamma<0||gamma>1.57079632679489662||muW<80||muW>320||
       mub<2||mub>6){
        fprintf(stderr,"F3_USAGE mH1 mH2 tanbeta gamma muW mub\n");return 2;
    }
    Init_param(&p);slha_adjust(&p);
    p.THDM_model=2;p.tan_beta=tanb;
    for(int i=1;i<=3;i++){
        p.lambda_u[i][i]=1./tanb;
        p.lambda_d[i][i]=-tanb;
        p.lambda_l[i][i]=-tanb;
    }
    if(!match(&p,mass1,1,muW,&sm)||
       !match(&p,mass1,0,muW,&l)||
       !match(&p,mass2,0,muW,&h)||
       !evolve(&p,&sm,mass1,muW,mub,&lowSM)){
        fprintf(stderr,"F3_CW_OR_RG_NONFINITE\n");return 3;
    }
    double w1=cos(gamma)*cos(gamma),w2=sin(gamma)*sin(gamma);
    if(fabs(w1+w2-1.)>1e-12)return 3;
    printf("STATUS F3_SOURCE_PINNED_NLO_RG_DIAGNOSTIC_NOT_BR_OR_EXCLUSION\n");
    printf("INPUT mass1=%.17g mass2=%.17g tanbeta=%.17g gamma=%.17g muW=%.17g mub=%.17g w1=%.17g w2=%.17g\n",
           mass1,mass2,tanb,gamma,muW,mub,w1,w2);
    for(int mode=0;mode<3;mode++) {
        for(int j=0;j<NC;j++){
            z.a[j]=sm.a[j]+w1*(l.a[j]-sm.a[j])+w2*(h.a[j]-sm.a[j]);
            z.b[j]=sm.b[j];
            z.c[j]=sm.c[j];
            if(mode>0 && (mode==2||j==7||j==8))
                z.b[j]+=w1*(l.b[j]-sm.b[j])+w2*(h.b[j]-sm.b[j]);
        }
        if(!evolve(&p,&z,mass1,muW,mub,&lowZ)){
            fprintf(stderr,"F3_COHERENT_RG_NONFINITE mode=%d\n",mode);return 3;
        }
        for(int j=1;j<=8;j++){
            const double da=creal(lowZ.a[j]-lowSM.a[j]);
            const double db=creal(lowZ.b[j]-lowSM.b[j]);
            const double ha=creal(z.a[j]-sm.a[j]);
            const double hb=creal(z.b[j]-sm.b[j]);
            if(!isfinite(da)||!isfinite(db)||!isfinite(ha)||!isfinite(hb))
                return 3;
            printf("WC mode=%d op=%d hiLO=%.17g hiNLO=%.17g loLO=%.17g loNLO=%.17g SMloLO=%.17g SMloNLO=%.17g\n",
                   mode,j,ha,hb,da,db,creal(lowSM.a[j]),creal(lowSM.b[j]));
        }
    }
    printf("F3_WC_XF_FOURQUARK_TRANSLATION_ASSUMED false\n");
    printf("F3_PUBLISHED_NLO_TYPEII_RATE_VALIDATED false\n");
    printf("F3_EXCLUSION UNKNOWN\n");
    return 0;
}
