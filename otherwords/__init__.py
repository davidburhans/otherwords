from collections import OrderedDict

tokens = [chr(x) for x in range(ord('A'), ord('Z') + 1)]

def char_filter(letter):
	global tokens
	if letter.upper() in tokens:
		return letter
	return ''

class WordTokenizer():
	def __init__(self, fn, filt=None):
		self.on_word = fn
		self.filt = filt
		self.word = ''
		self.word_idx = 0

	def filter(self, letter):
		if self.filt:
			return filt(letter)
		return char_filter(letter)

	def emit(self):
		if self.on_word and len(self.word) > 0:
			self.on_word(self.word, self.word_idx)
		self.word = ''
		self.word_idx = -1

	def tokenize(self, letters):
		self.word = ''
		self.word_idx = -1
		idx = 0
		for letter in letters:
			if self.filter(letter) == '':
				self.emit()
			else:
				if self.word == '':
					self.word_idx = idx
				self.word += letter
			idx += 1
		self.emit()


class PhraseTokenizer():
	def __init__(self, on_phrase, max_len=0):
		self.on_phrase = on_phrase
		self.max = max_len
		self.phrase = []
		self.phrase_idx = []
		self.phrase_len = 0

	def emit(self):
		if self.on_phrase:
			self.on_phrase(self.phrase, self.phrase_idx[0])
		self.phrase_len = self.phrase_len - len(self.phrase[0])
		self.phrase = self.phrase[1:]
		self.phrase_idx = self.phrase_idx[1:]

	def on_word(self, word, idx):
		if len(self.phrase) == 0:
			self.phrase_len = 0
		new_len = self.phrase_len + len(word)
		if new_len > self.max and len(self.phrase) > 0:
			self.emit()
		self.phrase_idx.append(idx)
		self.phrase.append(word)
		self.phrase_len = new_len

	def tokenize(self, letters):
		self.phrase = []
		self.phrase_idx = []
		word_token = WordTokenizer(self.on_word)
		word_token.tokenize(letters)
		while(len(self.phrase) > 0):
			self.emit()

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
		return ''.join(['%s%d' % (k, v,) for k,v in counted.items() if k in tokens])
    	
	def map(self, phrase):
		cased = [''.join(phr.upper()) for phr in phrase]
		fanned = [''.join(cased[0:c+1]) for c in range(len(cased) - 1)] 
		filtered = [f for f in fanned if len(f) >= self.min]
		dicts = [self.buildCountedDict(sorted(phr)) for phr in filtered]
		canon = [self.countedDictToCanon(d) for d in dicts]
		return canon
