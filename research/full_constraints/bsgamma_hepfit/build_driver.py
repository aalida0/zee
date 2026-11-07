"""Link the bounded client to unmodified upstream CMake library targets."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
from provenance import verify_source


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--root-config', type=Path, required=True)
    p.add_argument('--rgesolver-config', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--compat-lib-dir', type=Path)
    args = p.parse_args()
    verify_source(args.source)
    def flags(exe, flag):
        return shlex.split(subprocess.check_output([str(exe), flag], text=True))
    includes = [f'-I{x}' for x in sorted(args.source.glob('*/src'))]
    libs = [str(args.build / x / f'lib{x}.a') for x in
            ['StandardModel', 'Flavour', 'THDM', 'LeptonFlavour', 'LoopFunctions']]
    compat = []
    rge_libs = flags(args.rgesolver_config, '--libs')
    if args.compat_lib_dir:
        compat = [f'-L{args.compat_lib_dir}', f'-Wl,-rpath,{args.compat_lib_dir}',
                  f'-Wl,-rpath-link,{args.compat_lib_dir}']
        rge_libs = ['-l:libgsl.so.25' if x == '-lgsl' else x for x in rge_libs]
    cmd = ['g++', '-O2', '-Wall', *compat, *flags(args.root_config, '--cflags'),
           *flags(args.rgesolver_config, '--cflags'), *includes,
           str(Path(__file__).with_name('driver.cpp')), '-Wl,--start-group', *libs,
           *rge_libs, '-Wl,--end-group',
           *flags(args.root_config, '--libs'), '-lMathMore', '-lgfortran',
           '-o', str(args.output)]
    print(json.dumps(cmd), flush=True)
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
