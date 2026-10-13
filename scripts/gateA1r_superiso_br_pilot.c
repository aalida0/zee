/*
 * Gate A1R: source-pinned SuperIso v5 inclusive B -> X_s gamma BR pilot.
 *
 * Build against the ALREADY isolated A1M SuperIso source + libisospin.a.
 * Do NOT change upstream SuperIso's bsgamma.c, wilson.c, RG or default
 * SM inputs. THDM_model=1 bypasses MSSM epsilon corrections.
 *
 * Supported cases:
 *   SM  : unmodified SuperIso SM observable
 *   V   : standard single Type-II charged Higgs, isolated A1M matching
 *   A   : same Type-II charged Higgs, but overwrite only C2w[3..8]
 *         with source-pinned original KIT Mathematica C3-C6 and
 *         *RAW* three-loop C7/C8 matching. Its LO/NLO remains A1M.
 *
 * This is a pilot full BR calculation, NOT a 95% CL bound or complete
 * independent NNLO observable validation; photon E0=1.6GeV is hardcoded
 * in pinned SuperIso src/bsgamma.c.
 */
#include "include.h"
#include <float.h>
#include <errno.h>

static int finite_positive(double a) { return isfinite(a) && a>0.; }

struct authors_control {
    double mass,muW,mt,tanb;
    double c2[9]; /* 3,4,5,6,7,8 */
};

static int read_author_file(const char *path, struct authors_control *out)
{
    FILE *f=fopen(path,"r");
    int i,version;
    char sha[128];
    const char *expected =
        "cb2d1328bc2542a6324e73efe6f89c43381efdc93db5e3b0ca8348db980645d8";
    if(!f) { perror("A1R author file"); return 0; }
    if(fscanf(f,"A1R_AUTHOR_NNLO %d\n",&version)!=1 || version!=1
       || fscanf(f,"SHA256 %127s\n",sha)!=1
       || strcmp(sha,expected)!=0
       || fscanf(f,"MASS %lf\n",&out->mass)!=1
       || fscanf(f,"MUW %lf\n",&out->muW)!=1
       || fscanf(f,"MT %lf\n",&out->mt)!=1
       || fscanf(f,"TANBETA %lf\n",&out->tanb)!=1
       || fscanf(f,"C2 %lf %lf %lf %lf %lf %lf",
                 &out->c2[3],&out->c2[4],&out->c2[5],
                 &out->c2[6],&out->c2[7],&out->c2[8])!=6) {
        fprintf(stderr,"A1R_BAD_AUTHOR_REFERENCE_FILE\n");
        fclose(f);
        return 0;
    }
    for(i=3;i<=8;i++) {
        if(!isfinite(out->c2[i])) {
            fprintf(stderr,"A1R_NONFINITE_AUTHOR_COEFF\n");
            fclose(f);
            return 0;
        }
    }
    if(!finite_positive(out->mass) || !finite_positive(out->muW)
       || !finite_positive(out->mt) || !finite_positive(out->tanb)) {
        fprintf(stderr,"A1R_INVALID_REFERENCE_INPUTS\n");
        fclose(f);
        return 0;
    }
    fclose(f);
    return 1;
}

static int same_number(double a,double b,double atol,double rtol)
{
    return fabs(a-b)<=atol+rtol*fmax(fabs(a),fabs(b));
}

static void print_matching(const double C0w[],const double C1w[],
                           const double C2w[])
{
    int i;
    for(i=1;i<=8;i++)
        printf("MATCH op=%d LO=%.17g NLO=%.17g NNLO=%.17g\n",
               i,C0w[i],C1w[i],C2w[i]);
}

