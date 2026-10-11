/*
 * Gate A1N — candidate inclusive B->Xs gamma with SuperIso v5.0.
 *
 * Independent driver linked to ONE already-built SuperIso library.
 * No modifications to upstream library or headers.
 *
 * This is a physics CONTROL, not validated Zee exclusion or final BR.
 * It uses SuperIso's CW_calculator -> C_calculator_base1 ->
 * Cprime_calculator -> bsgamma chain with E_gamma>1.6 GeV,
 * after summing charged-Higgs Wilson vectors at the SAME muW.
 * Only the chosen Type-II quark Yukawa texture is implemented.
 *
 * Caller must repeat with unmodified and isolated patched v5 libraries.
 */
#include "include.h"
#include <complex.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NWC 11
#define M1 300.
#define M2 700.
#define BETA 1.394
#define GAMMA 1.089

typedef struct {
    double complex C0[NWC],C1[NWC],C2[NWC];
} Wilson;

static int finite_wc(const Wilson *w) {
    for (int i=1;i<=10;i++) {
        if (!isfinite(creal(w->C0[i])) || !isfinite(cimag(w->C0[i])) ||
            !isfinite(creal(w->C1[i])) || !isfinite(cimag(w->C1[i])) ||
            !isfinite(creal(w->C2[i])) || !isfinite(cimag(w->C2[i]))) return 0;
    }
    return 1;
}

static void initialize(struct parameters *p) {
    Init_param(p);
    slha_adjust(p);
    const double tb=tan(BETA);
    p->tan_beta=tb;
    for (int g=1;g<=3;g++) {
        p->lambda_u[g][g]=1./tb;
        p->lambda_d[g][g]=-tb;
        p->lambda_l[g][g]=-tb;
    }
    /* THDM_model=2 is nonzero to route through native 2HDM,
       not a declaration that SuperIso knows the Zee model. */
    p->THDM_model=2;
    p->SM=0;
}

static int run_sm(struct parameters *p, Wilson *out, double muW) {
    struct parameters sm=*p;
    sm.SM=1;
    sm.THDM_model=0;
    sm.mass_H=M1;
    memset(out,0,sizeof(*out));
    CW_calculator(2,out->C0,out->C1,out->C2,muW,&sm);
    return finite_wc(out);
}

static int run_typeII(struct parameters *p, Wilson *out,
                      double mass, double muW) {
    struct parameters thdm=*p;
    thdm.SM=0;
    thdm.THDM_model=2;
    thdm.mass_H=mass;
    memset(out,0,sizeof(*out));
    CW_calculator(2,out->C0,out->C1,out->C2,muW,&thdm);
    return finite_wc(out);
}

static void compose(Wilson *out,const Wilson *sm,
                    const Wilson *h1,const Wilson *h2,
                    double w1,double w2) {
    for(int i=0;i<=10;i++) {
        out->C0[i]=sm->C0[i]+w1*(h1->C0[i]-sm->C0[i])
                           +w2*(h2->C0[i]-sm->C0[i]);
        out->C1[i]=sm->C1[i]+w1*(h1->C1[i]-sm->C1[i])
                           +w2*(h2->C1[i]-sm->C1[i]);
        out->C2[i]=sm->C2[i]+w1*(h1->C2[i]-sm->C2[i])
                           +w2*(h2->C2[i]-sm->C2[i]);
    }
}

