/*
 * Gate A1V: operational flavor scan kernel based on validated A1U.
 * Reuse the EXACT A1U source-pinned SuperIso matching/interposition,
 * varying a bookkeeping parameter k in C(k) = C_SM + k(C_Zee-C_SM).
 *
 * k=0, +/-1, 0.5, 2 isolate interference and quadratic pieces.
 * k is NOT an independently physical mixing angle or model point.
 * Calls to the full vendor observable use genuine mixed high+low WC.
 * Do not infer exclusion or a calibrated theory error from this pilot.
 */
#define main gateA1u_original_main
#include "gateA1u_legacy_two_state_br.c"
#undef main

static void scaled_wc(struct wc *dest,const struct wc *sm,
                      const struct wc *zee,double k)
{
    int i;
    for(i=0;i<NWC;i++) {
        dest->C0[i]=sm->C0[i]+k*(zee->C0[i]-sm->C0[i]);
        dest->C1[i]=sm->C1[i]+k*(zee->C1[i]-sm->C1[i]);
        dest->C2[i]=sm->C2[i]+k*(zee->C2[i]-sm->C2[i]);
        dest->Cp[i]=sm->Cp[i]+k*(zee->Cp[i]-sm->Cp[i]);
    }
}
static double eval_wc(const struct wc *high,struct parameters *p,
                      double m1,double muW,double mub)
{
    struct low_wc low;
    if(!evolve(high,p,m1,1,muW,mub,&low)) return -1.;
    return observable_at_fixed_low(&low,high,p,m1,1,muW,mub,1);
}
int main(int argc,char **argv)
{
    double m1,m2,gamma,tanb,fw,fb,muW,mub,w1,w2;
    double x[5]={-1.,0.,0.5,1.,2.};
    double br[5],b0,linear,quad,pred05,pred2,refsm;
    struct parameters p;
    struct wc sm={0},h1={0},h2={0},zee={0},at_k={0};
    int i;
    if(argc!=8 || strcmp(argv[7],"helper_reload") ||
       !parse_input(argv[1],&m1) ||
       !parse_input(argv[2],&m2) ||
       !parse_input(argv[3],&gamma) ||
       !parse_input(argv[4],&tanb) ||
       !parse_input(argv[5],&fw) ||
       !parse_input(argv[6],&fb) ||
       !(m1>=200. && m1<=m2 && m2<=10000.) ||
       !(gamma>=0. && gamma<=1.57079632679489662) ||
       !(tanb>=0.25 && tanb<=100.) ||
       !(fw>=0.4 && fw<=2.5 && fb>=0.4 && fb<=2.5)) {
        fprintf(stderr,"A1V_INPUT_ERROR require mH1 mH2 gamma tanbeta muW_factor mub_factor helper_reload\n");
        return 2;
    }
    w1=cos(gamma)*cos(gamma);
    w2=sin(gamma)*sin(gamma);
    if(fabs(w1+w2-1.)>2.e-14) return 3;
    Init_param(&p);
    slha_adjust(&p);
    p.THDM_model=2;
    p.tan_beta=tanb;
    for(i=1;i<=3;i++) {
        p.lambda_u[i][i]=1./tanb;
        p.lambda_d[i][i]=-tanb;
        p.lambda_l[i][i]=-tanb;
    }
    muW=2.*p.mass_W*fw;
    mub=p.mass_b_pole/2.*fb;
    if(!isfinite(muW)||!isfinite(mub)||muW<60.||mub<0.8) {
        fprintf(stderr,"A1V_INVALID_SCALES\n");
        return 3;
    }
    if(!high_wc(&sm,&p,m1,1,muW,mub) ||
       !high_wc(&h1,&p,m1,0,muW,mub) ||
       !high_wc(&h2,&p,m2,0,muW,mub)) return 3;
    mix_wc(&zee,&sm,&h1,&h2,w1,w2);
    for(i=0;i<5;i++) {
        scaled_wc(&at_k,&sm,&zee,x[i]);
        br[i]=eval_wc(&at_k,&p,m1,muW,mub);
        if(!isfinite(br[i])||br[i]<=0.||br[i]>.01) {
            fprintf(stderr,"A1V_BAD_RATE k=%.17g value=%.17g\n",x[i],br[i]);
            return 3;
        }
        printf("A1V_K k=%.17g BR=%.17g\n",x[i],br[i]);
    }
    refsm=real_br(&sm,&p,m1,1,muW,mub);
    b0=br[1];
    linear=(br[3]-br[0])/2.;
    quad=(br[3]+br[0])/2.-b0;
    pred05=b0+0.5*linear+0.25*quad;
    pred2=b0+2.*linear+4.*quad;
    printf("A1V_INPUT mH1=%.17g mH2=%.17g gamma=%.17g tanbeta=%.17g "
           "muW_factor=%.17g mub_factor=%.17g muW=%.17g mub=%.17g\n",
           m1,m2,gamma,tanb,fw,fb,muW,mub);
    printf("A1V_DECOMP SM=%.17g LINEAR=%.17g QUADRATIC=%.17g "
           "FULL=%.17g RESIDUAL_HALF=%.17g RESIDUAL_DOUBLE=%.17g "
           "INDEPENDENT_SM=%.17g\n",
           b0,linear,quad,br[3],br[2]-pred05,br[4]-pred2,refsm);
    fflush(stdout);
    if(!isfinite(refsm)||fabs(refsm-b0)>2.e-12 ||
       fabs(br[2]-pred05)>5.e-11 ||fabs(br[4]-pred2)>5.e-11) {
        fprintf(stderr,"A1V_QUADRATIC_OR_SM_CLOSURE_FAILED\n");
        return 3;
    }
    printf("STATUS GATE_A1V_LEGACY_QUADRATIC_RESPONSE_NOT_FLAVOUR_EXCLUSION\n");
    return 0;
}
