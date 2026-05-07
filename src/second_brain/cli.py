"""CLI entry point using Click."""

from __future__ import annotations

import os
from pathlib import Path

import click
from loguru import logger

from second_brain.app import configure_logging
from second_brain.notes import create_note


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context):
    """second_brain -- capture and organise your thoughts.

    With no subcommand, launches the Textual TUI (sidebar of notes plus a
    markdown viewer/editor on the right).
    """
    configure_logging()
    if ctx.invoked_subcommand is None:
        from second_brain.tui import SecondBrainApp

        base_dir = Path(
            os.environ.get("SECOND_BRAIN_DIR", str(Path.home() / "second_brain"))
        ).expanduser()
        logger.debug("Launching TUI with notes_dir={}", base_dir)
        SecondBrainApp(notes_dir=base_dir).run()


def _decode_escapes(s: str) -> str:
    """Interpret ``\\n``, ``\\t``, ``\\r``, and ``\\\\`` escapes in ``s``.

    Lets users pass ``-c "line1\\nline2"`` from a normal double-quoted shell
    string and get a real newline, matching the UX implied by issue #3.
    Other backslash sequences are left untouched.
    """
    placeholder = "\x00"
    return (
        s.replace("\\\\", placeholder)
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\r", "\r")
        .replace(placeholder, "\\")
    )


@cli.command()
@click.argument("title")
@click.option(
    "--content",
    "-c",
    "content",
    default=None,
    help=(
        "Body content to write below the header. Backslash escapes "
        "(\\n, \\t, \\r, \\\\) are interpreted; real newlines are preserved."
    ),
)
def new(title: str, content: str | None):
    """Create a new note with the given TITLE.

    With no options, writes a stub containing the heading and an ISO
    timestamp. Pass --content/-c to also write a body below the header;
    \\n, \\t, \\r and \\\\ in the value are decoded into the corresponding
    characters, and real newlines are preserved verbatim.
    """
    base_dir = Path(
        os.environ.get("SECOND_BRAIN_DIR", str(Path.home() / "second_brain"))
    ).expanduser()
    logger.debug("Creating note in {}", base_dir)
    body = _decode_escapes(content) if content is not None else None
    path = create_note(title, base_dir, body=body)
    logger.info("Created note: {}", path)
    click.echo(path)


@cli.command("list")
def list_notes():
    """List all notes in the notes directory."""
    base_dir = Path(
        os.environ.get("SECOND_BRAIN_DIR", str(Path.home() / "second_brain"))
    ).expanduser()

    if not base_dir.is_dir():
        logger.warning("Notes directory does not exist: {}", base_dir)
        click.echo(f"Notes directory does not exist: {base_dir}")
        return

    files = sorted(base_dir.glob("*.md"), reverse=True)

    click.echo(f"Notes: {base_dir}")

    if not files:
        logger.info("No notes found in {}", base_dir)
        click.echo("No notes found.")
        return

    logger.debug("Found {} note(s) in {}", len(files), base_dir)
    for i, f in enumerate(files, 1):
        click.echo(f"{i}. {f.name}")


@cli.command()
@click.argument("number", type=int)
def show(number: int):
    """Display the contents of note NUMBER."""
    base_dir = Path(
        os.environ.get("SECOND_BRAIN_DIR", str(Path.home() / "second_brain"))
    ).expanduser()

    if not base_dir.is_dir():
        logger.error("Notes directory does not exist: {}", base_dir)
        click.echo(f"Error: Notes directory does not exist: {base_dir}", err=True)
        raise SystemExit(1)

    files = sorted(base_dir.glob("*.md"), reverse=True)

    if not files:
        logger.error("No notes found in {}", base_dir)
        click.echo("Error: No notes found.", err=True)
        raise SystemExit(1)

    if number < 1 or number > len(files):
        logger.error("Note {} out of range ({}  available)", number, len(files))
        click.echo(
            f"Error: Note {number} not found. Only {len(files)} notes available.",
            err=True,
        )
        raise SystemExit(1)

    logger.debug("Showing note {}: {}", number, files[number - 1].name)
    click.echo(files[number - 1].read_text())
