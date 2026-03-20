#!/usr/bin/env python3
"""Compatibility shim for the stage-agnostic AZQ Codex task runner."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def _load_runner():
    target = Path(__file__).resolve().parent / "azq_codex_task_runner.py"
    spec = spec_from_file_location("azq_codex_task_runner_impl", target)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load runner at {target}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_MODULE = _load_runner()

for _name in dir(_MODULE):
    if _name.startswith("_"):
        continue
    globals()[_name] = getattr(_MODULE, _name)


if __name__ == "__main__":
    raise SystemExit(_MODULE.main())
