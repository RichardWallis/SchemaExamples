#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
for path in [os.getcwd()]:
  sys.path.insert( 1, path ) #Pickup libs from shipped lib directory

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

from schemaexamples import schemaExamples

schemaExamples.loadExamplesFile("example-code/examples.txt")
#schemaExamples.loadExamplesFile("test.txt")
#print(schemaExamples.examplesForTerm("Event"))


#filename = "out" + term.id +".html"
filename = "out"

exes = sorted(schemaExamples.allExamples(), key=lambda x: (x.exmeta['file'],x.exmeta['filepos']))
f = open(filename,"w")
for ex in exes:
    #print("%s  %s" % (ex.exmeta.get('file'),ex.exmeta.get('filepos')))
    f.write(ex.serialize())
    f.write("\n")
f.close()
#print(ex.serialize())