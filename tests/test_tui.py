"""Tests for the Textual TUI."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from second_brain.cli import cli
from second_brain.tui import SecondBrainApp


@pytest.fixture
def populated_dir(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    (tmp_note_dir / "2026-03-20-old.md").write_text("# Old\n\nold body\n")
    (tmp_note_dir / "2026-03-22-new.md").write_text("# New\n\nnew body\n")
    return tmp_note_dir


# ---------------------------------------------------------------------------
# Layout / boot
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tui_starts_in_view_mode(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    app = SecondBrainApp(notes_dir=tmp_note_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.mode == "view"
        assert app.query_one("#note-list").display
        assert app.query_one("#create-btn").display
        assert not app.query_one("#editor").display
        assert not app.query_one("#save-btn").display
        assert not app.query_one("#cancel-btn").display


@pytest.mark.asyncio
async def test_tui_lists_notes_newest_first(populated_dir):
    app = SecondBrainApp(notes_dir=populated_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        list_view = app.query_one("#note-list")
        names = [item.name for item in list_view.children]
        assert names[0] == "2026-03-22-new.md"
        assert names[1] == "2026-03-20-old.md"


@pytest.mark.asyncio
async def test_tui_empty_directory_shows_empty_list(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    app = SecondBrainApp(notes_dir=tmp_note_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        list_view = app.query_one("#note-list")
        assert len(list_view.children) == 0


@pytest.mark.asyncio
async def test_tui_missing_directory_creates_it(tmp_note_dir):
    assert not tmp_note_dir.exists()
    app = SecondBrainApp(notes_dir=tmp_note_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
    assert tmp_note_dir.is_dir()


# ---------------------------------------------------------------------------
# Selecting a note
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tui_selecting_note_shows_content(populated_dir):
    app = SecondBrainApp(notes_dir=populated_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        list_view = app.query_one("#note-list")
        list_view.index = 0
        await pilot.pause()
        assert app.current_note_path is not None
        assert app.current_note_path.name == "2026-03-22-new.md"
        assert "new body" in app.current_note_text


# ---------------------------------------------------------------------------
# Create button -> edit mode
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tui_create_button_switches_to_edit_mode(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    app = SecondBrainApp(notes_dir=tmp_note_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click("#create-btn")
        await pilot.pause()
        assert app.mode == "edit"
        assert app.query_one("#editor").display
        assert app.query_one("#save-btn").display
        assert app.query_one("#cancel-btn").display
        assert not app.query_one("#create-btn").display


@pytest.mark.asyncio
async def test_tui_save_writes_new_note(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    app = SecondBrainApp(notes_dir=tmp_note_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click("#create-btn")
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.load_text("# Brand new\n\nfresh body")
        await pilot.pause()
        await pilot.click("#save-btn")
        await pilot.pause()
        files = list(tmp_note_dir.glob("*.md"))
        assert len(files) == 1
        text = files[0].read_text()
        assert "# Brand new" in text
        assert "fresh body" in text
        assert app.mode == "view"


@pytest.mark.asyncio
async def test_tui_save_refreshes_list(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    app = SecondBrainApp(notes_dir=tmp_note_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(app.query_one("#note-list").children) == 0
        await pilot.click("#create-btn")
        await pilot.pause()
        app.query_one("#editor").load_text("# Brand new\n")
        await pilot.click("#save-btn")
        await pilot.pause()
        assert len(app.query_one("#note-list").children) == 1


@pytest.mark.asyncio
async def test_tui_cancel_returns_to_view_without_save(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    app = SecondBrainApp(notes_dir=tmp_note_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click("#create-btn")
        await pilot.pause()
        app.query_one("#editor").load_text("# Should not save\n")
        await pilot.click("#cancel-btn")
        await pilot.pause()
        assert app.mode == "view"
        assert list(tmp_note_dir.glob("*.md")) == []


@pytest.mark.asyncio
async def test_tui_save_with_empty_body_uses_untitled(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    app = SecondBrainApp(notes_dir=tmp_note_dir)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.click("#create-btn")
        await pilot.pause()
        await pilot.click("#save-btn")
        await pilot.pause()
        files = list(tmp_note_dir.glob("*.md"))
        assert len(files) == 1
        assert "untitled" in files[0].name


# ---------------------------------------------------------------------------
# CLI default invocation
# ---------------------------------------------------------------------------


def test_cli_no_args_launches_tui(monkeypatch, tmp_note_dir):
    """Invoking `second_brain` with no arguments launches the TUI."""
    called = {}

    def fake_run(self):
        called["ran"] = True
        called["notes_dir"] = self.notes_dir

    monkeypatch.setattr(SecondBrainApp, "run", fake_run)
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0, result.output
    assert called.get("ran") is True
    assert called["notes_dir"] == tmp_note_dir


def test_cli_subcommands_still_work(tmp_note_dir):
    """Existing subcommands (new) still work and don't launch the TUI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "Sanity check"])
    assert result.exit_code == 0
    assert tmp_note_dir.is_dir()
    assert len(list(tmp_note_dir.glob("*.md"))) == 1
