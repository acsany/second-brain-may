# second-brain — CLI commands

```mermaid
flowchart TD
    CLI([second-brain]):::root

    CLI --> NEW["new TITLE [-c CONTENT]"]:::cmd
    CLI --> LIST[list]:::cmd
    CLI --> SHOW[show NUMBER]:::cmd

    NEW --> NEW_DESC[/"Create a new .md note<br/>(optionally with body)<br/>and echo its path"/]:::desc
    LIST --> LIST_DESC[/"List all notes<br/>newest first"/]:::desc
    SHOW --> SHOW_DESC[/"Print contents of<br/>note NUMBER to stdout"/]:::desc

    NEW_DESC --> DIR[("$SECOND_BRAIN_DIR<br/>default: ~/second_brain")]:::store
    LIST_DESC --> DIR
    SHOW_DESC --> DIR

    classDef root fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#f1f5f9
    classDef cmd fill:#0ea5e9,stroke:#0369a1,color:#0f172a
    classDef desc fill:#fef3c7,stroke:#b45309,color:#78350f
    classDef store fill:#dcfce7,stroke:#15803d,color:#14532d
```

## Examples

```bash
$ second-brain new "Idea: rewrite parser"
/Users/me/second_brain/2026-05-07-idea-rewrite-parser.md

$ second-brain new "Quick capture" -c "Body content here"
/Users/me/second_brain/2026-05-07-quick-capture.md

$ second-brain list
Notes: /Users/me/second_brain
1. 2026-05-07-idea-rewrite-parser.md
2. 2026-05-06-meeting-notes.md

$ second-brain show 1
# Idea: rewrite parser
...
```

Source: `src/second_brain/cli.py`
