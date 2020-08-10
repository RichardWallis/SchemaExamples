#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

from schemaexamples import schemaExamples

schemaExamples.loadExamplesFile("demo/examples.txt")
print(schemaExamples.examplesForTerm("Event"))

examps = schemaExamples.examplesForTerm("Event")
ex = examps[0]

print(ex.serialize())