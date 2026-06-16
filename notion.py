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

def image(url, caption=""):
    return {
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": url
            },
            "caption": [
                {
                    "type": "text",
                    "text": {"content": caption}
                }
            ]
        }
    }