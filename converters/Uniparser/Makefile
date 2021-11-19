.PHONY: download convert

DATADIR=../../data
IN_DIR=$(DATADIR)/original/Uniparser
OUT_DIR_udm=$(DATADIR)/converted/udm-Uniparser
OUT_DIR_kpv=$(DATADIR)/converted/kpv-Uniparser

PYTHONPATH=../../src
export PYTHONPATH

download: $(IN_DIR)/udm_wordlist_analyzed_fixed.txt $(IN_DIR)/kpv_wordlist_analyzed_fixed.txt

$(IN_DIR)/udm_wordlist_analyzed_fixed.txt: $(IN_DIR)/udm_wordlist_analyzed.txt
	# There are some spurious underscores in some word forms;
	#  get rid of them. Also, fix STEMSTEM -> STEM
	sed -e 's/__//; s/_</</; s/"STEMSTEM"/"STEM"/' < '$<' > '$@'

$(IN_DIR)/udm_wordlist_analyzed.txt: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-udm/raw/master/wordlists/wordlist_analyzed.txt'

$(IN_DIR)/kpv_wordlist_analyzed_fixed.txt: $(IN_DIR)/kpv_wordlist_analyzed.txt
	sed -e 's/<\(с\|ыс\|ӧд\|ысс\|сс\|CAUS\|PASS\)>/\&lt;\1\&gt;/g' < '$<' > '$@'

$(IN_DIR)/kpv_wordlist_analyzed.txt: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-komi-zyrian/raw/master/wordlists/wordlist_analyzed.txt'

$(IN_DIR):
	mkdir -p '$@'

$(OUT_DIR_udm):
	mkdir -p '$@'
$(OUT_DIR_kpv):
	mkdir -p '$@'

convert: $(OUT_DIR_udm)/all.useg $(OUT_DIR_kpv)/all.useg
# TODO Generate train / dev / test split.

$(OUT_DIR_udm)/all.useg: $(IN_DIR)/udm_wordlist_analyzed_fixed.txt | $(OUT_DIR_udm)
	./import_uniparser.py < '$<' 2>&1 > '$@' | tee '$(basename $@).log' >&2

$(OUT_DIR_kpv)/all.useg: $(IN_DIR)/kpv_wordlist_analyzed_fixed.txt | $(OUT_DIR_kpv)
	./import_uniparser.py < '$<' 2>&1 > '$@' | tee '$(basename $@).log' >&2
