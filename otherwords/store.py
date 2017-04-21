import sqlite3
from otherwords import PhraseMap, PhraseTokenizer

class SqliteStorage():
	def __init__(self, db_name, min_len=40):
		self.db_name = db_name
		self.mapper = PhraseMap(min_len=min_len)
		self.init_tables()

	def init_tables(self):
		self.db_con = sqlite3.connect(self.db_name)
		cur = self.db_con.cursor()
		cur.execute("create table if not exists read_files (filepath text not null);")
		cur.execute("create table if not exists anagrams (canon text not null, offset integer not null, read_file_rowid integer not null);")
		self.db_con.commit()
		self.file_id = -1

	def __call__(self, keys, idx):
		mapped = self.mapper.map(keys)
		cur = self.db_con.cursor()
		for m in mapped:
			cur.execute("insert into anagrams (canon, offset, read_file_rowid) values (?, ?, ?);", (m, idx, self.file_id,))
		self.db_con.commit()

	def process_file(self, filepath):
		self.filepath = filepath
		query_args = (self.filepath,)
		cur = self.db_con.cursor()
		cur.execute("select rowid from read_files where filepath = ?;", query_args)
		result = cur.fetchone()
		if result is None:
			cur.execute("insert into read_files (filepath) values (?);", query_args)
			cur.execute("select rowid from read_files where filepath = ?;", query_args)
			result = cur.fetchone()
			self.file_id = result[0]
			self.db_con.commit()
			phraseTokenizer = PhraseTokenizer(self, max_len=144)
			phraseTokenizer.tokenize_file(filepath)

	def find_by_canon(self, canon):
		cur = self.db_con.cursor()
		cur.execute("select offset, filepath from anagrams inner join read_files on anagrams.read_file_rowid = read_files.rowid where anagrams.canon = ?", (canon,))
		results = cur.fetchall()
		return results

	def find(self, phr):
		canon = self.mapper.canonize(phr.upper())
		return self.find_by_canon(canon)

	def reset(self, really=False):
		cur = self.db_con.cursor()
		cur.execute('drop table read_files;')
		cur.execute('drop table anagrams;')
		self.db_con.commit()
		self.init_tables()

