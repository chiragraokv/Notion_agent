from openai import OpenAI
import os
from tools import NotionTools
from notion import *
import json
FUNCTIONS = {
    "create_task": create_task,
    "update_task": update_task,
    "find_task_by_name": find_task_by_name,
    "delete_task": delete_task,
}

client = OpenAI(
    api_key=os.environ["GITHUB_TOKEN"],
    base_url="https://models.inference.ai.azure.com"
)
# here i need to write functtions to interact with notion 
def get_daily_scheduling(to_do,model = "gpt-4.1", new_task = ""):
    scheduling_prompt = f"""
Your goals are:

1. Prioritize tasks based on urgency, importance, dependencies, and deadlines.
2. Determine which task the user should focus on next.
3. Keep task statuses accurate:

   * not_started
   * doing
   * done
4. If a task is overdue and not completed, assign a realistic new due date and set its status to not_started.
5. Break large, vague, or complex tasks into smaller actionable subtasks when appropriate.
6. Create new tasks if they would help the user achieve existing goals.
7. For every task, generate a short entry for the "Meditations" field containing:

   * the purpose of the task,
   * the next concrete action,
   * any risks, blockers, or recommendations.

Guidelines:

* Prefer actionable tasks over vague goals.
* Avoid creating unnecessary tasks.
* Respect existing deadlines whenever possible.
* check if deadlines are missed and based on how difficult the task is give new
* Focus on helping the user make steady progress rather than maximizing the number of tasks.
* Keep meditation notes concise (1-3 sentences).
* Consider workload balance and task dependencies.

You have access to tools for creating, updating, and deleting tasks. Use these tools whenever changes to the task database are required instead of describing the changes in text.

Current tasks:
{to_do}
new task user wantes to do :
{new_task}
                """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a Personal assistant for scheduling tasks and manageing them ."},
            {"role": "user", "content": scheduling_prompt}],
        tools=NotionTools,
        tool_choice="auto"
    )

    return response.choices[0].message

def main():
    task = parse_tasks()
    message = get_daily_scheduling(task,new_task = "i need to sleep more (this is a recurring task)")
    if message.tool_calls:
        for call in message.tool_calls:
            function_name = call.function.name
            arguments = json.loads(call.function.arguments)

            if function_name in FUNCTIONS:
                print(f"Calling function: {function_name} with arguments: {arguments}")
                FUNCTIONS[function_name](**arguments)

if __name__ == "__main__":
    main()