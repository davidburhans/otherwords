import os
import sqlite3
from otherwords.token import PhraseTokenizer
from otherwords.tools import PhraseMap

class SqliteStorage():
	"""
	Used to store anagrams found by tokenizers into an Sqlite3 database.
	"""
	CREATE_FILE_TABLE = "create table if not exists read_files (filepath text not null);"
	CREATE_ANAGRAM_TABLE = "create table if not exists anagrams (canon text not null, offset integer not null, read_file_rowid integer not null);"
	INSERT_ANAGRAM = "insert into anagrams (canon, offset, read_file_rowid) values (?, ?, ?);"
	LIST_FILES = "select filepath from read_files;"
	CHECK_FOR_FILE = "select rowid from read_files where filepath = ?;"
	INSERT_FILE = "insert into read_files (filepath) values (?);"
	QUERY = "select offset, filepath from anagrams inner join read_files on anagrams.read_file_rowid = read_files.rowid where anagrams.canon = ?"
	DROP_FILE_TABLE = "drop table read_files;"
	DROP_ANAGRAM_TABLE = "drop table anagrams;"

	def __init__(self, db_name, min_len=40):
		"""
		Create sql database in file `db_name`
		"""
		self.db_name = db_name
		self.mapper = PhraseMap(min_len=min_len)
		self.init_tables()

	def init_tables(self):
		"""
		Initialize database tables for database. This will create tables if they
		do not exist and do nothing if they do.
		"""
		self.db_con = sqlite3.connect(self.db_name)
		self.db_con.isolation_level = "DEFERRED"
		cur = self.db_con.cursor()
		cur.execute("PRAGMA count_changes=OFF")
		cur.execute("PRAGMA synchronous = OFF")
		cur.execute("PRAGMA journal_mode = MEMORY")
		cur.execute(self.CREATE_FILE_TABLE)
		cur.execute(self.CREATE_ANAGRAM_TABLE)
		self.db_con.commit()
		self.file_id = -1

	def __call__(self, keys, idx):
		"""
		invoked by the tokenization process
		"""
		mapped = self.mapper.map(keys)
		cur = self.db_con.cursor()
		params = [(m, idx, self.file_id) for m in mapped]
		cur.executemany(self.INSERT_ANAGRAM, params)

	def list_processed_files(self):
		"""
		Returns a list of all files that the database has processed
		"""
		cur = self.db_con.cursor()
		cur.execute(self.LIST_FILES)
		return cur.fetchall()

	def has_processed_file(self, filepath):
		"""
		returns True if the file at `filepath` has been processed
		"""
		query_args = (os.path.basename(filepath),)
		cur = self.db_con.cursor()
		cur.execute(self.CHECK_FOR_FILE, query_args)
		result = cur.fetchone()
		return result is not None

	def process_file(self, filepath):
		"""
		Processes the file at `filepath` if not previously processed
		"""
		if not self.has_processed_file(filepath):
			query_args = (os.path.basename(filepath),)
			cur = self.db_con.cursor()
			cur.execute(self.INSERT_FILE, query_args)
			cur.execute(self.CHECK_FOR_FILE, query_args)
			result = cur.fetchone()
			self.file_id = result[0]
			self.db_con.commit()
			cur.execute("BEGIN TRANSACTION")
			phraseTokenizer = PhraseTokenizer(self, max_len=144)
			phraseTokenizer.tokenize_file(filepath)
			cur.execute("END TRANSACTION")
			self.db_con.commit()

	def find_by_canon(self, canon):
		"""
		Searches the database for an anagram based on the
		canonical representation of the anagrams
		"""
		cur = self.db_con.cursor()
		cur.execute(self.QUERY, (canon,))
		results = cur.fetchall()
		return results

	def find(self, phr):
		"""
		Searches the database for an anagrams which has the
		same canonical form as `phr`. This function will canonize
		the `phr` input before executing the search
		"""
		canon = self.mapper.canonize(phr.upper())
		return self.find_by_canon(canon)

	def reset(self, really=False):
		"""
		Removes all data from the database.
		`really` must be True for data to be destroyed
		"""
		cur = self.db_con.cursor()
		cur.execute(self.DROP_FILE_TABLE)
		cur.execute(self.DROP_ANAGRAM_TABLE)
		self.db_con.commit()
		self.init_tables()

