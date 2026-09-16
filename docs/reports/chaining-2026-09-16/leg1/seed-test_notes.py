"""Baseline tests for tinynotes. Green at baseline (ship-it/harden-it preflight needs that)."""

import json
import os
import tempfile

import notes


def _isolated_db(tmp_path, monkeypatch):
    db = str(tmp_path / "test.db")
    monkeypatch.setattr(notes, "DB_PATH", db)
    return db


def test_add_and_get_roundtrip(tmp_path, monkeypatch):
    _isolated_db(tmp_path, monkeypatch)
    nid = notes.add_note("hello", "world")
    row = notes.get_note(nid)
    assert row[1] == "hello" and row[2] == "world"


def test_list_orders_by_id(tmp_path, monkeypatch):
    _isolated_db(tmp_path, monkeypatch)
    a = notes.add_note("a", "1")
    b = notes.add_note("b", "2")
    ids = [r[0] for r in notes.list_notes()]
    assert ids == sorted(ids) and set(ids) == {a, b}


def test_delete_requires_token(tmp_path, monkeypatch):
    _isolated_db(tmp_path, monkeypatch)
    nid = notes.add_note("x", "y")
    assert notes.delete_note(nid, "wrong-token") is False
    assert notes.get_note(nid) is not None


def test_export_writes_json_list(tmp_path, monkeypatch):
    _isolated_db(tmp_path, monkeypatch)
    notes.add_note("t", "b")
    out = str(tmp_path / "out.json")
    notes.export_notes(out)
    with open(out) as f:
        data = json.load(f)
    assert isinstance(data, list) and len(data) == 1
