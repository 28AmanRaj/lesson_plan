from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from agent import generate_lesson_plan, display_lesson_plan

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