#TODO:
# - upload form segmentations to derinet github

# - convert from xlsx
#   https://github.com/vidraj/derinet/tree/master/data/annotations/cs/2018_12_complete_morphseg_1000
#   https://github.com/vidraj/derinet/tree/master/data/annotations/cs/2019_12_morphrootsegm_3rd_round/hand-annotated
#   https://github.com/vidraj/derinet/tree/master/data/annotations/cs/2020_04_complete_morphseg/annotated
#   
#   koreny:
#   https://github.com/vidraj/derinet/tree/master/data/annotations/cs/2018-12-largest-tree-roots/hand-annotated
#   
# - download
#   https://raw.githubusercontent.com/vidraj/derinet/master/data/annotations/cs/2020_04_complete_morphseg/prepare/union-2100-segmented.tsv

DATADIR=../../data
IN_DIR=$(DATADIR)/original/DeriNet-annotations
OUT_DIR=$(DATADIR)/converted/ces-DeriNet-annotations

SHELL = bash


download:
	mkdir -p $(IN_DIR)
	
convert:
	mkdir -p $(OUT_DIR)
	