static double evaluate(const char *label,
                       const Wilson *wc, struct parameters *p,
                       double muW,double mub,int pureSM,
                       double charged_mass,int scan_scale) {
    double complex c0b[NWC]={0},c1b[NWC]={0},c2b[NWC]={0};
    double complex cp[NWC]={0},cqp[3]={0};
    struct parameters point=*p;
    point.SM=pureSM?1:0;
    point.THDM_model=pureSM?0:2;
    /* Matching runs in temporary structs. Restore the same charged mass
       here for Cprime and bsgamma; otherwise point.mass_H defaults to 0. */
    point.mass_H=charged_mass;
    if (!(isfinite(point.mass_H) && point.mass_H>0.)) {
        fprintf(stderr,"Invalid charged-mass context for %s: %.17g\n",label,point.mass_H);
        return NAN;
    }
    /* CRITICAL: vendor API takes mutable arrays. Never cast away const
       and pass the shared matched Zee vector directly; every evaluation
       must receive a fresh independent copy to rule out call-order effects. */
    double complex c0w[NWC],c1w[NWC],c2w[NWC];
    memcpy(c0w,wc->C0,sizeof(c0w));
    memcpy(c1w,wc->C1,sizeof(c1w));
    memcpy(c2w,wc->C2,sizeof(c2w));
    C_calculator_base1(c0w,c1w,c2w,
                       muW,c0b,c1b,c2b,mub,&point);
    double highscale_mutation=0.;
    for(int i=1;i<=10;i++) {
        highscale_mutation=fmax(highscale_mutation,cabs(c0w[i]-wc->C0[i]));
        highscale_mutation=fmax(highscale_mutation,cabs(c1w[i]-wc->C1[i]));
        highscale_mutation=fmax(highscale_mutation,cabs(c2w[i]-wc->C2[i]));
    }
    if(!isfinite(highscale_mutation)) {
        fprintf(stderr,"High-scale array overwritten nonfinite for %s\n",label);
        return NAN;
    }
    if(strcmp(label,"ZEE_300_700")==0 ||
       strcmp(label,"ZEE_SAME_WC_ALT_MASS_700")==0 ||
        strcmp(label,"ZEE_REPEAT_MASS_300")==0 ||
        strcmp(label,"ZEE_REPEAT_MASS_700")==0) {
        printf("INPUTMUTATION %s max_abs=%.17g scale=%d\n",
               label,highscale_mutation,scan_scale);
    }
    /* Fail at the first invalid QCD-evolved Wilson coefficient, not at BR. */
    for (int i=1;i<=10;i++) {
        if(!isfinite(creal(c0b[i])) || !isfinite(cimag(c0b[i])) ||
           !isfinite(creal(c1b[i])) || !isfinite(cimag(c1b[i])) ||
           !isfinite(creal(c2b[i])) || !isfinite(cimag(c2b[i]))) {
            fprintf(stderr,"INVALID_RG_WC label=%s i=%d "
                    "C0=(%.17g,%.17g) C1=(%.17g,%.17g) "
                    "C2=(%.17g,%.17g) mass_H=%.17g muW=%.17g mub=%.17g\n",
                    label,i,creal(c0b[i]),cimag(c0b[i]),
                    creal(c1b[i]),cimag(c1b[i]),
                    creal(c2b[i]),cimag(c2b[i]),point.mass_H,muW,mub);
            return NAN;
        }
    }
    /* Diagnostic only: for identical Zee matching vectors, expose every
       post-RG coefficient to locate any hidden residual-mass dependence.
       Does not modify matching, RGE, Cprime, or BR input. */
    if (strcmp(label,"ZEE_300_700")==0 ||
        strcmp(label,"ZEE_SAME_WC_ALT_MASS_700")==0 ||
        strcmp(label,"ZEE_REPEAT_MASS_300")==0 ||
        strcmp(label,"ZEE_REPEAT_MASS_700")==0) {
        for (int i=1;i<=10;i++) {
            printf("RGEDETAIL %s i=%d C0re=%.17g C0im=%.17g "
                   "C1re=%.17g C1im=%.17g C2re=%.17g C2im=%.17g scale=%d\n",
                   label,i,creal(c0b[i]),cimag(c0b[i]),
                   creal(c1b[i]),cimag(c1b[i]),
                   creal(c2b[i]),cimag(c2b[i]),scan_scale);
        }
    }
    Cprime_calculator(2,cp,cqp,muW,mub,&point);
    /* SM chirality-flipped coefficients need not vanish. They are
       small but finite in SuperIso v5 even for its pure SM baseline.
       Never reject Cprime just because its norm is nonzero; instead
       record values and check their finiteness and consistency. */
    double cp_norm=0.;
    for (int i=1;i<=10;i++) {
        if(!isfinite(creal(cp[i])) || !isfinite(cimag(cp[i]))){
            fprintf(stderr,"Nonfinite Cprime[%d] for %s\n",i,label);
            return NAN;
        }
        cp_norm=fmax(cp_norm,cabs(cp[i]));
    }
    if (strcmp(label,"ZEE_300_700")==0 ||
        strcmp(label,"ZEE_SAME_WC_ALT_MASS_700")==0 ||
        strcmp(label,"ZEE_REPEAT_MASS_300")==0 ||
        strcmp(label,"ZEE_REPEAT_MASS_700")==0) {
        for (int i=1;i<=10;i++) {
            printf("CPALL %s i=%d re=%.17g im=%.17g scale=%d\n",
                   label,i,creal(cp[i]),cimag(cp[i]),scan_scale);
        }
    }
    double br=bsgamma(c0b,c1b,c2b,cp,mub,muW,&point);
    if (!isfinite(br) || br<=0. || br>=1. || !isfinite(cp_norm)) {
        fprintf(stderr,"FAILED BSGAMMA driver %s: BR=%g Cp_max=%g mass_H=%.17g muW=%.17g mub=%.17g THDM_model=%d SM=%d C0b7=%.17g C0b8=%.17g C1b7=%.17g C1b8=%.17g C2b7=%.17g C2b8=%.17g\n",label,br,cp_norm,point.mass_H,muW,mub,point.THDM_model,point.SM,creal(c0b[7]),creal(c0b[8]),creal(c1b[7]),creal(c1b[8]),creal(c2b[7]),creal(c2b[8]));
        return NAN;
    }
    printf("RESULT %s %.17g muW=%.17g mub=%.17g cpmax=%.17g scale=%d\n",
           label,br,muW,mub,cp_norm,scan_scale);
    printf("CPDETAIL %s C7p_re=%.17g C7p_im=%.17g "
           "C8p_re=%.17g C8p_im=%.17g scale=%d\n",
           label,creal(cp[7]),cimag(cp[7]),creal(cp[8]),cimag(cp[8]),
           scan_scale);
    return br;
}

