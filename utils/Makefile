
SHELL=bash

resourcesperlang:
	ls ../data/converted/* -1 -d | rev | cut -f1 -d '/' | rev | cut -f1 -d '-' | sort | uniq -c | sort -nr

compareall:
	mkdir -p ../data/extracted/segm_comparison
	for langcode in `ls ../data/converted/* -1 -d | rev | cut -f1 -d '/' | rev | cut -f1 -d '-' | uniq`; do \
	  if [ `ls ../data/converted/$${langcode}-*/*useg 2>/dev/null | wc -l` -gt 1 ];\
	  then \
	    echo Multiple resources for $$langcode; \
	    ./compare_usegs_for_same_language.py ../data/converted/$${langcode}-*/*useg > ../data/extracted/segm_comparison/$${langcode}-comparison.tsv ;\
	  fi;\
	done


