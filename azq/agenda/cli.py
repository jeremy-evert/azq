"""Agenda command routing for the top-level AZQ CLI."""


def dispatch(argv: list[str]) -> bool:
    """Handle Agenda commands and return True when one was dispatched."""
    if not argv or argv[0] != "agenda":
        return False

    if len(argv) < 2:
        print("Usage: azq agenda [build|list|show|dag]")
        return True

    sub = argv[1]

    if sub == "build":
        if len(argv) < 3:
            print("Usage: azq agenda build <deliverable_id>")
            return True

        from azq.agenda.build import build_agenda

        build_agenda(argv[2])
        return True

    if sub == "list":
        from azq.agenda.tasks import list_tasks

        list_tasks()
        return True

    if sub == "show":
        if len(argv) < 3:
            print("Usage: azq agenda show <task_id>")
            return True

        from azq.agenda.tasks import show_task

        show_task(argv[2])
        return True

    if sub == "dag":
        if len(argv) < 3:
            print("Usage: azq agenda dag <deliverable_id>")
            return True

        from azq.agenda.dags import agenda_dag

        agenda_dag(argv[2])
        return True

    print("Usage: azq agenda [build|list|show|dag]")
    return True
