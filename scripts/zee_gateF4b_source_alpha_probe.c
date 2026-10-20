/* F4b immutable-source control: parameters used by the isolated SuperIso
 * matching/RG code. NOT a decay rate or model validation.
 * Build only under /home with the already provenance-checked A1M library.
 */
#include "include.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

static int number(const char *text, double *result) {
    char *end = NULL;
    errno = 0;
    *result = strtod(text, &end);
    return errno == 0 && end != text && *end == '\0' && isfinite(*result);
}
int main(int argc, char **argv) {
    double muw, mub;
    if (argc != 3 || !number(argv[1], &muw) ||
        !number(argv[2], &mub) || muw < 80. || muw > 320. ||
        mub < 2. || mub > 6.) {
        fprintf(stderr, "F4B_USAGE muW_GeV mub_GeV\n");
        return 2;
    }
    struct parameters p;
    Init_param(&p);
    slha_adjust(&p);
    double asw = alphas_running(muw, p.mass_top_pole, p.mass_b_pole, &p);
    double asb = alphas_running(mub, p.mass_top_pole, p.mass_b_pole, &p);
    double mt = running_mass(p.mtmt, p.mtmt, muw,
                             p.mass_top_pole, p.mass_b, &p);
    if (!(isfinite(asw) && asw > .08 && asw < .15 &&
          isfinite(asb) && asb > .15 && asb < .35 &&
          isfinite(mt) && mt > 100. && mt < 250.))
        return 3;
    printf("F4B_SOURCE_INPUT muW=%.17g mub=%.17g alphas_muW=%.17g "
           "alphas_mub=%.17g mt_running_muW=%.17g mtmt=%.17g "
           "mt_pole=%.17g mb_pole=%.17g\n",
           muw, mub, asw, asb, mt, p.mtmt,
           p.mass_top_pole, p.mass_b_pole);
    puts("F4B_NOT_A_BRANCHING_RATIO_OR_EXCLUSION");
    return 0;
}
