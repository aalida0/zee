// Research-only HEPfit library client. GPL-3.0-or-later.
// Uses the public eight-operator, order-tagged matching interface.
#include "THDM.h"
#include "bsgamma.h"
#include "bsgammaTHDM.h"
#include "Flavour.h"
#include <array>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <cstring>

class CoherentMatching : public THDMMatching {
    const THDM& model;
    WilsonCoefficient np;
    std::vector<WilsonCoefficient> result;
public:
    std::array<std::array<double,8>,2> ordinary{};
    explicit CoherentMatching(const THDM& m): THDMMatching(m), model(m), np(8,NDR,NNLO) {}
    std::vector<WilsonCoefficient>& CMbsg() override {
        updateSMParameters();
        result.clear();
        // WilsonTemplate has a deep copy constructor but no deep assignment.
        // Reconstruct entries; assigning live entries would alias owning pointers.
        for(const auto& sm : StandardModelMatching::CMbsg()) result.push_back(sm);
        np.setMu(model.getMuw());
        for (int o=0; o<3; ++o) {
            std::array<double,8> c{};
            if (o<2) c=ordinary[o];
            // Ordinary BMU -> effective dipoles, at EACH retained order.
            c[6] -= c[2]/3.+4.*c[3]/9.+20.*c[4]/3.+80.*c[5]/9.;
            c[7] += c[2]-c[3]/6.+20.*c[4]-10.*c[5]/3.;
            double weight = o==0 ? 1. : (o==1 ? model.Alstilde5(model.getMuw()) : 0.);
            for(int i=0;i<8;++i) np.setCoeff(i,weight*c[i],static_cast<orders>(o));
        }
        result.push_back(np);
        return result;
    }
};

class CoherentModel : public THDM {
    mutable CoherentMatching matching;
public:
    CoherentModel():THDM(),matching(*this) { SMM.setObj(matching); }
    THDMMatching& getMatching() const override { return matching; }
    CoherentMatching& bridge() { return matching; }
};

void value(const std::string& key,double v) {
    if(!std::isfinite(v)) throw std::runtime_error("Nonfinite output: "+key);
    std::cout << "VALUE " << key << " " << v << "\n";
}

