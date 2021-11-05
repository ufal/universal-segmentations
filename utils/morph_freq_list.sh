#!/bin/bash

# reads the useg formats, prints frequency list of morphs

cut -f4 | sed 's/ + /\n/g' | sort | uniq -c | sort -nr
