/* Gate A1P: direct SuperIso v5 running-top mass audit at muW=2*mW.
 *
 * This program calls the EXACT function invoked by src/wilson.c:1599,
 * using the matching pilot's Init_param + slha_adjust context.
 * No model-specific Higgs prediction, no BR, no source patch.
 */
#include "include.h"
#include <math.h>
#include <stdio.h>

int main(void)
{
    struct parameters p;
    Init_param(&p);
    slha_adjust(&p);
    const double muW=2.*p.mass_W;
    const double mt=running_mass(p.mtmt,p.mtmt,muW,
                                 p.mass_top_pole,p.mass_b,&p);
    if(!(isfinite(mt)&&mt>100.&&mt<250.&&
         isfinite(muW)&&muW>50.&&muW<1000.)) {
        fprintf(stderr,"INVALID_GATE_A1P_TOP_MASS muW=%.17g mt=%.17g\n",
                muW,mt);
        return 1;
    }
    printf("STATUS SUPERISO_EXACT_RUNNING_TOP_FUNCTION_EVALUATED\n");
    printf("SUPERIOMT mtmuW_GeV=%.17g muW_GeV=%.17g "
           "mtmt_input_GeV=%.17g mtpole_input_GeV=%.17g "
           "mb_input_GeV=%.17g\n",
           mt,muW,p.mtmt,p.mass_top_pole,p.mass_b);
    return 0;
}
