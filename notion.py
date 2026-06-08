from notion_client import Client
import os
notion = Client(auth=os.environ["NOTION_TOKEN"])

DATA_SOURCE_ID = "3794df83-f4bd-8031-ad83-000bf7c7880b"


def parse_tasks(response = notion.data_sources.query(data_source_id=DATA_SOURCE_ID)):
    tasks = []

    for page in response["results"]:
        props = page["properties"]

        title_items = props["Task Name "]["title"]

        task_name = (
            title_items[0]["plain_text"]
            if title_items else ""
        )

        status_obj = props["Status"]["select"]
        status = status_obj["name"] if status_obj else None

        date_obj = props["Due date"]["date"]
        due_date = date_obj["start"] if date_obj else None
        if status != "done":
            tasks.append({
                "id": page["id"],
                "task": task_name,
                "status": status,
                "due_date": due_date
            })

    return tasks

def get_task(task_id,response = notion.data_sources.query(data_source_id=DATA_SOURCE_ID)):
    tasks = parse_tasks(response)

    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

def update_task(task_id,status=None,due_date=None,task_name=None,meditations=None):
    properties = {}

    if status:
        properties["Status"] = {
            "select": {
                "name": status
            }
        }

    if due_date:
        properties["Due date"] = {
            "date": {
                "start": due_date
            }
        }

    if task_name:
        properties["Task Name "] = {
            "title": [
                {
                    "text": {
                        "content": task_name
                    }
                }
            ]
        }

    if meditations:
        properties["Meditations"] = {
            "rich_text": [
                {
                    "text": {
                        "content": meditations
                    }
                }
            ]
        }

    return notion.pages.update(
        page_id=task_id,
        properties=properties
    )

    return notion.pages.update(
        page_id=task_id,
        properties=properties
    )

def find_task_by_name(task_name):
    response = notion.data_sources.query(
        data_source_id=DATA_SOURCE_ID
    )
    rows = []

    for page in response["results"]:
        title = page["properties"]["Task Name "]["title"]

        if title and title[0]["plain_text"] == task_name:
            rows.append(page)

    return rows

def create_task(task_name,
                status="not started",
                due_date=None,
                meditations=None):

    properties = {
        "Task Name ": {
            "title": [
                {
                    "text": {
                        "content": task_name
                    }
                }
            ]
        },
        "Status": {
            "select": {
                "name": status
            }
        }
    }

    if due_date:
        properties["Due date"] = {
            "date": {
                "start": due_date
            }
        }
    if meditations:
        properties["Meditations"] = {
            "rich_text": [
                {
                    "text": {
                        "content": meditations
                    }
                }
            ]
        }
    return notion.pages.create(
        parent={
            "data_source_id": DATA_SOURCE_ID
        },
        properties=properties
    )



def delete_task(page_id):
    return notion.pages.update(
    page_id=page_id,
    archived=True)
    

def main():
    # update_task('3794df83-f4bd-8029-a24a-fe3bdcaa94bc',meditations='This is a test') 
    print(find_task_by_name("Task 1"))
if __name__ == "__main__":
    main()