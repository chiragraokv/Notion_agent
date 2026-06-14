from notion_client import Client
import os
notion = Client(auth=os.environ["NOTION_TOKEN"])    
main_page = "0274df83f4bd83c0a5f2814b848a34c6"
import json
from datetime import datetime


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

def get_all_projects():
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

def create_project(name,emoji="🚀",description="",status="Planned"):
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

def get_project_task(project_id):
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
        list_task.append({"name": name,"status": status,"priority": priority,"due_date": due_date,})
    return json.dumps(list_task,indent=2)

def memory(date = None):
    #beta
    #this is to give temporal contex to ai
    results = notion.search(
        query="Cache",
        filter={
            "value": "data_source",
            "property": "object"
        }
    )
    data_source_id = results["results"][0]["id"]
    memory_db = notion.data_sources.query(
        data_source_id=data_source_id
    )["results"]
    memory_list = []
    cutoff = None
    if date:
        cutoff = datetime.fromisoformat(
            date.replace("Z", "+00:00")
        )
    for page in memory_db:
        notes = "".join(
        item["plain_text"]
        for item in page["properties"]["Notes"]["title"])
        last_edited = page.get("last_edited_time",{})
        if cutoff:
            edited_dt = datetime.fromisoformat(
                last_edited.replace("Z", "+00:00")
            )

            if edited_dt < cutoff:
                continue
        memory_list.append({last_edited:notes})
    return json.dumps(memory_list,indent=2)
        
def add_to_memory( note_text: str):
    results = notion.search(
        query="Cache",
        filter={
            "value": "data_source",
            "property": "object"
        }
    )
    data_source_id = results["results"][0]["id"]
    return notion.pages.create(
        parent={"data_source_id": data_source_id},
        properties={
            "Notes": {
                "title": [
                    {
                        "text": {
                            "content": note_text
                        }
                    }
                ]
            }
        }
    )



def create_task_for_project(project_id,name,status="To Do",priority="Medium",due_date=None,emoji="📋"):
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

def analyze():
    #beta 
    #this is a boolean function that the llm can use to continue processing 
    #the idea is to let the llm build context and explore database
    #this should reduce the amount of data exposed to llm in long term
    return True

    

def main():
    # print(get_callout_text("0274df83f4bd83c0a5f2814b848a34c6"))
    # send_text("0274df83f4bd83c0a5f2814b848a34c6", "rovin is gay")
    # create_project("notion agent",description="A smart notion personal assistant ")
    # add_to_memory("this is a test")
    print(get_project_task("37c4df83-f4bd-8153-a266-e074a6adbbbc"))
    create_task_for_project("37c4df83-f4bd-8153-a266-e074a6adbbbc","testing create")
if __name__ == "__main__":
    main()
