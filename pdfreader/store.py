import json
import os
import sqlite3
from pathlib import Path


class Store:
    def __init__(self, directory: Path):
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        database = directory / "library.sqlite3"
        fd = os.open(database, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
        self.db = sqlite3.connect(database)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE NOT NULL,
                page INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY,
                document INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                page INTEGER NOT NULL,
                kind TEXT NOT NULL,
                geometry TEXT NOT NULL,
                quote TEXT NOT NULL,
                note TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS marks_document_page ON marks(document, page);
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                document INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                body TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS messages_document ON messages(document);
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

    def documents(self):
        return self.db.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()

    def import_paths(self, paths):
        ids = []
        with self.db:
            for path in paths:
                self.db.execute("INSERT OR IGNORE INTO documents(path) VALUES (?)", (path,))
                row = self.db.execute("SELECT id FROM documents WHERE path=?", (path,)).fetchone()
                ids.append(row["id"])
        return ids

    def document(self, document):
        return self.db.execute("SELECT * FROM documents WHERE id=?", (document,)).fetchone()

    def save_page(self, document, page):
        with self.db:
            self.db.execute("UPDATE documents SET page=? WHERE id=?", (page, document))

    def remove_document(self, document):
        with self.db:
            self.db.execute("DELETE FROM documents WHERE id=?", (document,))

    def marks(self, document, page=None):
        query = "SELECT * FROM marks WHERE document=?"
        args = (document,)
        if page is not None:
            query += " AND page=?"
            args += (page,)
        rows = self.db.execute(query + " ORDER BY page, id", args)
        return [dict(row) | {"geometry": json.loads(row["geometry"])} for row in rows]

    def add_mark(self, document, page, kind, geometry, quote="", note=""):
        with self.db:
            self.db.execute("""
                INSERT INTO marks(document,page,kind,geometry,quote,note)
                VALUES (?,?,?,?,?,?)
            """, (document, page, kind, json.dumps(geometry), quote, note))

    def edit_mark(self, mark, note):
        with self.db:
            self.db.execute("UPDATE marks SET note=? WHERE id=?", (note, mark))

    def delete_marks(self, document, marks):
        with self.db:
            self.db.executemany(
                "DELETE FROM marks WHERE document=? AND id=?",
                ((document, mark) for mark in marks),
            )

    def messages(self, document, limit=None):
        if limit is not None:
            rows = self.db.execute("""
                SELECT role, body FROM messages WHERE document=? ORDER BY id DESC LIMIT ?
            """, (document, limit)).fetchall()[::-1]
        else:
            rows = self.db.execute("""
                SELECT role, body FROM messages WHERE document=? ORDER BY id
            """, (document,)).fetchall()
        return [{"role": row["role"], "content": row["body"]} for row in rows]

    def save_exchange(self, document, question, answer):
        with self.db:
            self.db.executemany(
                "INSERT INTO messages(document,role,body) VALUES (?,?,?)",
                [(document, "user", question), (document, "assistant", answer)],
            )

    def clear_messages(self, document):
        with self.db:
            self.db.execute("DELETE FROM messages WHERE document=?", (document,))

    def get(self, key, default=""):
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def configure(self, **values):
        with self.db:
            self.db.executemany("""
                INSERT INTO settings(key,value) VALUES (?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, values.items())
