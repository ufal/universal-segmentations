#!/usr/bin/env python3

import sys
from useg import SegLex

def main():
    lexicon = SegLex()
    lexicon.load(sys.stdin)
    lexicon.save(sys.stdout)

if __name__ == "__main__":
    main()
