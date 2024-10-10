from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from agent import generate_lesson_plan, display_lesson_plan

class LessonPlanState(TypedDict):
    topic: str
    grade: int
    subject: str
    lesson_plan: Optional[dict]
    error_message: Optional[str]

def graph_struct():
    print("Building lesson plan graph...")
    builder = StateGraph(LessonPlanState)

    def validate_wrapper(state: LessonPlanState) -> LessonPlanState:
        if not state["topic"]:
            state["error_message"] = "Error: Topic cannot be empty."
        elif state["grade"] < 3 or state["grade"] > 12:
            state["error_message"] = "Error: Age must be between 3 and 12 (inclusive)."
        else:
            state["error_message"] = None  # Clear previous errors
        return state


    def generate_wrapper(state: LessonPlanState) -> LessonPlanState:
    # Check if there's an error message before proceeding
        if state.get("error_message"):
            state["lesson_plan"] = None
            return state

        topic = state["topic"]
        grade = state["grade"]
        subject = state["subject"]
        

    # Generate the lesson plan
        lesson_plan = generate_lesson_plan(topic, grade, subject)
    
    # Check if the lesson plan was successfully generated
        if lesson_plan:
            state["lesson_plan"] = lesson_plan
            state["error_message"] = None
            display_lesson_plan(lesson_plan)  
        else:
            state["lesson_plan"] = None
            state["error_message"] = "Error: Lesson plan generation failed."  # Set an error message if generation failed

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


def run_graph(topic: str, grade: int, subject: str):
    state = LessonPlanState(topic=topic, grade=grade, subject=subject, lesson_plan=None, error_message=None)

    try:
        lesson_plan_graph.invoke(state)
    except Exception as e:
        state['error_message'] = str(e)
    finally:
        return state

