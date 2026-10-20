/* Gate A1P: read-only finite three-loop SuperIso charged-Higgs
 * helpers; all matching logarithms vanish by construction in this
 * diagnostic. Original A1M SuperIso source/library is NOT modified.
 *
 * Type-II at NNLO: C7,8^H,finite = cot^2(beta) * fn_lulu(x)
 *                                - fn_ldlu(x)
 * when lambda_u = cot beta, lambda_d = -tan beta.
 */
#include "include.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
int main(int argc, char**argv) {
    if(argc!=2) {
        fprintf(stderr,"Usage: %s fixed_running_mt_GeV\n",argv[0]);
        return 2;
    }
    char *end=NULL;
    const double mt=strtod(argv[1],&end);
    if(end==argv[1]||*end||!isfinite(mt)||mt<100||mt>250) {
        fputs("Invalid running top input\n",stderr);
        return 2;
    }
    const double masses[]={300.,700.,1000.,2000.};
    puts("STATUS GATE_A1P_ACTUAL_SUPERISO_THREE_LOOP_FINITE_HELPERS_NO_BR");
    printf("INPUT mt_fixed_GeV=%.17g\n",mt);
    for(unsigned j=0;j<sizeof(masses)/sizeof(masses[0]);j++) {
        const double m=masses[j], x=(mt/m)*(mt/m);
        const double ct7=C7H2lulumt(x),fr7=C7H2ldlumt(x);
        const double ct8=C8H2lulumt(x),fr8=C8H2ldlumt(x);
        if(!isfinite(ct7)||!isfinite(fr7)||!isfinite(ct8)||!isfinite(fr8)) {
            fprintf(stderr,"Nonfinite finite-loop helper at %.17g\n",m);
            return 1;
        }
        printf("FINITE mH=%.17g op=7 term=ct value=%.17g\n",m,ct7);
        printf("FINITE mH=%.17g op=7 term=fr value=%.17g\n",m,fr7);
        printf("FINITE mH=%.17g op=8 term=ct value=%.17g\n",m,ct8);
        printf("FINITE mH=%.17g op=8 term=fr value=%.17g\n",m,fr8);
    }
    return 0;
}
