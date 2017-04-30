# List of characters we care about when building/extracting anagrams
tokens = [chr(x) for x in range(ord('A'), ord('Z') + 1)]

def char_filter(letter):
	"""
	Converts letter to uppercase and checks in against `tokens`
	Returns the letter if it exists in `tokens` otherwise
	returns an empty string.
	"""
	global tokens
	if letter.upper() in tokens:
		return letter
	return ''

class WordTokenizer():
	"""
	Class that will tokenize text input based on a character filter
	"""
	def __init__(self, fn, filt=None):
		"""
		initializes the tokenizer with a function to be invoked per token `fn`
		and allows the passing of an optional character filter `filt`

		If defined, `filt` should be a function that accepts a character parameter
		and returns that character if it is a valid character for the tokenization
		"""
		self.on_word = fn
		self.filt = filt
		self.word = ''
		self.word_idx = 0

	def filter(self, letter):
		"""
		If `filt` was provide in construction, invokes it for the character,
		otherwise, invokes `char_filter`
		"""
		if self.filt:
			return filt(letter)
		return char_filter(letter)

	def emit(self):
		"""
		Executes user-defined callback function if we have a valid token
		"""
		if self.on_word and len(self.word) > 0:
			self.on_word(self.word, self.word_idx)
		self.word = ''
		self.word_idx = -1

	def _preTokenize(self):
		"""
		clear last token and prepare to process a new one
		"""
		self.word = ''
		self.word_idx = -1
		self.idx = 0		

	def _processChar(self, letter):
		"""
		puts a single character through the tokenization process
		"""
		if self.filter(letter) == '':
			self.emit()
		else:
			if self.word == '':
				self.word_idx = self.idx
			self.word += letter
		self.idx += 1

	def tokenize(self, letters):
		"""
		Tokenizes the string represented by `letters`
		"""
		self._preTokenize()
		for letter in letters:
			self._processChar(letter)
		self.emit()

	def tokenize_file(self, filename):
		"""
		tokenizes an entire file one character at a time
		"""
		self._preTokenize()
		with open(filename, "r", encoding="utf8") as f:
			letter = f.read(1)
			while letter:
				self._processChar(letter)
				letter = f.read(1)
		self.emit()


class PhraseTokenizer():
	"""
	Leverages `WordTokenizer` to tokenize a phrase of a maximum length
	"""
	def __init__(self, on_phrase, max_len=0):
		"""
		`on_phrase` will be invoked when a phrase reaches the given length
		`max_len` is the given length after which `on_phrase` is invoked
		"""
		self.on_phrase = on_phrase
		self.max = max_len
		self.phrase = []
		self.phrase_idx = []
		self.phrase_len = 0

	def emit(self):
		"""
		invokes user-defined function to process the current phrase
		pops the oldest word of the phrase from internal memory
		"""
		if self.on_phrase:
			self.on_phrase(self.phrase, self.phrase_idx[0])
		self.phrase_len = self.phrase_len - len(self.phrase[0])
		self.phrase = self.phrase[1:]
		self.phrase_idx = self.phrase_idx[1:]

	def on_word(self, word, idx):
		"""
		appends a word to the current phrase and emits if needed
		"""
		if len(self.phrase) == 0:
			self.phrase_len = 0
		new_len = self.phrase_len + len(word)
		if new_len > self.max and len(self.phrase) > 0:
			self.emit()
		self.phrase_idx.append(idx)
		self.phrase.append(word)
		self.phrase_len = new_len

	def _tokenize(self, letters, isfilename=False):
		self.phrase = []
		self.phrase_idx = []
		word_token = WordTokenizer(self.on_word)
		if isfilename:
			word_token.tokenize_file(letters)
		else:
			word_token.tokenize(letters)
		while(len(self.phrase) > 0):
			self.emit()

	def tokenize(self, letters):
		"""
		Tokenizes the string represented by `letters`
		"""
		self._tokenize(letters)

	def tokenize_file(self, filename):
		"""
		tokenizes an entire file one character at a time
		"""
		self._tokenize(filename, isfilename=True)