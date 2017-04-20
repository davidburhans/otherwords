from otherwords import WordTokenizer, PhraseTokenizer, PhraseMap

def test_word_tokenization():
	phrase = 'Lorem ipsum dolor sit amet'
	phrase_lst = phrase.split(' ')
	itr = phrase_lst.__iter__()

	def on_word(word, index):
		assert word == itr.__next__()
		if word == 'Lorem':
			assert index == 0

	wordTokenizer = WordTokenizer(on_word)
	wordTokenizer.tokenize(phrase)

def test_phrase_tokenization():
	phrase = 'Lorem ipsum dolor sit amet'
	phrase_lst = phrase.split(' ')

	expected = [phrase_lst, 	# Lorem
				phrase_lst[1:], # ipsum
				phrase_lst[2:], # dolor
				phrase_lst[3:], # sit
				phrase_lst[4:], # amet
				]
	expected_idx = [0, 	# Lorem
				6, # ipsum
				12, # dolor
				18, # sit
				22, # amet
				]
	expected_itr = expected.__iter__()
	idx_iter = iter(expected_idx)
	class testTokenizer():
		def __init__(self):
			self.called = 0

		def __call__(self, phr, index):
			self.called += 1
			ex_phr = expected_itr.__next__()
			ex_idx = idx_iter.__next__()
			assert phr == ex_phr
			assert index == ex_idx

	tt = testTokenizer()
	phraseTokenizer = PhraseTokenizer(tt, max_len=99)
	phraseTokenizer.tokenize(phrase)
	assert tt.called == len(expected)

def test_phrase_indexer():
	phrase = 'Lorem ipsum dolor sit amet'
	mapper = PhraseMap(min_len=5)

	expected_keys = [[
					"E1L1M1O1R1",
					"E1I1L1M2O1P1R1S1U1",
					"D1E1I1L2M2O3P1R2S1U1",
					"D1E1I2L2M2O3P1R2S2T1U1",
					], [
					"I1M1P1S1U1",
					"D1I1L1M1O2P1R1S1U1",
					"D1I2L1M1O2P1R1S2T1U1",
					], [
					"D1L1O2R1",
					"D1I1L1O2R1S1T1",
					]]
	expected_idx = [0, 6, 12]

	key_itr = iter(expected_keys)
	idx_itr = iter(expected_idx)

	class testIndexer():
		def __init__(self):
			self.called = 0
		def __call__(self, phr, phrase_idx):
			mapped = mapper.map(phr)
			if len(mapped) > 0:
				self.called += 1
				ex_key = next(key_itr)
				ex_idx = next(idx_itr)
				assert ex_key == mapped
				assert ex_idx == phrase_idx

	ti = testIndexer()
	phraseTokenizer = PhraseTokenizer(ti, max_len=99)
	phraseTokenizer.tokenize(phrase)
	assert ti.called == 3