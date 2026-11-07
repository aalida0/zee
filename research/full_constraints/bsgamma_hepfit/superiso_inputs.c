/* Read-only D9B normalization/input receipt. GPL-3.0-or-later. */
#include "include.h"
#define OUT(k,x) printf(k " %.17g\n",(double)(x))
int main(void) {
    struct parameters p; Init_param(&p); slha_adjust(&p); p.SM=1;
    OUT("C_sem",C_BXlnu(&p)); OUT("BRsem",p.BR_BXclnu_exp);
    OUT("CKMratio",pow(cabs(conj(p.Vts)*p.Vtb/p.Vcb),2.));
    OUT("overall",p.BR_BXclnu_exp*pow(cabs(conj(p.Vts)*p.Vtb/p.Vcb),2.)*6./137.036/pi/C_BXlnu(&p));
    OUT("mc_at_2",running_mass(p.mass_c,p.mass_c,2.,p.mass_top_pole,p.mass_b,&p));
    OUT("mc_at_3",running_mass(p.mass_c,p.mass_c,3.,p.mass_top_pole,p.mass_b,&p));
    OUT("mu_c",p.mu_c_bsg); OUT("mu_b",p.mass_b_pole/2.);
    OUT("Mbkin",p.mass_b+.37); OUT("mtop_pole",p.mass_top_pole);
    OUT("muG2",p.mu_G2_bsg); OUT("rhoD3",p.rho_D3_bsg); OUT("rhoLS3",p.rho_LS3_bsg);
    return 0;
}
