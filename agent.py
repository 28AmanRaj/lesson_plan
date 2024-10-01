from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
import sys
from typing import TypedDict, Optional

# Initialize the language model
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Function to generate lesson plan sections
def generate_lesson_plan(topic: str, age: int):
    system_message = SystemMessage(
        content=f"You are an expert teacher creating an engaging lesson plan for a {age}-year-old student about {topic}. Provide clear, concise, and age-appropriate responses."
    )

    combined_prompt = (
        f"Generate a lesson plan for a {age}-year-old student about {topic}. "
        f"Include the following sections: "
        f"1. Learning Objectives: What should they learn? "
        f"2. Key Vocabulary: List key terms to learn. "
        f"3. Activities: Suggest fun introductory activities. "
        f"4. Main Activities: Provide detailed activities for understanding. "
        f"5. Content Summary: Summarize key points of the lesson. "
        f"6. Plenary: How to wrap up the lesson."
    )

    messages = [system_message, HumanMessage(content=combined_prompt)]
    response = llm.generate([messages])
    
    # Split the response into sections
    sections = response.generations[0][0].text.strip().split("\n\n")
    
    lesson_plan = {}
    for section in sections:
        # Ensure there's a colon to split on
        if ":" in section:
            title, content = section.split(":", 1)
            lesson_plan[title.strip()] = content.strip()
        else:
            print(f"Warning: Skipping section due to unexpected format: {section}")
    
    return lesson_plan

def get_user_input(topic=None, age=None) -> tuple[str, int]:
    if topic is None:
        topic = input("Enter the topic: ").strip()
    if age is None:
        while True:
            try:
                age = int(input("Enter the age of the student: "))
                if age <= 0:
                    raise ValueError("Age must be a positive integer.")
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
    lesson_plan: Optional[dict]
    error_message: Optional[str]

def graph_struct():
    print("Building lesson plan graph...")
    builder = StateGraph(LessonPlanState)

    def get_user_input_wrapper(state: LessonPlanState) -> LessonPlanState:
        topic, age = get_user_input()  # Get input from the user
        state["topic"] = topic
        state["age"] = age
        return state

    def validate_wrapper(state: LessonPlanState) -> LessonPlanState:
        # Validate the input
        if not state["topic"]:
            state["error_message"] = "Error: Topic cannot be empty."
        elif state["age"] <= 0:
            state["error_message"] = "Error: Age must be a positive integer."
        else:
            state["error_message"] = None  # Clear any previous error messages
        return state

    def generate_wrapper(state: LessonPlanState) -> LessonPlanState:
        if state.get("error_message"):
            state["lesson_plan"] = None  # No lesson plan if there's an error
            return state
        
        topic = state["topic"]
        age = state["age"]
        lesson_plan = generate_lesson_plan(topic, age)
        
        if lesson_plan:
            state["lesson_plan"] = lesson_plan
            state["error_message"] = None  # Clear any error message
        else:
            state["lesson_plan"] = None
            state["error_message"] = "Error: Lesson plan generation failed."
        
        return state

    def display_wrapper(state: LessonPlanState) -> None:
        if state.get("error_message"):
            print(state["error_message"])
        else:
            lesson_plan = state.get("lesson_plan")
            if lesson_plan:
                display_lesson_plan(lesson_plan)
            else:
                print("No lesson plan generated.")

    builder.add_node("input", get_user_input_wrapper)
    builder.add_node("validate", validate_wrapper)
    builder.add_node("generate", generate_wrapper)
    builder.add_node("output", display_wrapper)

    builder.add_edge(START, "input")
    builder.add_edge("input", "validate")
    builder.add_edge("validate", "generate")
    builder.add_edge("generate", "output")
    builder.add_edge("output", END)

    lesson_plan_graph = builder.compile()
    print("Lesson plan graph built successfully.")
    return lesson_plan_graph

lesson_plan_graph = graph_struct()

def run_graph():
    # Initialize state with empty values
    state = LessonPlanState(topic="", age=0, lesson_plan=None, error_message=None)

    try:
        # Execute the graph
        lesson_plan_graph.invoke(state)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

# Initialize lesson_plan_graph in the main block
if __name__ == "__main__":
    # load_dotenv()  # Uncomment this line if you need to load environment variables
    # print("API Key Loaded:", os.getenv('LANGCHAIN_API_KEY'))  # Uncomment to check API Key
    
    run_graph()