int main(int argc,char** argv) {
 try {
    if(argc!=3) throw std::runtime_error("Usage: driver sm|thdm|bridge input.txt");
    std::string mode=argv[1];
    if(mode!="sm" && mode!="thdm" && mode!="bridge") throw std::runtime_error("Invalid mode");
    std::cout << std::setprecision(17);
    std::unique_ptr<StandardModel> model;
    if(mode=="sm") model=std::make_unique<StandardModel>();
    else if(mode=="thdm") model=std::make_unique<THDM>();
    else model=std::make_unique<CoherentModel>();
    model->setModelName(mode=="sm" ? "StandardModel" : "THDM");
    // Historical upstream Bsgamma cards explicitly specify a POLE top mass.
    // QCD's current default has changed to MSbar; never interpret 173.2 as MSbar.
    model->setFlag("FlagMtPole",true);
    model->InitializeModel();
    if(mode!="sm") model->setFlagStr("modelTypeflag","type2");
    if(mode!="sm") model->setFlagStr("RGEorder","approxNLO");
    Bsgamma obs(*model,QCD::STRANGE,1);
    model->addParameters(obs.getParametersForObservable());
    obs.setBinMin(1.6);
    std::map<std::string,double> pars;
    std::ifstream input(argv[2]);
    if(!input) throw std::runtime_error("Missing input");
    std::string key; double v;
    while(input>>key>>v) {
        if(key.rfind("NP",0)==0) {
            if(mode!="bridge" || key.size()!=5) throw std::runtime_error("Bad NP field");
            int order=key[2]-'0', index=key[4]-'1';
            if(order<0||order>1||index<0||index>7) throw std::runtime_error("Bad NP index");
            static_cast<CoherentModel&>(*model).bridge().ordinary[order][index]=v;
        } else pars[key]=v;
    }
    if(!input.eof()) throw std::runtime_error("Malformed input");
    for(const auto& p:pars) std::cout<<"INPUT "<<p.first<<" "<<p.second<<"\n";
    if(!model->Init(pars)) throw std::runtime_error("HEPfit Init failed");
    for(const auto& p:model->getUnknownParameters()) std::cout<<"UNKNOWN_INPUT "<<p<<"\n";
    const double mub=model->getOptionalParameter("mu_b_bsgamma");
    const double muc=model->getOptionalParameter("mu_c_bsgamma");
    obs.updateParameters();
    if(mode!="sm") {
        // Falsifier for omitted initialization: unused operator slots must be
        // zero even if the raw object storage was previously nonzero.
        alignas(THDMMatching) unsigned char storage[sizeof(THDMMatching)];
        std::memset(storage,0x3f,sizeof(storage));
        auto& thdm=static_cast<THDM&>(*model);
        auto* witness=new(storage) THDMMatching(thdm);
        double mt=model->Mrun(model->getMut(),model->getQuarks(QCD::TOP).getMass_scale(),model->getQuarks(QCD::TOP).getMass(),QCD::TOP,FULLNNLO);
        value("initialized_unused_NNLO_C1",witness->setWCbsg(0,thdm.gettanb(),mt,thdm.getmHp(),model->getMuw(),NNLO));
        value("initialized_unused_LO_C1",witness->setWCbsg(0,thdm.gettanb(),mt,thdm.getmHp(),model->getMuw(),LO));
        witness->~THDMMatching();
    }
    value("cut_GeV",obs.getBinMin());
    value("muw_GeV",model->getMuw()); value("mut_GeV",model->getMut());
    value("mu_b_GeV",mub); value("mu_c_GeV",muc);
    value("Mw_GeV",model->Mw());
    value("mt_MSbar_at_mt",model->getQuarks(QCD::TOP).getMass());
    value("mt_input_scale_GeV",model->getQuarks(QCD::TOP).getMass_scale());
    value("mt_MSbar_mut",model->Mrun(model->getMut(),model->getQuarks(QCD::TOP).getMass_scale(),model->getQuarks(QCD::TOP).getMass(),QCD::TOP,FULLNNLO));
    value("a_s_muw",model->Alstilde5(model->getMuw()));
    value("a_s_mub",model->Alstilde5(mub));
    value("CKMratio",(model->getCKM().computelamt_s()/model->getCKM().getV_cb()).abs2());
    auto ckm=model->getVCKM();
    for(int i=0;i<3;++i) for(int j=0;j<3;++j) {
        value("CKM_re_"+std::to_string(i)+"_"+std::to_string(j),ckm(i,j).real());
        value("CKM_im_"+std::to_string(i)+"_"+std::to_string(j),ckm(i,j).imag());
    }
    value("C_sem",obs.C_sem());
    double norm=model->getOptionalParameter("BRsem")/100.*(model->getCKM().computelamt_s()/model->getCKM().getV_cb()).abs2()*6.*model->getAle()/(M_PI*obs.C_sem());
    value("overall",norm);
    value("P_LO",obs.P(1.6,mub,muc,LO));
    value("P_NLO",obs.P(1.6,mub,muc,NLO));
    value("P_NNLO",obs.P(1.6,mub,muc,NNLO));
    value("P11_weighted",model->Alstilde5(mub)*obs.P11());
    value("P21_weighted",model->Alstilde5(mub)*obs.P21(1.6,mub));
    value("P_Vub_NLO",obs.Vub_NLO(1.6));
    value("P_EW_NLO",model->ale_OS(model->getMz())/(4.*M_PI)*obs.EW_NLO(mub));
    value("N_27",obs.N_27()); value("N_77",obs.N_77(1.6,mub));
    value("N",obs.N(1.6,mub));
    value("BR_NLO",norm*(obs.P(1.6,mub,muc,NLO)+obs.N(1.6,mub)));
    value("BR_stock_NNLO",obs.computeThValue());
    if(mode=="thdm") {
        bsgammaTHDM table(*model);
        value("BR_TypeII_table",table.computeThValue());
    }
    auto high=model->getMatching().CMbsg();
    for(size_t k=0;k<high.size();++k) for(int o=0;o<3;++o) for(int i=0;i<8;++i) {
        auto z=(*high[k].getCoeff(static_cast<orders>(o)))(i);
        value("high_"+std::to_string(k)+"_"+std::to_string(o)+"_"+std::to_string(i+1),z.real());
        value("high_im_"+std::to_string(k)+"_"+std::to_string(o)+"_"+std::to_string(i+1),z.imag());
    }
    auto low=model->getFlavour().ComputeCoeffsgamma(mub);
    for(int o=0;o<3;++o) for(int i=0;i<8;++i) {
        auto z=(*low[o])(i);
        value("low_"+std::to_string(o)+"_"+std::to_string(i+1),z.real());
        value("low_im_"+std::to_string(o)+"_"+std::to_string(i+1),z.imag());
    }
    return 0;
 } catch(const std::exception& e) { std::cerr<<"ERROR "<<e.what()<<"\n"; return 1; }
}
