from notion_client import Client
import os
notion = Client(auth=os.environ["NOTION_TOKEN"])    
main_page = "0274df83f4bd83c0a5f2814b848a34c6"
import json

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
    return json.dump(pro,indent=2)

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



    

def main():
    # print(get_callout_text("0274df83f4bd83c0a5f2814b848a34c6"))
    # send_text("0274df83f4bd83c0a5f2814b848a34c6", "rovin is gay")
    create_project("notion agent",description="A smart notion personal assistant ")

if __name__ == "__main__":
    main()
