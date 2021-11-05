DATADIR=../../data/
TMPDIR=./tmp
IN_DIR= $(DATADIR)/original/UniMorph/
OUT_DIR_COMMON = $(DATADIR)/converted

SHELL = bash

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

download:
	mkdir -p $(IN_DIR)
	mkdir  -p $(TMPDIR)
	cd $(TMPDIR) && wget https://unimorph.github.io/
	less tmp/index.html | perl -ne 'print "$$1\n" if /"(https:\/\/github.com\/unimorph\/...)"/' > tmp/git.urls

	cd $(IN_DIR) && for f in `cat $(mkfile_dir)/tmp/git.urls`; do  git clone $$f ; done


convert:
	for langcode in `ls $(IN_DIR)`; do \
	  echo Processing $$langcode ; \
	  mkdir -p $(OUT_DIR_COMMON)/$$langcode-UniMorph ; \
	  cat $(IN_DIR)/$$langcode/$$langcode | ./unimorph2useg.py > $(OUT_DIR_COMMON)/$$langcode-UniMorph/$$langcode.useg ;\
	  done
	mkdir -p tmp

test:
	cat ../../data/original/UniMorph/ces/ces ces | head -n 1000 | ./unimorph2useg.py > tmp/ces.useg
