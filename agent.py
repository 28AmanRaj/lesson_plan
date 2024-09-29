from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import langsmith
from langgraph.graph import StateGraph, START, END

"""load_dotenv()
api_key = os.getenv('LANGCHAIN_API_KEY')

langsmith_client = langsmith.Client(api_key=api_key)"""
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Function to generate lesson plan sections
def generate_lesson_plan(topic: str, age: int):
    system_message = SystemMessage(
        content=f"You are an expert teacher creating an engaging lesson plan for a {age}-year-old student about {topic}. Provide clear, concise, and age-appropriate responses."
    )

    prompts = {
        "Learning Objectives": f"What should a {age}-year-old student learn from a lesson about {topic}?",
        "Key Vocabulary": f"List key vocabulary terms that a {age}-year-old should learn from a lesson on {topic}.",
        "Activities": f"What are some fun, introductory activities for a {age}-year-old to introduce the topic {topic}?",
        "Main Activities": f"Provide detailed main activities for a {age}-year-old to help them understand {topic}.",
        "Content Summary": f"Summarize the key points of a lesson on {topic} for a {age}-year-old.",
        "Plenary": f"How can a teacher wrap up a lesson on {topic} for a {age}-year-old student?"
    }

    lesson_plan = {}
    
    for section, prompt in prompts.items():
        messages = [system_message, HumanMessage(content=prompt)]
        response = llm.generate([messages])
        lesson_plan[section] = response.generations[0][0].text.strip()
    
    return lesson_plan

def get_user_input():
    topic = input("Enter the topic: ")
    age = int(input("Enter the age of the student: "))
    return topic, age

def display_lesson_plan(lesson_plan):
    print("\nGenerated Lesson Plan:")
    for section, content in lesson_plan.items():
        print(f"{section}:\n{content}\n")

def graph_struct():
    builder = StateGraph(state_schema={
        "input": {"topic": str, "age": int},
        "output": {"lesson_plan": dict},
    })

    # Define nodes as functions
    builder.add_node("start", get_user_input)
    builder.add_node("generate", generate_lesson_plan)
    builder.add_node("output", display_lesson_plan)

    # Define edges for control flow
    builder.add_edge(START, "start")
    builder.add_edge("start", "generate")
    builder.add_edge("generate", "output")
    builder.add_edge("output", END)

    part_1_graph = builder.compile()

    return part_1_graph

# Create the graph
lesson_plan_graph = graph_struct()

# Execute the graph
def run_graph():
    topic, age = get_user_input()
    lesson_plan = generate_lesson_plan(topic, age)
    display_lesson_plan(lesson_plan)

run_graph()
