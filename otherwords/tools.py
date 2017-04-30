from collections import OrderedDict
from otherwords.token import tokens

import os

class PhraseMap():
	def __init__(self, min_len=0):
		self.min = min_len

	def buildCountedDict(self, phrase):
	    ret = OrderedDict()
	    for p in phrase:
	      if p in ret:
	        ret[p] += 1
	      else:
	        ret[p] = 1
	    return ret
	    
	def countedDictToCanon(self, counted):
		global tokens
		canon = ''
		for k, v in counted.items():
			if k in tokens:
				if v > 1:
					canon += '%s%d' % (k, v,)
				else:
					canon += k
		return canon

	def canonize(self, phr):
		d = self.buildCountedDict(sorted(phr))
		return self.countedDictToCanon(d)

	def map(self, phrase):
		cased = [''.join(phr.upper()) for phr in phrase]
		fanned = [''.join(cased[0:c+1]) for c in range(len(cased))] 
		filtered = [f for f in fanned if len(f) >= self.min]
		canon = [self.canonize(f) for f in filtered]
		return canon


class DirectoryLoader():
	def __init__(self, store):
		self.store = store

	def load_directory(self, path, filter_fn=None):
		for (basepath, dirs, files) in os.walk(path):
			for f in files:
				fullpath = os.path.join(basepath, f)
				if filter_fn is None or filter_fn(fullpath):
					print("processing", f)
					self.store.process_file(fullpath)
