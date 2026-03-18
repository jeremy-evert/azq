"""Canonical schema primitives for Agenda task records and DAG artifacts.

Task normalization lives here so later file-backed repository logic can rely on
one durable task-record shape without mixing schema concerns into task storage
code. DAG normalization also lives here as a distinct schema concern so graph
artifacts can stay separate from task records before they reach disk.
"""

import re
from typing import Any, Optional

TASK_ID_PATTERN = re.compile(r"^TASK_(\d+)$")
GRAPH_ID_SUFFIX = "_DAG"
TASK_INTENT_HEADING = "## Task Intent"
DESCRIPTION_HEADING = "## Description"
DEPENDENCIES_HEADING = "## Dependencies"
EXECUTION_NOTES_HEADING = "## Execution Notes"


def task_id_number(task_id: str) -> Optional[int]:
    """Extract the numeric suffix from a canonical TASK id."""
    match = TASK_ID_PATTERN.fullmatch(task_id)
    if match is None:
        return None
    return int(match.group(1))


def canonical_graph_id(goal_id: str) -> str:
    """Build the canonical graph id for one exact goal id."""
    normalized_goal_id = str(goal_id).strip()
    if not normalized_goal_id:
        return ""
    return f"GOAL_{normalized_goal_id}{GRAPH_ID_SUFFIX}"


def _normalize_task_dependencies(task_record: dict[str, Any]) -> list[Any]:
    """Normalize task dependency input into a stable list field."""
    dependencies = task_record.get("dependencies", task_record.get("depends_on"))
    if dependencies is None:
        return []
    if isinstance(dependencies, list):
        return list(dependencies)
    if isinstance(dependencies, tuple):
        return list(dependencies)
    return [dependencies]


def _normalize_task_intent(task_record: dict[str, Any]) -> dict[str, str]:
    """Normalize task intent input into a small stable metadata object.

    Fallbacks stay conservative so generated or noisy task inputs remain
    inspectable instead of silently growing speculative structure:
    - dict-shaped intent keeps only ``kind`` and ``summary``
    - string-like intent becomes an explicit summary
    - missing intent becomes an ``unspecified`` kind with an empty summary
    """

    raw_intent = task_record.get("task_intent", task_record.get("intent"))
    if isinstance(raw_intent, dict):
        kind = str(
            raw_intent.get("kind", raw_intent.get("type", "unspecified"))
        ).strip()
        summary = str(
            raw_intent.get(
                "summary",
                raw_intent.get(
                    "description",
                    raw_intent.get("title", raw_intent.get("intent", "")),
                ),
            )
        ).strip()
        return {
            "kind": kind or "unspecified",
            "summary": summary,
        }

    if raw_intent is None:
        raw_intent = task_record.get("intent_summary")

    if raw_intent is None:
        return {
            "kind": "unspecified",
            "summary": "",
        }

    return {
        "kind": "explicit",
        "summary": str(raw_intent).strip(),
    }


def normalize_task_record(task_record: dict[str, Any]) -> dict[str, Any]:
    """Convert partial task-shaped data into the canonical Agenda schema.

    Fallbacks stay conservative so stub tasks remain explicit:
    - ``deliverable_id`` accepts legacy-like parent aliases but defaults empty
    - ``title`` prefers an explicit title, then legacy ``task``, then the
      first non-empty line of ``description``
    - ``dependencies`` always becomes a list
    - ``status`` defaults to ``ready``
    - ``execution_notes`` and ``created`` become empty strings when missing
    - ``task_intent`` becomes a stable metadata object
    """

    description = str(task_record.get("description", "")).strip()
    title = str(task_record.get("title", task_record.get("task", ""))).strip()
    if not title and description:
        title = description.splitlines()[0].strip()

    return {
        "task_id": str(task_record.get("task_id", "")).strip(),
        "deliverable_id": str(
            task_record.get(
                "deliverable_id",
                task_record.get(
                    "parent_deliverable_id",
                    task_record.get("deliverable", ""),
                ),
            )
        ).strip(),
        "title": title,
        "status": str(task_record.get("status", "ready")).strip() or "ready",
        "task_intent": _normalize_task_intent(task_record),
        "description": description,
        "dependencies": _normalize_task_dependencies(task_record),
        "execution_notes": str(task_record.get("execution_notes", "")).strip(),
        "created": str(task_record.get("created", "")).strip(),
    }


