import streamlit as st
import requests
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv()

# Hugging Face Inference API configuration
API_URL = os.getenv('API_URL')
headers = {"Authorization": os.getenv("API_KEY")}

def query_api(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error: Unable to fetch response from the API.")
        return {"error": response.text}

def generate_code(prompt):
    response = query_api(prompt)
    # Assuming the response contains a field 'generated_text' with the output
    if 'error' in response:
        return "Error occurred: " + response['error']
    return response.get('generated_text', '')

# Create searches
tool_search = DuckDuckGoSearchRun()

# Define Agents
manager = Agent(
    role='Project Manager',
    goal='Manage the web development project',
    backstory='Experienced in coordinating web development tasks.',
    verbose=True,
    allow_delegation=True,
    llm=generate_code,  # Use API for generating responses
    tools=[tool_search]
)

developer = Agent(
    role='Developer',
    goal='Develop the webpage based on specifications',
    backstory='An expert in web development with a focus on user-friendly interfaces.',
    verbose=True,
    allow_delegation=False,
    llm=generate_code  # Use API for code generation
)

# Streamlit interface for user input
st.title("Web Development Task Manager")

combined_prompt = st.text_area("Enter your combined HTML and CSS development prompt:")

combined_task = Task(
    description=f"Develop HTML and CSS content based on the user's prompt: {combined_prompt}",
    agent=developer,
    expected_output="HTML and CSS development completed successfully",
    subtasks=[
        "1. Design and implement the header section with a logo and navigation.",
        "2. Create a responsive layout for the main content area.",
        "3. Integrate a contact form in the footer for user inquiries.",
        "4. Apply the user-specified theme, such as using red as the primary color.",
        "5. Optimize the webpage for performance and load times.",
        "6. Generate CSS file based on the user's prompt and integrate CSS into the HTML file."
    ]
)

web_development_crew = Crew(
    agents=[manager, developer],
    tasks=[combined_task],
    verbose=True,
    process=Process.sequential
)

temp_file_name = "trial_page.html"

# Generate webpage on button click
if st.button("Generate Webpage"):
    combined_output = web_development_crew.kickoff()  # This uses API for generation.

    # Save generated output to an HTML file
    with open(temp_file_name, "w") as trial_file:
        trial_file.write(combined_output)

    st.success(f"Webpage saved to {temp_file_name}")

    st.write("Opening the trial content in the default web browser...")
    webbrowser.open(temp_file_name)

# User Feedback and Iteration
user_feedback = st.text_area("Provide feedback on the trial webpage (type 'done' when satisfied, 'modify' to provide modifications): ")

if user_feedback.lower() == 'modify':
    # Allow the user to modify the HTML and CSS content
    modified_prompt = st.text_area("Enter your modified combined HTML and CSS prompt: ")
    combined_task.description = f"Modify HTML and CSS content based on the user's prompt: {modified_prompt}"
    combined_output = web_development_crew.kickoff()  # Run the task again with the modified prompt

    # Save the modified content to the temporary file
    with open(temp_file_name, "w") as trial_file:
        trial_file.write(combined_output)

    st.success(f"Modified webpage saved to {temp_file_name}")

# Finalization and Deployment (if needed)
final_combined_output = combined_prompt
st.write("Crew: Finalizing Web Content")
st.code(final_combined_output)
