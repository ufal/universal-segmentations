.PHONY: all lint profile clean
.SECONDARY:

all: udmurt/udmurt.useg

udmurt/udmurt.useg: udmurt/wordlist_analyzed_fixed.txt src/import_udmurt.py src/useg/seg_lex.py src/useg/seg_tsv.py
	./src/import_udmurt.py < '$<' 2>&1 > '$@' | tee '$(basename $@).log' >&2

udmurt/wordlist_analyzed_fixed.txt: udmurt/wordlist_analyzed.txt
	# There are some spurious underscores in some word forms;
	#  get rid of them. Also, fix STEMSTEM -> STEM
	sed -e 's/__//; s/_</</; s/"STEMSTEM"/"STEM"/' < '$<' > '$@'

udmurt/wordlist_analyzed.txt: | udmurt
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-udm/raw/master/wordlists/wordlist_analyzed.txt'

udmurt:
	mkdir -p '$@'

lint:
	pylint src/

profile: udmurt/wordlist_analyzed_fixed.txt src/import_udmurt.py src/useg/seg_lex.py src/useg/seg_tsv.py
# 	python3 -m scalene --cpu-only --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
	python3 -m cProfile --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
	snakeviz '$@'

clean:
	rm -f udmurt/wordlist_analyzed_fixed.txt
	rm -f udmurt/udmurt.useg udmurt/udmurt.log
	#rm -f udmurt/wordlist_analyzed.txt
