#!/bin/bash

# check the convention for directory names:  langcode-resourceabbrevname
# (langcodes according to ISO 639-3  )

ls -1 ../data/converted/ | grep -vE '^[a-z]{3}-.+$'
