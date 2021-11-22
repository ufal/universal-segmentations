.PHONY: download convert
.SECONDARY:

DATADIR=../../data
IN_DIR=$(DATADIR)/original/Uniparser
LANGS=udm kpv mdf tgk

PYTHONPATH=../../src
export PYTHONPATH

download: $(LANGS:%=$(IN_DIR)/%_wordlist_analyzed_fixed.txt) $(IN_DIR)/tgk_affixes.txt

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

$(IN_DIR)/mdf_wordlist_analyzed_fixed.txt: $(IN_DIR)/mdf_wordlist_analyzed.txt
	sed -e 's/<\(фт\|CAUS\)>/\&lt;\1\&gt;/g' < '$<' > '$@'

$(IN_DIR)/mdf_wordlist_analyzed.txt: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-moksha/raw/master/wordlists/wordlist_analyzed.txt'

$(IN_DIR)/tgk_wordlist_analyzed_fixed.txt: $(IN_DIR)/tgk_wordlist_analyzed.txt
	sed -e 's/ trans_en=""//g; s/>__*/>/; s/__*</</; s/\(trans_ru="[^"]*" \)trans_ru="[^"]*"/\1/g' < '$<' > '$@'

$(IN_DIR)/tgk_wordlist_analyzed.txt: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-tajik/raw/master/wordlists/wordlist_analyzed.txt'

$(IN_DIR)/%_affixes.txt: $(IN_DIR)/%_paradigms.txt
	grep ' gloss: ' '$<' |sed -e 's/ *gloss: *//' | sort -u > '$@'
	# The tgk paradigms miss these glosses for some reason (maybe
	#  they are in the constraint grammars?).
	printf 'ADJ0\nCONV\nDEMIN1\nDEMIN2\nDEMIN3\nDEMIN4\n' >> '$@'

$(IN_DIR)/tgk_paradigms.txt: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-tajik/raw/master/paradigms.txt'

$(IN_DIR):
	mkdir -p '$@'

$(DATADIR)/converted/%-Uniparser/:
	mkdir -p '$@'

convert: $(LANGS:%=$(DATADIR)/converted/%-Uniparser/all.useg)
# TODO Generate train / dev / test split.

$(DATADIR)/converted/%-Uniparser/all.useg: $(IN_DIR)/%_wordlist_analyzed_fixed.txt | $(DATADIR)/converted/%-Uniparser/
	./import_uniparser.py --annot-name 'Uniparser $*' < '$<' > '$@' 2> '$(basename $@).log'

$(DATADIR)/converted/udm-Uniparser/all.useg: $(IN_DIR)/udm_wordlist_analyzed_fixed.txt | $(DATADIR)/converted/udm-Uniparser/
	./import_uniparser.py --annot-name 'Uniparser udm' --multi-stem-infixation < '$<' > '$@' 2> '$(basename $@).log'

$(DATADIR)/converted/tgk-Uniparser/all.useg: $(IN_DIR)/tgk_wordlist_analyzed_fixed.txt $(IN_DIR)/tgk_affixes.txt | $(DATADIR)/converted/tgk-Uniparser/
	./import_uniparser.py --annot-name 'Uniparser tgk' --affixes $(IN_DIR)/tgk_affixes.txt < '$<' > '$@' 2> '$(basename $@).log'
