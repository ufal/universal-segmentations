#TODO:
#   koreny:
#   https://github.com/vidraj/derinet/tree/master/data/annotations/cs/2018-12-largest-tree-roots/hand-annotated
#   https://github.com/vidraj/derinet/tree/master/data/annotations/cs/2019_12_morphrootsegm_3rd_round/hand-annotated

# - download
#   https://raw.githubusercontent.com/vidraj/derinet/master/data/annotations/cs/2020_04_complete_morphseg/prepare/union-2100-segmented.tsv

DATADIR=../../data
IN_DIR=$(DATADIR)/original/DeriNet-annotations
OUT_DIR=$(DATADIR)/converted/ces-DeriNet-annotations

SHELL = bash


download:
	mkdir -p $(IN_DIR)
	wget https://raw.githubusercontent.com/vidraj/derinet/master/data/annotations/cs/2020_04_complete_morphseg/prepare/union-2100-segmented.tsv -O $(IN_DIR)/morphemes_seg1.tsv
	wget https://raw.githubusercontent.com/vidraj/derinet/master/data/annotations/cs/2021_05_complete_morphseg_bandsampling/zatim_vyreseno.tsv  -O $(IN_DIR)/morphemes_seg2.tsv
	wget https://raw.githubusercontent.com/vidraj/derinet/master/data/annotations/cs/2021_11_complete_morphseg-forms_bandsampling/zatim_vyreseno.tsv -O $(IN_DIR)/forms_seg1.tsv
	
convert:
	mkdir -p $(OUT_DIR)
	python convertor.py lemmas1 $(IN_DIR)/morphemes_seg1.tsv $(OUT_DIR)/morphemes_seg1.useg
	python convertor.py lemmas2 $(IN_DIR)/morphemes_seg2.tsv $(OUT_DIR)/morphemes_seg2.useg
	python convertor.py forms1 $(IN_DIR)/forms_seg1.tsv $(OUT_DIR)/forms_seg1.useg