int main(int argc,char **argv)
{
    struct parameters param;
    struct authors_control orig;
    double mH,tanbeta,muW,mub,mt,br;
    double C0w[11],C1w[11],C2w[11],SM0w[11],SM1w[11],SM2w[11];
    double C0b[11],C1b[11],C2b[11],Cp[11];
    double complex CQp[3];
    char *end;
    char mode;
    int i;
    if(argc<4 || argc>5) {
        fprintf(stderr,"usage: %s [S|V|A] mass_H_GeV tanbeta [author_NNLO_file]\n",
                argv[0]);return 2;
    }
    if(strlen(argv[1])!=1 ||
       (argv[1][0]!='S' && argv[1][0]!='V' && argv[1][0]!='A')) {
        fprintf(stderr,"A1R_INVALID_MODE\n");return 2;
    }
    mode=argv[1][0];
    if((mode=='A' && argc!=5) || (mode!='A' && argc!=4)) {
        fprintf(stderr,"A1R_WRONG_AUTHOR_INPUT_COMBINATION\n");return 2;
    }
    errno=0;
    mH=strtod(argv[2],&end);
    if(errno || !end || *end || !finite_positive(mH) || mH<200) {
        fprintf(stderr,"A1R_INVALID_CHARGED_MASS\n");return 2;
    }
    errno=0;
    tanbeta=strtod(argv[3],&end);
    if(errno || !end || *end || !finite_positive(tanbeta) ||
       tanbeta<0.25 || tanbeta>100) {
        fprintf(stderr,"A1R_INVALID_TANBETA\n");return 2;
    }
    if(mode=='A' && !read_author_file(argv[4],&orig)) return 2;

    Init_param(&param);
    slha_adjust(&param);
    param.SM=(mode=='S')?1:0;
    /* THDM_model!=0 uses explicit lambda Yukawas and skips MSSM loops. */
    param.THDM_model=1;
    param.mass_H=mH;
    param.tan_beta=tanbeta;
    for(i=1;i<=3;i++) {
        param.lambda_u[i][i]=1./tanbeta;
        param.lambda_d[i][i]=-tanbeta;
        param.lambda_l[i][i]=-tanbeta;
    }
    muW=2.*param.mass_W;
    mub=param.mass_b_pole/2.;
    mt=running_mass(param.mass_top,param.mass_top,muW,
                    param.mass_top_pole,param.mass_b_pole,&param);
    if(!finite_positive(muW) || !finite_positive(mub) ||
       !finite_positive(mt) || !finite_positive(param.mass_b_pole) ||
       !finite_positive(param.mass_W)) {
        fprintf(stderr,"A1R_INVALID_PINNED_VENDOR_SM_PARAMETERS\n");return 3;
    }

    if(mode=='A') {
        if(!same_number(mH,orig.mass,1e-9,1e-12) ||
           !same_number(muW,orig.muW,1e-8,1e-10) ||
           !same_number(mt,orig.mt,1e-8,1e-10) ||
           !same_number(tanbeta,orig.tanb,1e-11,1e-10)) {
            fprintf(stderr,
                    "A1R_ORIGINAL_INPUT_MISMATCH mH=%.17g/%.17g "
                    "muW=%.17g/%.17g mt=%.17g/%.17g tan=%.17g/%.17g\n",
                    mH,orig.mass,muW,orig.muW,mt,orig.mt,
                    tanbeta,orig.tanb);
            return 3;
        }
        param.SM=1;
        CW_calculator(SM0w,SM1w,SM2w,muW,&param);
        param.SM=0;
    }
    CW_calculator(C0w,C1w,C2w,muW,&param);
    if(mode=='A') {
        for(i=3;i<=8;i++) {
            /* Original c2HDM.m author C2[7/8] come from cH[3,7/8].
             * They are RAW dipole coefficients, not cHeff[2,7/8].
             * C_calculator_base1 applies effective rotation itself. */
            double old=C2w[i];
            C2w[i]=SM2w[i]+orig.c2[i];
            printf("AUTHOR_C2_OVERWRITE op=%d vendor=%.17g original_total=%.17g\n",
                   i,old,C2w[i]);
        }
    }
    C_calculator_base1(C0w,C1w,C2w,muW,C0b,C1b,C2b,mub,&param);
    Cprime_calculator(Cp,CQp,muW,mub,&param);
    br=bsgamma(C0b,C1b,C2b,Cp,mub,muW,&param);
    if(!isfinite(br) || br<=0. || br>0.01) {
        fprintf(stderr,"A1R_UNPHYSICAL_BR_CALCULATION %.17g\n",br);
        return 3;
    }
    printf("STATUS A1R_SUPERISO_V5_BR_PILOT_NOT_FLAVOUR_EXCLUSION\n");
    printf("INPUT mode=%c mass_H=%.17g tanbeta=%.17g muW=%.17g "
           "mu_b=%.17g mt_muW=%.17g E0_GeV=1.6\n",
           mode,mH,tanbeta,muW,mub,mt);
    print_matching(C0w,C1w,C2w);
    printf("LOW_SCALE C0_7=%.17g C1_7=%.17g C2_7=%.17g "
           "C0_8=%.17g C1_8=%.17g C2_8=%.17g\n",
           C0b[7],C1b[7],C2b[7],C0b[8],C1b[8],C2b[8]);
    printf("BR_B_TO_XS_GAMMA=%.17g\n",br);
    printf("OBSERVABLE_PHYSICAL_PRECISION_VALIDATED false\n");
    printf("ZEE_ALLOWED_OR_EXCLUDED undetermined\n");
    return 0;
}
