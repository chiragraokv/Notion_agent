from notion_client import Client
import os
import json
from datetime import datetime
from langchain.tools import tool
from typing import Literal

notion = Client(auth=os.environ["NOTION_TOKEN"])    


def get_callout_text(page_id):
    blocks = notion.blocks.children.list(block_id=page_id)
    texts = []
    for block in blocks["results"]:
        
        if block["type"] == "callout":
            for rt in block["callout"]["rich_text"]:
                texts.append(rt["plain_text"])

    return "".join(texts)

def send_text(page_id, message):
    blocks = notion.blocks.children.list(block_id=page_id)

    quote_id = None
    for block in blocks["results"]:
        
        if block["type"] == "quote":
            quote_id = block["id"]
            break

    if quote_id is None:
        return None

    return notion.blocks.update(
        block_id=quote_id,
        quote={
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": message
                    }
                }
            ]
        }
    )

@tool
def get_all_projects():
    "Used to get all Projects from NOTION"
    results = notion.search(
        query="Projects",
        filter={
            "value": "data_source",
            "property": "object"
        }
    )

    if not results["results"]:
        raise ValueError("Projects data source not found")

    data_source_id = results["results"][0]["id"]

    projects = notion.data_sources.query(
        data_source_id=data_source_id
    )["results"]
    pro = []
    for page in projects:
        name = page["properties"]["Name"]["title"][0]["plain_text"]
        description = "".join(item["plain_text"]for item in page["properties"]["Description"]["rich_text"])
        status = (page.get("properties", {}).get("Status", {}).get("status", {}).get("name"))
        progress = page.get("properties",{}).get("progress",{}).get("formula",{}).get("number")
        meta = (page.get("properties", {}).get("Meta", {}).get("formula", {}).get("string"))
        id  = page["id"]

        proj = {
            "name": name,
            "description": description,
            "status": status,
            "progress":progress,
            "workload": meta,
            "id": id
        }
        pro.append(proj)
    return json.dumps(pro,indent=2)

@tool
def create_project(name,emoji="🚀",description="",status="Planned"):
    "Create a new project for the user, use only if project not present"
    results = notion.search(
        query="Projects",
        filter={
            "value": "data_source",
            "property": "object"
        }
    )
    if not results["results"]:
        raise ValueError("Projects data source not found")

    data_source_id = results["results"][0]["id"]
    return notion.pages.create(
        parent={
            "type": "data_source_id",
            "data_source_id": data_source_id
        },
        icon={
            "type": "emoji",
            "emoji": emoji
        },
        properties={
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": description
                        }
                    }
                ]
            },
            "Status": {
                "status": {
                    "name": status
                }
            }
        }
    ) 

@tool   
def update_project(page_id:str,name:str|None = None,description:str|None=None,status: Literal["Not Started","In Progress","Completed"] | None = None,emoji:str|None=None):
    "Used to update exsisting projects, use correct page_id to access the project"
    properties = {}

    if name is not None:
        properties["Name"] = {
            "title": [
                {
                    "text": {
                        "content": name
                    }
                }
            ]
        }

    if description is not None:
        properties["Description"] = {
            "rich_text": [
                {
                    "text": {
                        "content": description
                    }
                }
            ]
        }

    if status is not None:
        properties["Status"] = {
            "status": {
                "name": status
            }
        }

    payload = {"page_id": page_id}

    if properties:
        payload["properties"] = properties

    if emoji is not None:
        payload["icon"] = {
            "type": "emoji",
            "emoji": emoji
        }

    notion.pages.update(**payload)

    return {
        "success": True,
        "page_id": page_id
    }

@tool
def get_project_task(project_id:str):
    "each project can have sub task, get information about same"
    page = notion.pages.retrieve(project_id)
    task_ids = [
    rel["id"]
    for rel in page["properties"]["Tasks"]["relation"]]
    list_task = []
    for t in task_ids:
        task = notion.pages.retrieve(t)
        properties = page.get("properties", {})
        title = properties.get("Name", {}).get("title", [])
        name = "".join(t.get("plain_text", "") for t in title)
        status = (properties.get("Status", {}).get("status", {}).get("name"))
        priority = (properties.get("Priority", {}).get("status", {}).get("name"))
        due_date = (properties.get("Due", {}).get("date", {}))
        due_date = due_date.get("start") if due_date else None
        list_task.append({"task_id": t,"name": name,"status": status,"priority": priority,"due_date": due_date,})
    return json.dumps(list_task,indent=2)


