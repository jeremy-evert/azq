#!/usr/bin/env python3
"""Compatibility shim for the stage-agnostic AZQ Codex task runner."""

from azq_codex_task_runner import *  # noqa: F401,F403
from azq_codex_task_runner import main


if __name__ == "__main__":
    raise SystemExit(main())
