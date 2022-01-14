#!/usr/bin/env python3

import sys
from useg import SegLex

def main():
    lexicon = SegLex()
    f1=open(sys.argv[1],"r", encoding="utf-8")
    f2=open(sys.argv[2],"w", encoding="utf-8")
    lexicon.load(f1)
    lexicon.save(f2)
    f1.close()
    f2.close()

if __name__ == "__main__":
    main()
