# TUI

Running `second_brain` with no arguments launches a Textual-based TUI — a
two-pane interface for browsing and capturing notes.

```bash
uv run second_brain
```

## Layout

```text
┌─────────────────┬───────────────────────────────────────────┐
│ note list       │                                           │
│ (newest first)  │   markdown viewer (read-only)             │
│  • 2026-05-07-… │   ── or ──                                │
│  • 2026-05-06-… │   markdown editor (when creating a note)  │
│  …              │                                           │
│                 │                                           │
│ [ Create ]      │   [ Save ] [ Cancel ]   (edit mode only)  │
└─────────────────┴───────────────────────────────────────────┘
```

- **Left sidebar** — scrollable `ListView` populated from the notes directory
  (`SECOND_BRAIN_DIR`, default `~/second_brain/`), sorted newest first. A
  `Create` button sits at the bottom.
- **Right pane** — toggles between a `Markdown` viewer (when browsing) and a
  `TextArea` editor with `Save` / `Cancel` buttons (when creating).

## Modes

The app has two modes, exposed as the reactive attribute `mode` on
`SecondBrainApp`:

| Mode   | Right-pane shows  | Visible buttons       |
|--------|-------------------|-----------------------|
| `view` | `Markdown` viewer | `Create`              |
| `edit` | `TextArea` editor | `Save`, `Cancel`      |

## Keyboard shortcuts

| Key | Action            |
|-----|-------------------|
| `n` | New note (edit)   |
| `q` | Quit              |
| `↑` / `↓` | Move highlight in the note list |
| `Enter`   | Select highlighted note          |

## How saving works

When you press **Save** in edit mode:

1. The first non-empty line of the editor becomes the title. Leading `#`s are
   stripped, so `# My idea`, `## My idea` and `My idea` all yield the title
   `My idea`. If the editor is empty the title falls back to `untitled`.
2. The remaining text becomes the body, written verbatim below the auto-
   generated `# title` heading and ISO timestamp produced by
   [`create_note`][second_brain.notes.create_note].
3. If a file with the same name exists for today, a numeric suffix
   (`-1`, `-2`, …) is appended to avoid overwriting.
4. The sidebar is refreshed and the new note becomes the highlighted entry.

**Cancel** discards the editor contents without writing anything.

## Configuration

The TUI honours `SECOND_BRAIN_DIR`, `LOG_LEVEL`, and `LOG_FILE` exactly like
the rest of the CLI — see [Usage](usage.md#environment-variables).

If the notes directory does not yet exist when the app starts, the TUI
creates it.
