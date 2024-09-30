from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
import sys
from typing import TypedDict, Optional


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
    topic = input("Enter the topic: ").strip()
    while True:
        try:
            age = int(input("Enter the age of the student: "))
            if age < 0:
                raise ValueError("Age cannot be negative.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid age.")
    return topic, age

def display_lesson_plan(lesson_plan):
    print("\nGenerated Lesson Plan:")
    for section, content in lesson_plan.items():
        print(f"{section}:\n{content}\n")

class LessonPlanState(TypedDict):
    topic: str
    age: int
    lesson_plan: Optional[dict]  # This will hold the generated lesson plan

def graph_struct():
    print("Building lesson plan graph...")
    # Create the StateGraph with the defined TypedDict
    builder = StateGraph(LessonPlanState)

    # Define wrapper functions to match the expected signature
    def get_user_input_wrapper(state: LessonPlanState) -> LessonPlanState:
        # Get topic and age directly from state instead of user input
        topic = state["topic"]
        age = state["age"]
        
        # Ensure topic and age are provided
        if not topic or age <= 0:
            raise ValueError("Topic must be provided and age must be a positive integer.")
        
        state["topic"] = topic
        state["age"] = age
        return state  # Return updated state

    def generate_wrapper(state: LessonPlanState) -> LessonPlanState:
        topic = state["topic"]
        age = state["age"]
        lesson_plan = generate_lesson_plan(topic, age)
        state["lesson_plan"] = lesson_plan
        return state  # Return updated state

    def display_wrapper(state: LessonPlanState) -> None:
        lesson_plan = state["lesson_plan"]
        display_lesson_plan(lesson_plan)
        return None  # No return value needed
    
    # Define nodes as functions
    builder.add_node("input", get_user_input_wrapper)
    builder.add_node("generate", generate_wrapper)
    builder.add_node("output", display_wrapper)
    
    # Define edges for control flow
    builder.add_edge(START, "input")
    builder.add_edge("input", "generate")
    builder.add_edge("generate", "output")
    builder.add_edge("output", END)
    
    lesson_plan_graph = builder.compile()
    print("Lesson plan graph built successfully.")
    return lesson_plan_graph





# Create the graph
lesson_plan_graph = graph_struct()

# Execute the graph
def run_graph():
    state = LessonPlanState(topic="", age=0, lesson_plan=None)  # Initialize state

    try:
        # Execute the graph
        lesson_plan_graph.invoke(state)  # Use the appropriate method here
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    load_dotenv()
    print("API Key Loaded:", os.getenv('LANGCHAIN_API_KEY'))
    run_graph()

