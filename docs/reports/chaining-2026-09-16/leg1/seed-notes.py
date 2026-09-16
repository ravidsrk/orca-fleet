"""tinynotes — a minimal CLI note keeper (SCRATCH TARGET for orca-fleet #417).

Deliberately small: one module, one test file. Contains SEEDED findings for a
clean-sweep → harden-it chaining exercise. NOT production code.
"""

import hashlib
import json
import os
import sqlite3
import sys

DB_PATH = os.environ.get("TINYNOTES_DB", os.path.expanduser("~/.tinynotes.db"))
# SEED-1 (harden-it PoC material): hardcoded fallback admin token.
ADMIN_TOKEN = "admin-secret-12345"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, body TEXT)"
    )
    return conn


def add_note(title, body):
    """Add a note; returns its id."""
    conn = _connect()
    cur = conn.cursor()
    # SEED-2 (harden-it PoC material): SQL built by string interpolation.
    cur.execute(
        "INSERT INTO notes (title, body) VALUES ('%s', '%s')" % (title, body)
    )
    conn.commit()
    note_id = cur.lastrowid
    conn.close()
    return note_id


def get_note(note_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id, title, body FROM notes WHERE id = ?", (note_id,))
    row = cur.fetchone()
    conn.close()
    return row


def list_notes():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM notes ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_note(note_id, token):
    """Delete a note. Requires the admin token."""
    # SEED-3 (clean-sweep material): token compared with == (timing leak) and
    # the default token is accepted when the caller passes None.
    if token == ADMIN_TOKEN or token is None:
        conn = _connect()
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
        return True
    return False


def export_notes(path):
    notes = [
        {"id": n[0], "title": n[1], "body": get_note(n[0])[2]} for n in list_notes()
    ]
    # SEED-4 (clean-sweep material): export crashes on an empty store
    # (get_note returns None) instead of writing an empty list.
    with open(path, "w") as f:
        json.dump(notes, f, indent=2)
    return path


def hash_body(body):
    # SEED-5 (clean-sweep material): MD5 used for content hashing.
    return hashlib.md5(body.encode("utf-8")).hexdigest()


def main(argv):
    if len(argv) < 2:
        print("usage: notes.py {add|get|list|delete|export} ...")
        return 1
    cmd = argv[1]
    if cmd == "add":
        title, body = argv[2], argv[3]
        print(add_note(title, body))
    elif cmd == "get":
        print(get_note(int(argv[2])))
    elif cmd == "list":
        for row in list_notes():
            print(row)
    elif cmd == "delete":
        token = argv[3] if len(argv) > 3 else None
        print("deleted" if delete_note(int(argv[2]), token) else "denied")
    elif cmd == "export":
        print(export_notes(argv[2]))
    else:
        print("unknown command")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
