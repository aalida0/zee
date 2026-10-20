/* Gate A1P: direct evaluation of the *actual* SuperIso v5 NNLO
 * charged-Higgs helper functions Delta3H and Delta4H.
 *
 * This probes the compiled provenance-pinned A1M SuperIso library;
 * no matching coefficient is modified. mt(muW) and tanbeta must be
 * supplied from the independently verified A1P input JSON.
 */
#include "include.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    if(argc != 3) {
        fprintf(stderr,"Usage: %s mt_muW tanbeta\n",argv[0]);
        return 2;
    }
    const double mt=strtod(argv[1],NULL);
    const double tanbeta=strtod(argv[2],NULL);
    if(!(isfinite(mt)&&mt>100.&&mt<250.&&
         isfinite(tanbeta)&&tanbeta>0.1&&tanbeta<1000.)) {
        fprintf(stderr,"Invalid top mass/tanbeta\n");
        return 2;
    }
    const double lu=1./tanbeta;
    const double masses[]={300.,700.,1000.,2000.};
    puts("STATUS GATE_A1P_ACTUAL_SUPERISO_HELPER_VALUES_NOT_BR");
    printf("INPUT mt_muW=%.17g tanbeta=%.17g\n",mt,tanbeta);
    for(unsigned i=0;i<sizeof(masses)/sizeof(masses[0]);i++) {
        const double mass=masses[i];
        const double x=(mt/mass)*(mt/mass);
        const double delta3=Delta3H(x,lu);
        const double delta4=Delta4H(x,lu);
        if(!isfinite(delta3)||!isfinite(delta4)) {
            fprintf(stderr,"Nonfinite helper result for mH=%.17g\n",mass);
            return 1;
        }
        printf("HELPER mass=%.17g op=3 value=%.17g\n",mass,delta3);
        printf("HELPER mass=%.17g op=4 value=%.17g\n",mass,delta4);
    }
    return 0;
}
