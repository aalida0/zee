#!/usr/bin/env bash
# Reuse installed libraries; no installation and no event generation.
set -eu
zgamma_prefix=${ZGAMMA_HERWIG_PREFIX:-/home/amine/codes/Herwig/herwigpp}
zgamma_sources="$zgamma_prefix/src/Herwig-7.3.0/Looptools/.libs"
mkdir -p /tmp/zee-zgamma-native
if [ ! -e /tmp/zee-zgamma-native/libgsl.so.25 ]; then
    ln -s "$zgamma_prefix/lib/libgsl.so.25.1.0" /tmp/zee-zgamma-native/libgsl.so.25
fi
g++ -O2 -I"$zgamma_prefix/include" \
    research/full_constraints/higgs/zgamma_pv_probe.cpp \
    "$zgamma_sources/libHwLooptools.a" \
    "$zgamma_sources/libHwLooptoolsCFC.a" \
    "$zgamma_sources/libHwLooptoolsXFC.a" \
    -L"$zgamma_prefix/lib/ThePEG" \
    -Wl,-rpath,"$zgamma_prefix/lib/ThePEG" \
    -Wl,-rpath,"$zgamma_prefix/lib" \
    -Wl,-rpath-link,"$zgamma_prefix/lib" \
    -lThePEG -lgfortran -lquadmath -o /tmp/zee-zgamma-pv-probe
