import os
import sys
import asyncio
from langgraph_sdk import get_client
from graph import run_graph


async def setup_langgraph():
    client = get_client(url=os.environ["DEPLOYMENT_URL"])
    assistants = await client.assistants.search()
    assistant = [a for a in assistants if not a["config"]][0]
    return client, assistant

async def create_thread(client, assistant):
    print("Creating thread...")
    thread = await client.threads.create()
    print(f"Thread created: {thread['thread_id']}")
    return thread['thread_id']

async def execute_langgraph_run(client, assistant, thread_id, user_input):
    input_data = {"messages": [{"role": "user", "content": user_input}]}
    print(f"Sending input: {input_data}")

    async for chunk in client.runs.stream(
            thread_id,
            assistant["assistant_id"],
            input=input_data,
            stream_mode="updates",
        ):
        if chunk.data and chunk.event != "metadata":
            print(chunk.data)

async def main():
    client, assistant = await setup_langgraph()
    thread_id = await create_thread(client, assistant)
    
    while True:
        topic = input("Please enter the topic (or type 'exit' to quit): ")
        if topic.lower() == 'exit':
            break
        
        while True:
            try:
                grade = int(input("Please enter the age of the student: "))
                if grade < 3 or grade > 12:
                    raise ValueError("Age must be between 3 and 12 (inclusive).")
                break
            except ValueError as e:
                print(f"Invalid input: {e}. Please enter a valid age.")
        
        run_graph(topic, grade)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
