#!/usr/bin/env python3
"""Strict static delimiter/string/comment balance check for F16 Wolfram scripts.

Not a Mathematica or physics validator. Its only purpose is to prevent an
unterminated script from reaching the user as a supposed SARAH physics run.
"""
from __future__ import annotations
import argparse
from pathlib import Path

OPEN={")":"(","]":"[","}":"{"}
DELIMITERS=set("()[]{}")

def check(text:str):
    stack=[]
    string=False
    escaped=False
    comments=0
    line=1
    i=0
    while i<len(text):
        ch=text[i]
        nxt=text[i+1] if i+1<len(text) else ""
        if ch=="\n":line+=1
        if comments:
            if ch=="(" and nxt=="*":
                comments+=1;i+=2;continue
            if ch=="*" and nxt==")":
                comments-=1;i+=2;continue
            i+=1;continue
        if string:
            if escaped:escaped=False
            elif ch=="\\":escaped=True
            elif ch=='"':string=False
            i+=1;continue
        if ch=="(" and nxt=="*":
            comments+=1;i+=2;continue
        if ch=='"':
            string=True;i+=1;continue
        if ch in DELIMITERS:
            if ch in "([{":
                stack.append((ch,line))
            else:
                if not stack or stack[-1][0]!=OPEN[ch]:
                    raise ValueError(
                        f"Wolfram delimiter mismatch at line {line}: "
                        f"unexpected {ch!r}, stack tail={stack[-3:]}")
                stack.pop()
        i+=1
    if comments:raise ValueError("Wolfram unterminated (*...*) comment")
    if string:raise ValueError("Wolfram unterminated string")
    if stack:raise ValueError(
        "Wolfram unclosed delimiters: "+str(stack[-10:]))
    return True

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files",nargs="+",type=Path)
    args=ap.parse_args()
    for path in args.files:
        check(path.read_text())
        print("F16_WOLFRAM_DELIMITER_BALANCE_PASS",path)

if __name__=="__main__":main()
