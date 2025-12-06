from io import BytesIO
from typing import List
import csv
from io import StringIO


def build_project_csv(project, boards) -> BytesIO:
    """
    Build a CSV file for the given project and boards. Returns a BytesIO.
    """
    sio = StringIO()
    writer = csv.writer(sio)

    # Header
    writer.writerow(["Board", "Column", "Task Name", "Priority", "Due Date", "Description"])

    for board in boards:
        board_name = board.name or ""
        columns = getattr(board, "columns", []) or []
        if not columns:
            writer.writerow([board_name, "", "", "", "", ""])
            continue

        for col in columns:
            col_name = col.name or ""
            tasks = getattr(col, "tasks", []) or []
            if not tasks:
                writer.writerow([board_name, col_name, "", "", "", ""])
                continue

            for task in tasks:
                title = getattr(task, "title", "") or ""
                priority = getattr(task, "priority", "") or ""
                due = ""
                if getattr(task, "due_date", None):
                    try:
                        due = task.due_date.isoformat()
                    except Exception:
                        due = str(task.due_date)
                desc = getattr(task, "description", "") or ""
                writer.writerow([board_name, col_name, title, priority, due, desc])

    data = sio.getvalue()
    # Prepend UTF-8 BOM for Excel compatibility
    b = data.encode("utf-8")
    bom = b"\xef\xbb\xbf"
    return BytesIO(bom + b)
