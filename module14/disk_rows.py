"""Temporary SQLite row storage; bounded cache, stable iteration and JSON hashing."""
import hashlib
import json
import sqlite3
import tempfile

from module14.scan import encode


class DiskRows(list):
    """List-compatible JSON iterable backed by disk; close after consumption.

    JSON must use iterencode(_one_shot=False): the C encoder bypasses list
    subclass iteration. No Python list of all records is constructed.
    """
    def __init__(self):
        self.directory = tempfile.TemporaryDirectory(prefix='d14-rows-')
        self.db = sqlite3.connect(self.directory.name+'/rows.sqlite')
        self.db.execute('PRAGMA cache_size=-2048')
        self.db.execute('PRAGMA temp_store=FILE')
        self.db.execute('CREATE TABLE rows(seq INTEGER PRIMARY KEY, id INTEGER, ordering TEXT, family INTEGER, data TEXT)')
        self.db.execute('CREATE INDEX identity_sort ON rows(id, ordering, family)')
        self.count = 0

    def append(self, row):
        n = row.get('neutrino')
        ordering = row.get('ordering') if 'ordering' in row else n.get('ordering') if isinstance(n, dict) else None
        family = row.get('family') if 'family' in row else n.get('family') if isinstance(n, dict) else None
        self.db.execute('INSERT INTO rows VALUES(?,?,?,?,?)', (self.count,row['id'],ordering,family,encode(row)))
        self.count += 1

    def __len__(self):
        return self.count

    def __iter__(self):
        for data, in self.db.execute('SELECT data FROM rows ORDER BY seq'):
            yield json.loads(data)

    def sorted(self):
        for data, in self.db.execute('SELECT data FROM rows ORDER BY id, ordering, family'):
            yield json.loads(data)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError('DiskRows supports integer indexing only')
        if index < 0:
            index += self.count
        record = self.db.execute('SELECT data FROM rows WHERE seq=?',(index,)).fetchone()
        if record is None:
            raise IndexError(index)
        return json.loads(record[0])

    def close(self):
        if getattr(self, 'db', None) is not None:
            self.db.close()
            self.db = None
        self.directory.cleanup()

    def __del__(self):
        if hasattr(self, 'directory'):
            self.close()


def json_chunks(value):
    return json.JSONEncoder(sort_keys=True, separators=(',', ':'), allow_nan=False).iterencode(value)


def streaming_digest(value):
    h = hashlib.sha256()
    for chunk in json_chunks(value):
        h.update(chunk.encode())
    return h.hexdigest()
