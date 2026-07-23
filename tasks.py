import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "task.json")

tasks = []


def save_tasks():
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=2)
        file.write("\n")


def load_tasks():
    global tasks

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            loaded_tasks = json.load(file)

        if isinstance(loaded_tasks, list):
            tasks[:] = loaded_tasks
        else:
            tasks.clear()
            save_tasks()

    except FileNotFoundError:
        tasks.clear()
        save_tasks()
    except json.JSONDecodeError:
        tasks.clear()
        save_tasks()

    return tasks


def add_task(user_task):
    user_task = user_task.strip()

    if not user_task:
        return False, "Task description cannot be empty."

    if any(task["task"].strip().lower() == user_task.lower() for task in tasks):
        return False, "This task is already added."

    task_id = 1 if not tasks else tasks[-1]["id"] + 1
    new_task = {"id": task_id, "task": user_task, "status": "pending"}
    tasks.append(new_task)
    save_tasks()

    return True, f"Task '{user_task}' added successfully."


STATUS_FLOW = ["pending", "in progress", "completed"]


def update_status(task_id):
    for task in tasks:
        if task["id"] == task_id:
            current = task.get("status", "pending").strip().lower()

            if current not in {status.lower() for status in STATUS_FLOW}:
                current = "pending"

            current_index = next(
                (
                    index
                    for index, status in enumerate(STATUS_FLOW)
                    if status.lower() == current
                ),
                0,
            )
            next_index = (current_index + 1) % len(STATUS_FLOW)
            task["status"] = STATUS_FLOW[next_index]
            save_tasks()
            return True, task["status"]

    return False, None


def delete_tasks(task_id):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            break

    save_tasks()


def delete_completed_task():
    pending_task = []

    for task in tasks:
        if task.get("status", "pending") != "completed":
            pending_task.append(task)

    tasks[:] = pending_task
    save_tasks()
    return True, "Completed tasks deleted successfully."


def delete_all_tasks():
    tasks.clear()
    save_tasks()


def get_active_tasks_count(tasks_database=None):
    if tasks_database is None:
        tasks_database = tasks
    active_statuses = {"pending", "in progress"}
    return sum(
        1 for task in tasks_database if task.get("status", "pending") in active_statuses
    )
