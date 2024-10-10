import os
from langgraph_sdk import get_client
from graph import run_graph
from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from typing import  Optional

class LessonPlanRequest(BaseModel):
    topic: str
    grade: int
    subject: str
    pdf_file: Optional[UploadFile] = File(None)

class LessonPlanResponse(BaseModel):
    lesson_plan: Optional[dict]
    error_message: Optional[str] = None


app = FastAPI()


"""async def setup_langgraph():
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

    # Take input only once
    topic = input("Please enter the topic: ")

    while True:
        try:
            grade = int(input("Please enter the grade of the student: "))
            if grade < 3 or grade > 12:
                raise ValueError("Grade must be between 3 and 12 (inclusive).")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid grade.")

    # Run the graph only once with the fixed topic and grade
    run_graph(topic, grade)

    # Optionally, you can add a message after running the graph
    print("Graph has been run successfully.")"""


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Lesson Plan API!"}


@app.post("/generate_lesson_plan", response_model=LessonPlanResponse)
async def generate_lesson_plan(
    topic: str = Form(...),  # Using Form to handle string input
    grade: int = Form(...),
    subject: str = Form(...),   # Using Form to handle integer input
    pdf_file: UploadFile = File(None)  # UploadFile for the PDF
):
    # Log the received inputs
    print(f"Received Topic: {topic}")
    print(f"Received Grade: {grade}")
    print(f"Received Subject: {subject}")
    
    if pdf_file:
        print(f"Received PDF file: {pdf_file.filename}")  # Log the file name

    # Here you would normally run your graph logic
    state = run_graph(topic, grade, subject) or {}

    if 'error_message' in state and state['error_message']:
        return LessonPlanResponse(lesson_plan={}, error_message=state['error_message'])

    return LessonPlanResponse(lesson_plan=state.get('lesson_plan', None), error_message=None)







