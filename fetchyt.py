import os
from tavily import TavilyClient


def fetch_youtube_link(topic: str, grade: int) -> str:
    api_key = os.getenv('TAVILY_API_KEY')
    tavily_client = TavilyClient(api_key=api_key)
    response = tavily_client.search(f"Suggest youtube video for a {grade}th grade student about {topic}.")
    
    if 'results' in response and response['results']:
        for result in response['results']:
            url = result.get('url', '')
            if "youtube.com" in url or "youtu.be" in url:
                return url  # Return the first YouTube link found
    
    return "No relevant YouTube video found"
