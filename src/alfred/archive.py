"""The archive step of the memory protocol.

Saving a run only writes it to local disk. This module is what actually pushes
that memory to the *archive* — the git repository — so it survives beyond the
current (ephemeral) session, plus regenerates the human-readable STANDINGS.md.

`alfred archive` runs: regenerate STANDINGS.md -> git add runs/ + STANDINGS.md
-> commit -> push (with retry/backoff). It is safe to run when nothing changed.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from alfred import memory

STANDINGS_FILE = "STANDINGS.md"


class ArchiveError(RuntimeError):
    pass


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )


def _repo_root(start: Path) -> Path:
    res = _git(["rev-parse", "--show-toplevel"], start)
    if res.returncode != 0:
        raise ArchiveError("not inside a git repository — cannot archive memory")
    return Path(res.stdout.strip())


def _has_staged_changes(root: Path) -> bool:
    # Exit code 1 means there *are* staged differences.
    return _git(["diff", "--cached", "--quiet"], root).returncode != 0


def archive_memory(
    *,
    message: str | None = None,
    push: bool = True,
    cwd: Path | None = None,
    max_retries: int = 4,
) -> str:
    """Commit the run archive + standings and push to the remote.

    Returns a short status string. Raises ArchiveError on git failure.
    """
    cwd = Path(cwd or Path.cwd())
    root = _repo_root(cwd)
    runs_dir = root / "runs"

    # 1. Refresh the human-readable scoreboard.
    memory.write_standings(root / STANDINGS_FILE, directory=runs_dir)

    # 2. Stage memory locations: the raw run archive + the standings summary.
    _git(["add", "runs", STANDINGS_FILE], root)

    if not _has_staged_changes(root):
        return "Memory already archived — nothing new to push."

    # 3. Commit.
    n = len(memory.list_run_files(runs_dir))
    msg = message or f"Archive comedy memory: {n} run(s) on record"
    commit = _git(["commit", "-m", msg], root)
    if commit.returncode != 0:
        raise ArchiveError(f"git commit failed: {commit.stderr.strip()}")

    if not push:
        return f"Committed locally: {msg} (not pushed — use --push)."

    # 4. Push to the archive, with exponential backoff on transient failures.
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], root).stdout.strip()
    last_err = ""
    for attempt in range(max_retries):
        res = _git(["push", "-u", "origin", branch], root)
        if res.returncode == 0:
            return f"📦 Memory archived & pushed to origin/{branch}: {msg}"
        last_err = res.stderr.strip()
        if attempt < max_retries - 1:
            time.sleep(2 ** (attempt + 1))
    raise ArchiveError(f"git push failed after {max_retries} tries: {last_err}")
