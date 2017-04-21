from otherwords import WordTokenizer, PhraseTokenizer, PhraseMap

from collections import defaultdict

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
					"ELMOR",
					"EILM2OPRSU",
					"DEIL2M2O3PR2SU",
					"DEI2L2M2O3PR2S2TU",
					"ADE2I2L2M3O3PR2S2T2U",
					], [
					"IMPSU",
					"DILMO2PRSU",
					"DI2LMO2PRS2TU",
					"ADEI2LM2O2PRS2T2U",
					], [
					"DLO2R",
					"DILO2RST",
					"ADEILMO2RST2",
					], [
					"AEIMST2",
					]]
	expected_idx = [0, 6, 12, 18]

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
	assert ti.called == 4

def test_from_file_indexing():
	filename = "test/lorem.txt"

	class testStore():
		def __init__(self):
			self.mapper = PhraseMap(min_len=20)
			self.store = defaultdict(list)

		def __call__(self, phr, idx):
			keys = self.mapper.map(phr)
			for key in keys:
				self.store[key].append((idx, filename,))

	store = testStore()

	phraseTokenizer = PhraseTokenizer(store, max_len=144)
	phraseTokenizer.tokenize_file(filename)
	assert store.store["ADE2I2L2M3O3PR2S2T2U"][0] == (0, filename,)

def test_sqlite_storage():
	from otherwords.store import SqliteStorage
	store = SqliteStorage('test.db', min_len=20)

	filename = "test/lorem.txt"
	store.reset(really=True)
	store.process_file(filename)
	results = store.find_by_canon("ADE2I2L2M3O3PR2S2T2U")
	assert results == [(0, filename), (329, filename)]
	results = store.find('Lorem ipsum dolor sit amet')
	assert results == [(0, filename), (329, filename)]
