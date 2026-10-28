// Independent LHAPDF interface for the analytical Z-only convolution.
#include <LHAPDF/LHAPDF.h>
#include <memory>
static std::unique_ptr<LHAPDF::PDF> pdf;
extern "C" {
void d5_pdf_init() { pdf.reset(LHAPDF::mkPDF("NNPDF30_lo_as_0130",0)); }
double d5_xfx(int id,double x,double q) { return pdf->xfxQ(id,x,q); }
double d5_alpha(double q) { return pdf->alphasQ(q); }
}
