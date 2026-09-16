# tinynotes (scratch target — orca-fleet #417)

A minimal CLI note keeper. **Scratch repo**: seeded with known findings for a
`clean-sweep → harden-it` mission-chaining exercise. Not production code.

## Usage

```sh
python3 notes.py add "title" "body"
python3 notes.py list
python3 notes.py export notes.json
```

## Claims under test

- Notes are stored in a local SQLite database (see `TINYNOTES_DB`).
- Exported JSON is encrypted at rest with AES-256. (SEED-6: doc-claim — false,
  export is plaintext JSON; clean-sweep `source=doc-claims` material.)
- Deleting a note always requires the admin token. (SEED-7: doc-claim — false
  when the caller passes no token; see `delete_note`.)
