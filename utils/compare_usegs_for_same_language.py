#!/usr/bin/env python3

import sys

segmentations = [{}]  # unused zeroth item, to avoid zero label
allforms = {}

number_of_input_files = len(sys.argv)


for index in range(1,number_of_input_files):
    filename = sys.argv[index]
    print(f"#Input file {index}: {filename}")
    segmentations.append({})
    
    for line in open(filename):
        (form, lemma, pos, segm, rest) = line.split("\t")
        allforms[form] = 1
        segmentations[index][form] = segm


for form in sorted(allforms):

    segm_strings = []
    incompl = False
    prev = None
    same = True
    for index in range(1,number_of_input_files):
        if form in segmentations[index]:
            segm_strings.append(segmentations[index][form])
            if prev != None and prev != segmentations[index][form]:
                same = False
                
            prev = segmentations[index][form]    
        else:
            segm_strings.append("???")
            incompl = True

    columns = [form]
    if incompl:
        columns.append('INCOMPL')
    elif same:
        columns.append('SAME')
    else:
        columns.append('DIFF')

    columns.extend(segm_strings)

    print("\t".join(columns))
