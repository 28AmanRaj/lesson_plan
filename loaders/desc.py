import openai
from openai import OpenAI
from langchain_community.document_loaders import WebBaseLoader
# Set your OpenAI API key here
openai.api_key = 'OPENAI_API_KEY'
# url = "https://www.investindia.gov.in/team-india-blogs/indias-union-budget-2024-25-key-highlights"
def fetch_summarize(content: str) -> str:
    """
    Fetch content from the URL using WebBaseLoader, and summarize it to extract major topics.

    Args:
    url (str): The URL to fetch content from.

    Returns:
    str: A summary of the content with major topics.
    """
    emp_str = [str(item) for item in content]

# Convert the list into a single string
    single_string = ' '.join(emp_str)
    # single_string = ' '.join(content)
    # print("string",single_string)
    tokens = single_string.split()
    # print("alpha")
    
    # Get the first 50,000 tokens
    limited_tokens = tokens[0:50000]
    # print("limited_tokens",limited_tokens)
    # Join the tokens back into a single string
    limited_content = ' '.join(limited_tokens)
    
    prompt = (
    "You are an assistant tasked with generating a concise description of a document. "
    "Your description should highlight the most important topics covered in the document. "
    "Please ensure your description does not exceed 50 words.\n\n"
    "Document:\n"
    f"{limited_content}\n\n"
)

    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            # {"role": "user", "content": f"Summarize the following content and list the major topics:{limited_content}"}
        ],
       
    )
    summary=(completion.choices[0].message.content)
    return summary

# Example usage
# Replace with the actual URL you want to summarize
# summary = fetch_summarize(url)
# print("Summary with major topics:")
# print(summary)
