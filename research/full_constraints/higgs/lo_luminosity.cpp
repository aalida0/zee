// Independent fixed-card LO convolution control; LHAPDF supplies PDFs only.
// Output integral d(log x) [x f_i(x)] [(tau/x) f_j(tau/x)] = tau L_ij.
#include <LHAPDF/LHAPDF.h>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <memory>
int main(int argc, char **argv) {
  if(argc!=7) return 2;
  LHAPDF::setVerbosity(0);
  std::unique_ptr<LHAPDF::PDF> pdf(LHAPDF::mkPDF(argv[1],std::atoi(argv[2])));
  double mass=std::atof(argv[3]), energy=13000., q=std::atof(argv[4]);
  int n=std::atoi(argv[5]), id=std::atoi(argv[6]);
  if(mass<=0 || mass>=energy || q<=0 || n<2 || n%2 || (id!=21 && id!=5)) return 3;
  double tau=std::pow(mass/energy,2), low=std::log(tau), step=-low/n, sum=0;
  for(int i=0;i<=n;++i) {
    double x=std::exp(low+i*step), y=tau/x;
    x=std::min(1.,x); y=std::min(1.,y);
    double f=pdf->xfxQ(id,x,q)*pdf->xfxQ(id==21?21:-5,y,q);
    if(id==5) f+=pdf->xfxQ(-5,x,q)*pdf->xfxQ(5,y,q);
    sum+=(i==0 || i==n?1:i%2?4:2)*f;
  }
  std::cout << std::setprecision(17) << sum*step/3 << " " << pdf->alphasQ(q) << "\n";
}
