.PHONY: download convert

DATADIR=../../data
IN_DIR=$(DATADIR)/original/Uniparser
OUT_DIR_udm=$(DATADIR)/converted/udm-Uniparser

PYTHONPATH=../../src
export PYTHONPATH

download: $(IN_DIR)/udm_wordlist_analyzed_fixed.txt

$(IN_DIR)/udm_wordlist_analyzed_fixed.txt: $(IN_DIR)/udm_wordlist_analyzed.txt
	# There are some spurious underscores in some word forms;
	#  get rid of them. Also, fix STEMSTEM -> STEM
	sed -e 's/__//; s/_</</; s/"STEMSTEM"/"STEM"/' < '$<' > '$@'

$(IN_DIR)/udm_wordlist_analyzed.txt: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-udm/raw/master/wordlists/wordlist_analyzed.txt'

$(IN_DIR):
	mkdir -p '$@'

$(OUT_DIR_udm):
	mkdir -p '$@'

convert: $(OUT_DIR_udm)/all.useg
# TODO Generate train / dev / test split.

$(OUT_DIR_udm)/all.useg: $(IN_DIR)/udm_wordlist_analyzed_fixed.txt | $(OUT_DIR_udm)
	./import_udmurt.py < '$<' 2>&1 > '$@' | tee '$(basename $@).log' >&2