static int run_suite(struct parameters *p,double muW,double mub,int scale_index) {
    Wilson sm={0},h1={0},h2={0},h1000={0},h2000={0};
    Wilson zee={0},endpoint1={0},endpoint2={0};
    if (!run_sm(p,&sm,muW) ||
        !run_typeII(p,&h1,M1,muW) ||
        !run_typeII(p,&h2,M2,muW) ||
        !run_typeII(p,&h1000,1000.,muW) ||
        !run_typeII(p,&h2000,2000.,muW)) {
        fputs("Nonfinite high-scale matching Wilson coefficient\n",stderr);
        return 1;
    }
    double w1=pow(cos(GAMMA),2.),w2=pow(sin(GAMMA),2.);
    if(fabs(w1+w2-1.)>1e-13) return 1;
    compose(&zee,&sm,&h1,&h2,w1,w2);
    compose(&endpoint1,&sm,&h1,&h2,1.,0.);
    compose(&endpoint2,&sm,&h1,&h2,0.,1.);

    struct { const char *name; const Wilson *wc; int sm; double mass; } cases[]={
        {"SM",&sm,1,M1},
        {"TYPEII_300",&h1,0,M1},
        {"TYPEII_700",&h2,0,M2},
        {"TYPEII_1000",&h1000,0,1000.},
        {"TYPEII_2000",&h2000,0,2000.},
        {"ZEE_300_700",&zee,0,M1},
        /* Identical WCs but a different residual param.mass_H:
           if bsgamma/Cprime depends on it, our Zee interface is incomplete. */
        {"ZEE_SAME_WC_ALT_MASS_700",&zee,0,M2},
        /* Order-dependence control. These are exactly identical
           source/mass cases repeated in the same running process. */
        {"ZEE_REPEAT_MASS_300",&zee,0,M1},
        {"ZEE_REPEAT_MASS_700",&zee,0,M2},
        {"ENDPOINT_H1",&endpoint1,0,M1},
        {"ENDPOINT_H2",&endpoint2,0,M2},
    };
    printf("RUN scale=%d muW=%.17g mub=%.17g w1=%.17g w2=%.17g\n",
           scale_index,muW,mub,w1,w2);
    for(size_t i=0;i<sizeof(cases)/sizeof(cases[0]);i++) {
        if (!isfinite(evaluate(cases[i].name,cases[i].wc,p,muW,mub,
                               cases[i].sm,cases[i].mass,scale_index))) return 1;
    }
    return 0;
}

int main(int argc,char **argv) {
    if(argc!=1) {
        fprintf(stderr,"Usage: %s (uses frozen Gate A1N parameters)\n",argv[0]);
        return 2;
    }
    (void)argv;
    struct parameters p;
    initialize(&p);
    if(!(p.mass_W>0. && p.mass_b_pole>0. && p.mass_top_pole>0.)) {
        fputs("Invalid default SuperIso SM inputs\n",stderr);
        return 1;
    }
    const double muW0=2.*p.mass_W, mub0=p.mass_b_pole/2.;
    printf("STATUS GATE_A1N_BR_CANDIDATE_NOT_VALIDATED_FOR_EXCLUSION\n");
    printf("INPUTS mH1=300 mH2=700 gamma=1.089 beta=1.394 tanbeta=%.17g "
           "Egamma_min_GeV=1.6\n",tan(BETA));
    if (run_suite(&p,muW0,mub0,0)) return 1;
    if (run_suite(&p,muW0/2.,mub0,1)) return 1;
    if (run_suite(&p,muW0*2.,mub0,2)) return 1;
    if (run_suite(&p,muW0,mub0*0.8,3)) return 1;
    if (run_suite(&p,muW0,mub0*1.5,4)) return 1;
    puts("STATUS_END GATE_A1N_BR_CANDIDATE_NO_EXCLUSION");
    return 0;
}
