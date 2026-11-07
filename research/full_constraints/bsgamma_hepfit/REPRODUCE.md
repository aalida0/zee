# Bounded HEPfit reproduction

Run from this repository root, on a clean scratch directory. Downloads,
sources, libraries and binaries stay outside Git. Do not change frozen
Modules0–13, D14, their receipts or the separate flavor worktree.
Only the original D12 scalar cards and exact algebraic controls are evaluated.

The host-specific commands below reproduce the executed environment.
`SOURCE_LOCK.json` pins downloaded source/package archives and the patched
build files. `BUILD_RECEIPT.json` separately records the reused ROOT/GSL
installation bytes and their original archives. On another host, restore
compatible pinned dependencies before running, and record a fresh build
receipt; binary hashes need not match across different compilers/build paths.
The numerical receipt checks remain mandatory.

```bash
scratch=/tmp/zee-hepfit
task_dir="$PWD/research/full_constraints/bsgamma_hepfit"
hepfit_src="$scratch/HEPfit-322bd73a2dadd94ce94a6d71cb79d616e569120a"
gslpp_src="$scratch/gslpp-f5b059e058a47f6797823a3846fd2cf9d17ff12c"
rge_src="$scratch/RGESolver-d1eb75559e03ae74a9ed0532760560757ef3beec"
compat_dir="$scratch/compat/usr/lib/x86_64-linux-gnu"
mkdir -p "$scratch"

curl -fLsS https://codeload.github.com/silvest/HEPfit/tar.gz/322bd73a2dadd94ce94a6d71cb79d616e569120a -o "$scratch/source.tar.gz"
curl -fLsS https://codeload.github.com/silvest/gslpp/tar.gz/f5b059e058a47f6797823a3846fd2cf9d17ff12c -o "$scratch/gslpp.tar.gz"
curl -fLsS https://codeload.github.com/silvest/RGESolver/tar.gz/d1eb75559e03ae74a9ed0532760560757ef3beec -o "$scratch/rgesolver.tar.gz"
curl -fLsS https://archive.ubuntu.com/ubuntu/pool/universe/t/tbb/libtbb2_2020.3-1ubuntu3_amd64.deb -o "$scratch/libtbb2.deb"

python3 - "$scratch" "$task_dir/SOURCE_LOCK.json" <<'PY'
import sys,json,hashlib,pathlib
root=pathlib.Path(sys.argv[1])
for name,digest in json.load(open(sys.argv[2]))['archives'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
PY

tar -xzf "$scratch/source.tar.gz" -C "$scratch"
tar -xzf "$scratch/gslpp.tar.gz" -C "$scratch"
tar -xzf "$scratch/rgesolver.tar.gz" -C "$scratch"
cp -a "$gslpp_src/src" "$hepfit_src/gslpp/"
cp "$gslpp_src/CMakeLists.txt" "$hepfit_src/gslpp/"
cp -a "$gslpp_src/src" "$rge_src/gslpp/"
patch -d "$hepfit_src" -p1 --batch -i "$task_dir/initialize_matching.patch"
python3 "$task_dir/provenance.py" --source "$hepfit_src"

cmake -S "$rge_src" -B "$scratch/rge-build" -DCMAKE_INSTALL_PREFIX="$scratch/deps" -DROOT_CONFIG_DIR=/home/amine/root/bin
cmake --build "$scratch/rge-build" --target RGESolver -j2
cmake --install "$scratch/rge-build"
cmake -S "$hepfit_src" -B "$scratch/build" -DNOMCMC=ON -DBAT_INSTALL=OFF -DROOT_CONFIG_DIR=/home/amine/root/bin -DRGESOLVER_CONFIG_DIR="$scratch/deps/bin" -DCMAKE_INSTALL_PREFIX="$scratch/install"
cmake --build "$scratch/build" --target StandardModel THDM Flavour LeptonFlavour LoopFunctions -j2

mkdir -p "$scratch/compat"
dpkg-deb -x "$scratch/libtbb2.deb" "$scratch/compat"
cp /home/amine/codes/Herwig/herwigpp/lib/libgsl.so.25.1.0 "$compat_dir/"
ln -s libgsl.so.25.1.0 "$compat_dir/libgsl.so.25"
python3 "$task_dir/build_driver.py" --source "$hepfit_src" --build "$scratch/build" --root-config /home/amine/root/bin/root-config --rgesolver-config "$scratch/deps/bin/rgesolver-config" --compat-lib-dir "$compat_dir" --output "$scratch/driver"

mkdir -p "$scratch/superiso"
python3 -c 'import hashlib; assert hashlib.sha256(open("/home/amine/Downloads/superiso_v5.0.tgz","rb").read()).hexdigest()=="7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f"'
tar -xzf /home/amine/Downloads/superiso_v5.0.tgz -C "$scratch/superiso"
patch -d "$scratch/superiso/SuperIso_v5.0" -p1 --batch -i "$PWD/module5/patches/d9b_superiso_v5.0.patch"
# Serial: upstream ar-member rules are unsafe under parallel make.
make -C "$scratch/superiso/SuperIso_v5.0" -B -j1
gcc -O2 -I "$scratch/superiso/SuperIso_v5.0/src" scripts/zee_d9b_rate_probe.c "$scratch/superiso/SuperIso_v5.0/src/libsuperiso.a" -lm -o "$scratch/superiso_probe"
gcc -O2 -I "$scratch/superiso/SuperIso_v5.0/src" "$task_dir/superiso_inputs.c" "$scratch/superiso/SuperIso_v5.0/src/libsuperiso.a" -lm -o "$scratch/superiso_inputs"

# Use a new output directory to preserve the committed execution receipt.
python3 "$task_dir/execute.py" --source "$hepfit_src" --binary "$scratch/driver" --superiso "$scratch/superiso_probe" --superiso-inputs "$scratch/superiso_inputs" --compat-lib-dir "$compat_dir" --root-lib-dir /home/amine/root/lib --output-dir "$scratch/replay"
python3 "$task_dir/provenance.py" --source "$hepfit_src" --execution "$scratch/replay/HEPFIT_EXECUTION.json"
python3 "$task_dir/capture_build.py" --scratch "$scratch" --root-prefix /home/amine/root --output "$scratch/BUILD_RECEIPT.json"
python3 -m unittest discover -s "$task_dir" -p 'test_*.py' -v
python3 research/full_constraints/verify_evidence.py
git diff --check
```

The SuperIso archive must have SHA256
`7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f`.
Its tracked patch and the frozen BMU evaluator/card bytes are checked by the
runner against the parent manifest. The commands above do not run the frozen
validator that rewrites original validation reports.

Tests read the **committed** execution receipts. To validate a fresh runtime
replay, also run the explicit `provenance.py --execution` command above and
compare its numerical values with the committed JSON. Implementation
tolerances do not imply a physical theory error.

The unpatched initialization falsifier is separately source-bound in
`receipts/initialization-falsifier-build.log`: the exact original
THDMMatching.cpp is extracted from the pinned archive, authenticated against
the original task SHA, compiled before the static libraries and linked into
a separate scratch executable. Only its nonzero-storage witness is evidence
for the bug. Its rate is not an accepted physics prediction.

HEPfit and this adapter/patch are GPL-3.0-or-later; retain upstream notices
and provide complete corresponding source if distributing linked binaries.
This repository distributes no such binaries. Source pins, the patch and
build commands do not replace the GPL source obligations for a binary release.
