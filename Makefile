.PHONY: all lint profile clean
.SECONDARY:

all: udmurt/udmurt.useg

udm/udmurt.useg: udm/wordlist_analyzed_fixed.txt src/import_udmurt.py src/useg/seg_lex.py src/useg/seg_tsv.py
	./src/import_udmurt.py < '$<' 2>&1 > '$@' | tee '$(basename $@).log' >&2

udm/wordlist_analyzed_fixed.txt: udm/wordlist_analyzed.txt
	# There are some spurious underscores in some word forms;
	#  get rid of them. Also, fix STEMSTEM -> STEM
	sed -e 's/__//; s/_</</; s/"STEMSTEM"/"STEM"/' < '$<' > '$@'

udm/wordlist_analyzed.txt: | udm
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-udm/raw/master/wordlists/wordlist_analyzed.txt'

udm:
	mkdir -p '$@'

lint:
	pylint src/

profile: udm/wordlist_analyzed_fixed.txt src/import_udmurt.py src/useg/seg_lex.py src/useg/seg_tsv.py
# 	python3 -m scalene --cpu-only --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
	python3 -m cProfile --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
	snakeviz '$@'

clean:
	rm -f udm/wordlist_analyzed_fixed.txt
	rm -f udm/udmurt.useg udm/udmurt.log
	#rm -f udm/wordlist_analyzed.txt
