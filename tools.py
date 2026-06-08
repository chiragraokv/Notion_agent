NotionTools = [
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task in Notion",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The Notion page ID"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["not_started", "doing", "done"]
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format"
                    },
                    "task_name": {
                        "type": "string",
                        "description": "The name of the task"
                    },
                    "meditations": {
                        "type": "string",
                        "description": "comments or notes related to task"
                    }
                },
                "required": ["task_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Update an existing task in Notion",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["not_started", "doing", "done"]
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format"
                    },
                    "task_name": {
                        "type": "string",
                        "description": "The name of the task"
                    },
                    "meditations": {
                        "type": "string",
                        "description": "comments or notes related to task"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task",
            "description": "Get an existing task from Notion",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The Notion page ID"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "find_task_by_name",
            "description": "Find a task by its name in Notion",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_name": {
                        "type": "string",
                        "description": "The name of the task"
                    }
                },
                "required": ["task_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from Notion",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The Notion page ID"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]

