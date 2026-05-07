"""Textual TUI for the second-brain CLI."""

from __future__ import annotations

import os
from pathlib import Path

from loguru import logger
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Label, ListItem, ListView, Markdown, TextArea

from second_brain.notes import create_note


def _resolve_notes_dir() -> Path:
    return Path(
        os.environ.get("SECOND_BRAIN_DIR", str(Path.home() / "second_brain"))
    ).expanduser()


class SecondBrainApp(App):
    """Two-pane TUI: sidebar list + markdown viewer/editor."""

    CSS = """
    Screen {
        layout: horizontal;
    }
    #sidebar {
        width: 32;
        border-right: solid $accent;
    }
    #note-list {
        height: 1fr;
    }
    #create-btn {
        width: 100%;
        margin: 1 0 0 0;
    }
    #right {
        width: 1fr;
        padding: 1;
    }
    #viewer {
        height: 1fr;
    }
    #editor {
        height: 1fr;
    }
    #edit-actions {
        height: 3;
        margin-top: 1;
    }
    #save-btn, #cancel-btn {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "new_note", "New note"),
    ]

    mode: reactive[str] = reactive("view")

    def __init__(self, notes_dir: Path | None = None):
        super().__init__()
        self.notes_dir = (notes_dir or _resolve_notes_dir()).expanduser()
        self.current_note_path: Path | None = None
        self.current_note_text: str = ""

    def compose(self) -> ComposeResult:
        with Vertical(id="sidebar"):
            yield ListView(id="note-list")
            yield Button("Create", id="create-btn", variant="primary")
        with Vertical(id="right"):
            yield Markdown("", id="viewer")
            yield TextArea.code_editor("", language="markdown", id="editor")
            with Horizontal(id="edit-actions"):
                yield Button("Save", id="save-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_mount(self) -> None:
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self._apply_mode()
        self._refresh_note_list()

    # ------------------------------------------------------------------ helpers

    def _apply_mode(self) -> None:
        editing = self.mode == "edit"
        self.query_one("#editor").display = editing
        self.query_one("#save-btn").display = editing
        self.query_one("#cancel-btn").display = editing
        self.query_one("#viewer").display = not editing
        self.query_one("#create-btn").display = not editing

    def watch_mode(self, _old: str, _new: str) -> None:
        if self.is_mounted:
            self._apply_mode()

    @property
    def is_mounted(self) -> bool:
        try:
            self.query_one("#editor")
        except Exception:
            return False
        return True

    def _list_files(self) -> list[Path]:
        return sorted(self.notes_dir.glob("*.md"), reverse=True)

    def _refresh_note_list(self) -> None:
        list_view = self.query_one("#note-list", ListView)
        list_view.clear()
        for f in self._list_files():
            list_view.append(ListItem(Label(f.name), name=f.name))

    def _load_note(self, path: Path) -> None:
        self.current_note_path = path
        self.current_note_text = path.read_text(encoding="utf-8")
        self.query_one("#viewer", Markdown).update(self.current_note_text)

    # ------------------------------------------------------------------ events

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.item
        if item is None or item.name is None:
            return
        path = self.notes_dir / item.name
        if path.is_file():
            self._load_note(path)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if item is None or item.name is None:
            return
        path = self.notes_dir / item.name
        if path.is_file():
            self._load_note(path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "create-btn":
            self._enter_edit_mode()
        elif button_id == "save-btn":
            self._save_and_exit_edit()
        elif button_id == "cancel-btn":
            self._cancel_edit()

    def action_new_note(self) -> None:
        if self.mode == "view":
            self._enter_edit_mode()

    # ------------------------------------------------------------------ flow

    def _enter_edit_mode(self) -> None:
        editor = self.query_one("#editor", TextArea)
        editor.load_text("")
        self.mode = "edit"
        editor.focus()

    def _cancel_edit(self) -> None:
        self.query_one("#editor", TextArea).load_text("")
        self.mode = "view"

    def _save_and_exit_edit(self) -> None:
        editor = self.query_one("#editor", TextArea)
        body = editor.text
        title = _extract_title(body)
        # Body is everything after the first heading line if it matches; otherwise
        # treat the whole text as body.
        stripped_body = _strip_leading_title(body, title)
        path = create_note(title, self.notes_dir, body=stripped_body or None)
        logger.info("TUI saved note: {}", path)
        editor.load_text("")
        self.mode = "view"
        self._refresh_note_list()
        list_view = self.query_one("#note-list", ListView)
        if len(list_view.children):
            list_view.index = 0


def _extract_title(text: str) -> str:
    """Pull a title from the first non-empty line; fall back to ``untitled``."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or "untitled"
        return stripped
    return "untitled"


def _strip_leading_title(text: str, title: str) -> str:
    """Drop a leading ``# title`` line so ``create_note`` doesn't duplicate it."""
    lines = text.splitlines()
    out: list[str] = []
    skipped = False
    for line in lines:
        if not skipped:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.lstrip("#").strip() == title:
                skipped = True
                continue
            skipped = True
            out.append(line)
        else:
            out.append(line)
    return "\n".join(out).strip("\n")


def run(notes_dir: Path | None = None) -> None:
    """Launch the TUI."""
    SecondBrainApp(notes_dir=notes_dir).run()
