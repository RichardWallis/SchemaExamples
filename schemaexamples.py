#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from __future__ import with_statement

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

import os
import os.path
import urllib
import glob
import re
import threading
import datetime, time

class schemaExamples():
    
    EXAMPLESMAP = {}
    EXAMPLES = {}    
    exlock = threading.RLock()
    
    
    @staticmethod
    def loadExamplesFile(exfile):
        return schemaExamples.loadExamplesFiles([exfile])
    

    @staticmethod
    def loadExamplesFiles(exfiles):
        parser = ExampleFileParser()
        for f in exfiles:
            for example in parser.parse(f):
                #log.info("Ex: %s %s" % (example.keyvalue,example.terms))
                keyvalue = example.keyvalue
                with schemaExamples.exlock:
                    if not schemaExamples.EXAMPLES.get(keyvalue,None):
                        schemaExamples.EXAMPLES[keyvalue] = example
                        
                    for term in example.terms:
                
                        if(not schemaExamples.EXAMPLESMAP.get(term, None)):
                            schemaExamples.EXAMPLESMAP[term] = []
                    
                        if not keyvalue in schemaExamples.EXAMPLESMAP.get(term):
                            schemaExamples.EXAMPLESMAP.get(term).append(keyvalue)
                
            
    @staticmethod
    def examplesForTerm(term):
        examples = []
        examps = schemaExamples.EXAMPLESMAP.get(term)
        if examps:
            for e in examps:
                ex = schemaExamples.EXAMPLES.get(e)
                if ex:
                    examples.append(ex)
        return examples

    @staticmethod
    def allExamples():
        return schemaExamples.EXAMPLES.values()
            
    
    @staticmethod
    def serializeExample(ex):
        buff = []
        buff.append("TYPES: %s %s" % (ex.keyvalue,ex.terms))
        buff.append("PRE-MARKUP: \n%s" % ex.getHtml)
        buff.append("MICRODATA: \n%s" % ex.getMicrodata)
        
        return buff.join("\n")
            
    
    
class Example ():
    
    ExamplesCount = 0
    
        

    def __init__ (self, terms, original_html, microdata, rdfa, jsonld, exmeta):
        """Example constructor, registers itself with the ExampleMap of terms to examples."""
        global EXAMPLES, EXAMPLESMAP, ExamplesCount
        self.terms = terms
        self.original_html = original_html
        self.microdata = microdata
        self.rdfa = rdfa
        self.jsonld = jsonld
        self.exmeta = exmeta
        self.keyvalue = self.exmeta.get('id',None)
        if not self.keyvalue:
            self.keyvalue = "%s-gen-%s"% (terms[0],Example.ExamplesCount)
            self.exmeta['id'] = self.keyvalue

    def get(self, name) :
        """Exposes original_content, microdata, rdfa and jsonld versions (in the layer(s) specified)."""
        if name == 'original_html':
           return self.original_html
        if name == 'microdata':
           return self.microdata
        if name == 'rdfa':
           return self.rdfa
        if name == 'jsonld':
           return self.jsonld
          
    def getHtml(self):
        return self.original_html
    def getMicrodata(self):
        return self.microdata
    def getRdfa(self):
        return self.rdfa
    def getJsonld(self):
        return self.jsonld
    
    def serialize(self):
        buff = []
        termnames = ""
        first = True
        id = self.keyvalue
        if "-gen-" in id:
            id = ""
        for t in self.terms:
            if first:
                first = False
            else:
                termnames += ", "
            termnames += t
            
        buff.append("TYPES: #%s %s" % (id,termnames))
        buff.append("PRE-MARKUP: \n%s" % self.getHtml())
        buff.append("MICRODATA: \n%s" % self.getMicrodata())
        buff.append("RDFA: \n%s" % self.getRdfa())
        buff.append("JSON: \n%s" % self.getJsonld())
        
        return "\n".join(buff)


class ExampleFileParser():

    def __init__ (self):
        logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
        self.file = ""
        self.filepos = 0
        self.initFields()

    def initFields(self):
        self.currentStr = []
        self.terms = []
        self.exmeta = {}
        self.preMarkupStr = ""
        self.microdataStr = ""
        self.rdfaStr = ""
        self.jsonStr = ""
        self.state= ""

    def nextPart(self, next):
        if (self.state == 'PRE-MARKUP:'):
            self.preMarkupStr = "".join(self.currentStr)
        elif (self.state ==  'MICRODATA:'):
            self.microdataStr = "".join(self.currentStr)
        elif (self.state == 'RDFA:'):
            self.rdfaStr = "".join(self.currentStr)
        elif (self.state == 'JSON:'):
            self.jsonStr = "".join(self.currentStr)
        self.state = next
        self.currentStr = []

    def process_example_id(self, m):
        self.exmeta["id"] = m.group(1)
        #logging.debug("Storing ID: %s" % self.exmeta["id"] )
        return ''

    def parse (self, file):
        import codecs
        self.file = file
        filepos = 0
        examples = []
        egid = re.compile("""#(\S+)\s+""")
        #logging.info("[%s] Reading file %s" % (api.getInstanceId(short=True),file))
        start = datetime.datetime.now()
        
        if file.startswith("file://"):
            file = file[7:]
        
        if "://" in file:
            content = urllib.urlopen(file).read().decode("utf8")
        else:
            fd = codecs.open(file, 'r', encoding="utf8")
            content = fd.read()
            fd.close()
        
        lines = re.split('\n|\r', content)
        first = True
        for line in lines:
            # Per-example sections begin with e.g.: 'TYPES: #music-2 Person, MusicComposition, Organization'
            line = line.rstrip()

            if line.startswith("TYPES:"):
                filepos += 1
                self.nextPart('TYPES:')
                #logging.debug("About to call api.Example.AddExample with terms: %s " % "".join( [" ; %s " % t.id for t in self.terms] ) )
                #Create example from what has been previously collected
                #If 1st call there will be no terms which will be regected and no xample created.
                if first:
                    first = False
                else:
                    examples.append(Example(self.terms, self.preMarkupStr, self.microdataStr, self.rdfaStr, self.jsonStr, self.exmeta))
                    self.initFields()
                self.exmeta['file'] = file
                self.exmeta['filepos'] = filepos
                typelist = re.split(':', line)
                #logging.debug("TYPE INFO: '%s' " % line );
                tdata = egid.sub(self.process_example_id, typelist[1]) # strips IDs, records them in exmeta["id"]
                ttl = tdata.split(',')
                for ttli in ttl:
                    ttli = re.sub(' ', '', ttli)
                    #logging.debug("TTLI: %s " % ttli); # danbri tmp
                    if len(ttli) and "@@" not in ttli:
                        self.terms.append(ttli)
            else:
                tokens = ["PRE-MARKUP:", "MICRODATA:", "RDFA:", "JSON:"]
                for tk in tokens:
                    ltk = len(tk)
                    if line.startswith(tk):
                        self.nextPart(tk)
                        line = line[ltk:]
                if (len(line) > 0):
                    self.currentStr.append(line + "\n")
        self.nextPart('TYPES:') # should flush on each block of examples
        filepos += 1
        examples.append(Example(self.terms, self.preMarkupStr, self.microdataStr, self.rdfaStr, self.jsonStr, self.exmeta)) # should flush last one
        #logging.info ("%s [%s] examples in %s" % (count,datetime.datetime.now() - start, file))
        return examples



