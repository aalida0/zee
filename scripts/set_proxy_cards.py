#!/usr/bin/env python3
"""Configure 2HDM Type-II production-only screening cards. Not a Zee UFO."""
import pathlib, re, sys
if len(sys.argv) != 2:
    sys.exit("Usage: set_proxy_cards.py /path/to/MG5/process")
root=pathlib.Path(sys.argv[1])
pc=root/"Cards/param_card.dat"
rc=root/"Cards/run_card.dat"
if not pc.exists() or not rc.exists():
    sys.exit("ABORT: MG5 cards not found")
masses={37:700.0,25:125.0,35:580.7,36:633.7}
fr={1:5.7294462974594245,2:1.0}
wanted={("mass", k):v for k,v in masses.items()}
wanted.update({("frblock", k):v for k,v in fr.items()})
rows=pc.read_text().splitlines(keepends=True)
block=None; seen=set(); out=[]
for line in rows:
    a=re.match(r"^\s*BLOCK\s+(\S+)",line,re.I)
    if a: block=a.group(1).lower()
    elif re.match(r"^\s*DECAY\s+",line,re.I): block=None
    m=re.match(r"^(\s*)(\d+)(\s+)(\S+)(.*)$",line)
    if m and block and (block,int(m[2])) in wanted:
        key=(block,int(m[2]))
        line=f"{m[1]}{m[2]}{m[3]}{wanted[key]:.12e}{m[5]}"
        seen.add(key)
    out.append(line)
missing=set(wanted)-seen
if missing: sys.exit(f"ABORT: missing param card entries {sorted(missing)}")
pc.write_text("".join(out))
print("PARAM CARD:",sorted(seen))
updates={"ebeam1":"7000","ebeam2":"7000","nevents":"1200",
         "ickkw":"0","maxjetflavor":"4","pdlabel":"nn23lo1"}
rows=rc.read_text().splitlines(keepends=True)
out=[]; seen=set()
for line in rows:
    m=re.match(r"^(\s*)([^!=#]+?)(\s*=\s*)([A-Za-z_]\w*)(\b.*)$",line)
    if m and m[4].lower() in updates:
        key=m[4].lower()
        line=f"{m[1]}{updates[key]}{m[3]}{m[4]}{m[5]}"
        seen.add(key)
    out.append(line)
missing={"ebeam1","ebeam2","nevents","pdlabel"}-seen
if missing: sys.exit(f"ABORT: missing run card entries {sorted(missing)}")
rc.write_text("".join(out))
print("RUN CARD:",sorted(seen))
print("NOTE: initial internal PDF is exploratory; use consistent nf=4 PDF later.")
print("NOTE: 2HDM 'h+'/'h-' are one charged state and antiparticle, NOT Zee H1/H2.")
