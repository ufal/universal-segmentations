.PHONY: all clean
.SECONDARY:

all: udmurt/udmurt.useg

udmurt/udmurt.useg: udmurt/wordlist_analyzed.txt src/import_udmurt.py
	./src/import_udmurt.py < '$<' 2>&1 > '$@' | tee '$(basename $@).log' >&2

udmurt/wordlist_analyzed.txt: | udmurt
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-udm/raw/master/wordlists/wordlist_analyzed.txt'

udmurt:
	mkdir -p '$@'

clean:
	rm -f udmurt/udmurt.useg udmurt/udmurt.log
	#rm -f udmurt/wordlist_analyzed.txt
