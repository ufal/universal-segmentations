SHELL=bash

resourcesperlang:
	ls ../data/converted/* -1 -d | rev | cut -f1 -d '/' | rev | cut -f1 -d '-' | sort | uniq -c | sort -nr

compareall:
	for langcode in `ls ../data/converted/* -1 -d | rev | cut -f1 -d '/' | rev | cut -f1 -d '-'`; do \
	  if [ `ls ../data/converted/$${langcode}-*/*useg 2>/dev/null | wc -l` -gt 1 ];\
	  then \
	    echo Multiple resources for $$langcode; \
	    ls ../data/converted/$${langcode}-*/*useg ;\
	  fi;\
	done


