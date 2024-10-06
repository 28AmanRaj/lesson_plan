# agent.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import sys
from fetchyt import fetch_youtube_link



# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
load_dotenv()

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
