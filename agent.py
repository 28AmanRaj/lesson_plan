# agent.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import sys
from typing import TypedDict, Optional
from tavily import TavilyClient
from langgraph.graph import StateGraph, START, END
import asyncio
from langgraph_sdk import get_client

# Initialize the language model
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
load_dotenv()

def fetch_youtube_link(topic: str, age: int) -> str:
    api_key = os.getenv('TAVILY_API_KEY')
    tavily_client = TavilyClient(api_key=api_key)
    response = tavily_client.search(f"Suggest youtube video for a {age}-year-old student about {topic}.")
    
    if 'results' in response and response['results']:
        for result in response['results']:
            url = result.get('url', '')
            if "youtube.com" in url or "youtu.be" in url:
                return url  # Return the first YouTube link found
    
    return "No relevant YouTube video found"

def generate_lesson_plan(topic: str, age: int):
    system_message = SystemMessage(
        content=f"You are an expert teacher creating an engaging lesson plan for a {age}-year-old student about {topic}. Provide clear, concise, and age-appropriate responses."
    )

    prompts = {
        "Learning Objectives": f"What should a {age}-year-old student learn from a lesson about {topic}?",
        "Key Vocabulary": f"List key vocabulary terms that a {age}-year-old should learn from a lesson on {topic}.",
        "Activities": f"What are some fun, introductory activities for a {age}-year-old to introduce the topic {topic}?",
        "Content Summary": f"Summarize the key points of a lesson on {topic} for a {age}-year-old.",
        "YouTube Link": fetch_youtube_link(topic, age)
    }

    lesson_plan = {}
    
    for section, prompt in prompts.items():
        if section == "YouTube Link":
            lesson_plan[section] = prompt
        else:
            messages = [system_message, HumanMessage(content=prompt)]
            response = llm.generate([messages])
            lesson_plan[section] = response.generations[0][0].text.strip()
    
    return lesson_plan

def display_lesson_plan(lesson_plan):
    print("\nGenerated Lesson Plan:")
    for section, content in lesson_plan.items():
        print(f"{section}:\n{content}\n")

class LessonPlanState(TypedDict):
    topic: str
    age: int
    lesson_plan: Optional[dict]
    error_message: Optional[str]

def graph_struct():
    print("Building lesson plan graph...")
    builder = StateGraph(LessonPlanState)

    def validate_wrapper(state: LessonPlanState) -> LessonPlanState:
        if not state["topic"]:
            state["error_message"] = "Error: Topic cannot be empty."
        elif state["age"] <= 0:
            state["error_message"] = "Error: Age must be a positive integer."
        else:
            state["error_message"] = None  # Clear any previous error messages
        return state

    def generate_wrapper(state: LessonPlanState) -> LessonPlanState:
        if state.get("error_message"):
            state["lesson_plan"] = None
            return state
        
        topic = state["topic"]
        age = state["age"]
        lesson_plan = generate_lesson_plan(topic, age)
        
        if lesson_plan:
            state["lesson_plan"] = lesson_plan
            state["error_message"] = None
            display_lesson_plan(lesson_plan)
        else:
            state["lesson_plan"] = None
            state["error_message"] = "Error: Lesson plan generation failed."
        
        return state

    builder.add_node("validate", validate_wrapper)
    builder.add_node("generate", generate_wrapper)

    builder.add_edge(START, "validate")
    builder.add_edge("validate", "generate")
    builder.add_edge("generate", END)

    lesson_plan_graph = builder.compile()
    print("Lesson plan graph built successfully.")
    return lesson_plan_graph

lesson_plan_graph = graph_struct()

def run_graph(topic: str, age: int):
    state = LessonPlanState(topic=topic, age=age, lesson_plan=None, error_message=None)

    try:
        lesson_plan_graph.invoke(state)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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
                age = int(input("Please enter the age of the student: "))
                if age <= 0:
                    raise ValueError("Age must be a positive integer.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}. Please enter a valid age.")
        
        run_graph(topic, age)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