def _normalize_string_list(value: Any) -> list[str]:
    """Normalize list-like schema input into a stable string list."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]

    normalized = str(value).strip()
    if not normalized:
        return []
    return [normalized]


def _normalize_dag_edge(edge: Any, index: int) -> dict[str, str]:
    """Normalize one dependency edge into the canonical edge schema."""
    if isinstance(edge, dict):
        from_task_id = str(
            edge.get(
                "from_task_id",
                edge.get("from", edge.get("source", edge.get("predecessor", ""))),
            )
        ).strip()
        to_task_id = str(
            edge.get(
                "to_task_id",
                edge.get("to", edge.get("target", edge.get("successor", ""))),
            )
        ).strip()
        edge_id = str(edge.get("edge_id", "")).strip()
    elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
        from_task_id = str(edge[0]).strip()
        to_task_id = str(edge[1]).strip()
        edge_id = ""
    else:
        from_task_id = str(edge).strip()
        to_task_id = ""
        edge_id = ""

    if not edge_id:
        if from_task_id or to_task_id:
            edge_id = f"{from_task_id}->{to_task_id}"
        else:
            edge_id = f"edge_{index:03d}"

    return {
        "edge_id": edge_id,
        "from_task_id": from_task_id,
        "to_task_id": to_task_id,
    }


def _normalize_dependency_edges(dag_record: dict[str, Any]) -> list[dict[str, str]]:
    """Normalize DAG edges into a readable, stable edge list."""
    raw_edges = dag_record.get(
        "dependency_edges",
        dag_record.get("edges", dag_record.get("dependencies")),
    )
    if raw_edges is None:
        return []
    if not isinstance(raw_edges, (list, tuple)):
        raw_edges = [raw_edges]

    return [_normalize_dag_edge(edge, index) for index, edge in enumerate(raw_edges, 1)]


def normalize_dag_record(dag_record: dict[str, Any]) -> dict[str, Any]:
    """Convert partial DAG-shaped data into the canonical Agenda DAG schema.

    DAG normalization stays separate from task-record normalization.
    The schema is intentionally sparse and inspectable:
    - ``graph_id`` is the stable graph-level identity
    - ``goal_id`` anchors the graph to its parent goal
    - ``dependency_edges`` always contains explicit edge objects
    - ``status`` defaults to ``draft``
    - ``created`` and ``notes`` become empty strings when missing
    """

    goal_id = str(
        dag_record.get("goal_id", dag_record.get("parent_goal_id", dag_record.get("goal", "")))
    ).strip()
    graph_id = str(
        dag_record.get("graph_id", dag_record.get("dag_id", dag_record.get("id", "")))
    ).strip()
    if not graph_id and goal_id:
        graph_id = canonical_graph_id(goal_id)

    return {
        "graph_id": graph_id,
        "goal_id": goal_id,
        "deliverable_ids": _normalize_string_list(
            dag_record.get(
                "deliverable_ids",
                dag_record.get("deliverables", dag_record.get("deliverable_id")),
            )
        ),
        "task_ids": _normalize_string_list(
            dag_record.get("task_ids", dag_record.get("tasks", dag_record.get("task_id")))
        ),
        "dependency_edges": _normalize_dependency_edges(dag_record),
        "status": str(dag_record.get("status", "draft")).strip() or "draft",
        "created": str(dag_record.get("created", "")).strip(),
        "notes": str(dag_record.get("notes", dag_record.get("description", ""))).strip(),
    }


# Public schema helpers re-exported by ``azq.agenda.storage``.
__all__ = [
    "TASK_ID_PATTERN",
    "GRAPH_ID_SUFFIX",
    "TASK_INTENT_HEADING",
    "DESCRIPTION_HEADING",
    "DEPENDENCIES_HEADING",
    "EXECUTION_NOTES_HEADING",
    "task_id_number",
    "canonical_graph_id",
    "normalize_task_record",
    "normalize_dag_record",
]
