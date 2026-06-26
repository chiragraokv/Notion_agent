from openai import OpenAI
# from elevenlabs.client import ElevenLabs
# from elevenlabs import save
import os
from Shengchanlu import *
import json
import pandas as pd


client = OpenAI(
    api_key=os.environ["GITHUB_TOKEN"],
    base_url="https://models.inference.ai.azure.com"
)


with open("tools.json", "r") as f:
    tools = json.load(f)
FUNCTIONS = {

    "memory": memory,
    "add_to_memory": add_to_memory,
    "analyze": analyze,
}
QUERY_FUNCTIONS = {
    "get_all_projects": get_all_projects,
    "get_project_task": get_project_task
}
CREATE_FUNCTIONS = {
    "create_project": create_project,
    "create_task_for_project": create_task_for_project,
    "add_blocks": add_blocks
}
UPDATE_FUNCTIONS = {
    "update_project": update_project,
    "update_task": update_task
}

def extract_usage_metrics(response):
    """
    Extracts token usage, model info, latency, and cost-relevant metadata
    from an OpenAI ChatCompletion response.
    """
    folder = "logs"
    file = os.path.join(folder, "app.csv")
    os.makedirs(folder, exist_ok=True)


    usage = response.usage
    metrics = {
        "response_id": getattr(response, "id", None),
        "model": getattr(response, "model", None),
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "prompt_audio_tokens": getattr(usage.prompt_tokens_details, "audio_tokens", None),
        "cached_tokens": getattr(usage.prompt_tokens_details, "cached_tokens", None),

        "reasoning_tokens": getattr(usage.completion_tokens_details, "reasoning_tokens", None),
        "accepted_prediction_tokens": getattr(usage.completion_tokens_details, "accepted_prediction_tokens", None),
        "rejected_prediction_tokens": getattr(usage.completion_tokens_details, "rejected_prediction_tokens", None),
        "audio_completion_tokens": getattr(usage.completion_tokens_details, "audio_tokens", None),
        "latency_total_ms": response.latency_checkpoint.get("total_duration_ms") if hasattr(response, "latency_checkpoint") else None,
        "ttft_ms": response.latency_checkpoint.get("engine_ttft_ms") if hasattr(response, "latency_checkpoint") else None,
        "ttlt_ms": response.latency_checkpoint.get("engine_ttlt_ms") if hasattr(response, "latency_checkpoint") else None,
        "finish_reason": response.choices[0].finish_reason if response.choices else None,
        "used_tool_calls": bool(
            response.choices[0].message.tool_calls
            if response.choices and response.choices[0].message.tool_calls
            else False
        ),
    }
    file_exists = os.path.isfile(file)

    new_row = pd.DataFrame([metrics])

    if os.path.exists(file):
        df = pd.read_excel(file)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(file, index=False)


def interact(message,fetch = None,model = "gpt-4.1",):
    role_message = """You are a personal assistant to manage all projects. you have access to all the project database. 
           you also have context memory storage. you have to assist the user in efficiently manageing task and enrich the user by smartly assigning tasks. 
           set analyze to true if more info is needed along with query functions. it is important to explore the pages before creating anything to avoid duplicates"""
    if fetch:
        message += "\n\nRequested data:\n"
        message += json.dumps(fetch, indent=2)  
    response = client.chat.completions.create(
       model=model,
       messages=[
           {"role": "system", "content":role_message },
           {"role": "user", "content": message}],
       tools=tools,
       tool_choice="auto")
    chat_msg = response.choices[0].message
    # extract_usage_metrics(response=response)
    analyze = False
    if chat_msg.tool_calls:
       for call in chat_msg.tool_calls:
           function_name = call.function.name
           arguments = json.loads(call.function.arguments)
           if function_name in FUNCTIONS:
               if function_name == "analyze":
                   print(f"Calling function: {function_name} with arguments: {arguments}")
                   analyze = FUNCTIONS[function_name](**arguments)
       for call in chat_msg.tool_calls:
           function_name = call.function.name
           arguments = json.loads(call.function.arguments)
           request = []
           if function_name in QUERY_FUNCTIONS:
               analyze = True
               print(f"Calling function: {function_name} with arguments: {arguments}")
               request.append(QUERY_FUNCTIONS[function_name](**arguments))
           if function_name in CREATE_FUNCTIONS:
               print(f"Calling function: {function_name} with arguments: {arguments}")
               res = CREATE_FUNCTIONS[function_name](**arguments)
           if function_name in UPDATE_FUNCTIONS:
               print(f"Calling function: {function_name} with arguments: {arguments}")
               UPDATE_FUNCTIONS[function_name](**arguments)    
    if analyze:
        print("reasoning 🤔")
        interact(message,request)            

                


def main():
    print("asd")
    interact(message="make a new research task about snns,give a comparision bw cnns and snns with image examples in the task using add_blocks function for me to read inside the task", model="gpt-4o-mini")
if __name__ == "__main__":
    main()
     
