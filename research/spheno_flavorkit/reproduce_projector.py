"""Recover the official projector in disposable local copies, then run the toy.

Archives are downloaded separately from the official URLs (see audit). This
script validates hashes, extracts to local/d15_projector_toolchain, builds only
symbolic helpers, and runs Mathematica. No installed package is changed.
"""
from pathlib import Path
import hashlib
import subprocess
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parent
LOCAL=ROOT/'local'
ARCHIVES={
 'FeynArts-3.9.tar.gz':'1add14aea4f3ee09b29e88438ad105ccd7df48969514c6b902f6c57bee303963',
 'FormCalc-7.5.tar.gz':'59e56b0cf32e906578b419bca740a4ee31eda36af4074e9dacee22db0b324a0c',
 'PreSARAH-1.0.3.download':'999142f4d4283bb70b225809e44440fd1ee29e289f1d956c051536e0bf1279bf'}


def main():
    work=Path(tempfile.mkdtemp(prefix='d15_projector_',dir=LOCAL))
    for name,digest in ARCHIVES.items():
        archive=LOCAL/name
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==digest,name
        with tarfile.open(archive) as tar:
            # Archives are pinned; also enforce path containment.
            for member in tar.getmembers():
                target=(work/member.name).resolve()
                assert target.is_relative_to(work.resolve())
                if member.issym():
                    assert (target.parent/member.linkname).resolve().is_relative_to(work.resolve())
                if member.islnk():
                    assert (work/member.linkname).resolve().is_relative_to(work.resolve())
            tar.extractall(work)
    # Compatibility-only path discovery: old FileInformation used symbol keys;
    # Wolfram 15 uses string keys. No algebraic simplification is patched.
    for relative in ['FeynArts-3.9/FeynArts.m','FormCalc-7.5/FormCalc75.m']:
        f=work/relative; s=f.read_text()
        if relative.startswith('FeynArts'):
            s=s.replace('(File /. FileInformation[System`Private`FindFile[$Input]])','$InputFileName')
            s=s.replace('Discard','D15ObsoleteDiscard')
        else:
            s=s.replace('File /.\n  FileInformation[System`Private`FindFile[$Input]]','$InputFileName')
        f.write_text(s)
    f=work/'PreSARAH-1.0.3/PreSARAH_package.m'
    f.write_text(f.read_text().replace('System`Private`FindFile[$Input]','$InputFileName'))
    # Wolfram 15 has MathLink SDK but no legacy mcc wrapper. The required
    # symbolic tools can be built directly, retaining the package sources.
    result=subprocess.run(['math','-noprompt','-run','Print[$InstallationDirectory];Quit[]'],capture_output=True,text=True,check=True)
    install=Path(result.stdout.strip().strip('"'))
    sdk=install/'SystemFiles/Links/MathLink/DeveloperKit/Linux-x86-64/CompilerAdditions'
    fc=work/'FormCalc-7.5'; binaries=fc/'Linux-x86-64'; binaries.mkdir(exist_ok=True)
    with (work/'build.log').open('w') as log:
        def run(args): subprocess.run(list(map(str,args)),stdout=log,stderr=log,check=True)
        for src in ['FormCalc/ReadForm.tm','tools/ReadData.tm']:
            out=binaries/Path(src).stem; c=out.with_suffix('.c')
            run([sdk/'mprep',fc/src,'-o',c])
            run(['gcc','-O2','-DMLCONST=const','-I'+str(sdk),c,'-L'+str(sdk),'-Wl,-rpath,'+str(sdk),'-lML64i4','-lpthread','-lrt','-ldl','-lm','-lstdc++','-o',out])
        for src in ['FormCalc/ToForm.c','FormCalc/ToFortran.c','FormCalc/ToC.c','tools/reorder.c']:
            run(['gcc','-O2',fc/src,'-o',binaries/Path(src).stem])
    load=f'''BeginPackage["LoopTools`"]
{{bb0,bb1,cc0,cc00,cc1,cc2,cc12,cc22,cc11,dd0,dd00}};
EndPackage[]
Get["{work}/FeynArts-3.9/FeynArts.m"];
Get["{work}/FormCalc-7.5/FormCalc.m"];
Get["{work}/PreSARAH-1.0.3/PreSARAH_package.m"];
Unprotect[Paint]; Clear[Paint]; Paint[___]:=Null;
SetOptions[DeclareProcess,MomElim->2];
GetCodeForSARAH["PhotonLLp.m"];
Put[ampSave,"{work}/ampSave.m"];
Put[TriangleOperators,"{work}/projectors.m"];
Print["D15_REGEN_DONE"];
Quit[];
'''
    script=work/'regenerate.m';script.write_text(load)
    with (work/'regenerate.log').open('w') as log:
        subprocess.run(['math','-noprompt','-script',str(script)],stdout=log,stderr=log,check=True,timeout=180)
    assert 'D15_REGEN_DONE' in (work/'regenerate.log').read_text()
    toy=work/'run-toy.m';toy.write_text(f'D15Local="{work}";\nGet["{ROOT}/projector_toy.m"];\n')
    with (work/'toy.log').open('w') as log:
        subprocess.run(['math','-noprompt','-script',str(toy)],stdout=log,stderr=log,check=True,timeout=180)
    assert 'D15_TOY_DONE' in (work/'toy.log').read_text()
    subprocess.run(['python3',str(ROOT/'compare_projector_sources.py'),str(work/'PreSARAH-1.0.3/Output/Gamma2l.m')],check=True)
    print(work)

if __name__=='__main__': main()