@tool
def update_task(task_page_id,name:str|None=None,status:Literal["done","not done"]|None=None,priority:str|None=None,due_date:str|None=None):
    "Update a exsisting task inside a project, use the tasks page id to access it"
    properties = {}
    if name is not None:
        properties["Name"] = {"title": [{"text": {"content": name}}]}
    if status is not None:
        properties["Status"] = {"status": {"name": status}}
    if priority is not None:
        properties["Priority"] = {"status": {"name": priority}}
    if due_date is not None:
        properties["Due"] = {"date": {"start": due_date}}
    return notion.pages.update(page_id=task_page_id,properties=properties)

@tool
def create_task_for_project(project_id:str,name,status="To Do",priority="Medium",due_date=None,emoji="📋"):
    "used to create a task under a project"
    project_page = notion.pages.retrieve(project_id)
    task_relations = project_page["properties"]["Tasks"]["relation"]
    if not task_relations:
        raise ValueError(
            "Project has no tasks. Cannot infer task database."
        )
    sample_task_id = task_relations[0]["id"]
    sample_task = notion.pages.retrieve(sample_task_id)
    database_id = sample_task["parent"]["database_id"]
    properties = {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": name
                    }
                }
            ]
        },
        "Status": {
            "status": {
                "name": status
            }
        },
        "Priority": {
            "status": {
                "name": priority
            }
        },
        "Project": {
            "relation": [
                {
                    "id": project_id
                }
            ]
        }
    }

    if due_date:
        properties["Due"] = {
            "date": {
                "start": due_date
            }
        }

    return notion.pages.create(
        parent={"database_id": database_id},
        icon={
            "type": "emoji",
            "emoji": emoji
        },
        properties=properties
    )

def paragraph(text):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
    }

def heading1(text):
    return {
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
    }

def heading2(text):
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
    }

def bullet(text):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
    }

def checkbox(text, checked=False):
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ],
            "checked": checked
        }
    }

def image(url):
    return {
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": url
            }
        }
    }
PAGE_BLOCK_FUNCTIONS = {
    "p": paragraph,
    "img": image,
    "h1": heading1,
    "h2": heading2,
    "todo": checkbox,
    "b": bullet
}

@tool
def add_blocks(page_id, llm_blocks):
    """
    Append blocks to a Notion page.

    Block types:
    p: paragraph
    h1: heading1
    h2: heading2
    b: bullet
    todo: checkbox
    img: image (URL)

    llm_blocks format:
    [
        {"type": "p", "value": "Example paragraph"},
        {"type": "h1", "value": "Title"},
        {"type": "todo", "value": "Buy milk"},
        {"type": "img", "value": "https://..."}
    ]
    """
    
    blocks = []

    for block in llm_blocks:
        block_type = block["type"]

        if block_type not in PAGE_BLOCK_FUNCTIONS:
            continue

        blocks.append(
            PAGE_BLOCK_FUNCTIONS[block_type](
                block["value"]
            )
        )

    return notion.blocks.children.append(
        block_id=page_id,
        children=blocks
    )

    

def main():

    # update_project("37c4df83-f4bd-8153-a266-e074a6adbbbc","this is a updated project")
    # update_task("37b4df83f4bd80e7aa2aefbe87fa047d","this is updated name")
    llm_block = [
    {"type": "h1", "value": "Results"},
    {"type": "p", "value": "Training complete"},
    {"type": "b", "value": "FID = 34"},
    {"type": "b", "value": "LPIPS = 0.12"},
    {"type": "img", "value": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6sGD7JTZnzScm52XzpJVzKAP1f1wJyXj5G6Brpj7-HQ&s=10"}
]
    add_blocks("37b4df83-f4bd-8073-b70b-d0c16c61ca10", llm_block)
if __name__ == "__main__":
    main()
