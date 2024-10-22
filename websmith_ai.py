import streamlit as st
import requests
from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
import webbrowser
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY=os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model=genai.GenerativeModel('gemini-pro')

CODELLAMA_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-hf"  # Replace with the actual URL for CodeLlama model
HEADERS = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}

def generate_detailed_prompt(user_query):
    """Generate a detailed prompt using the Gemini model."""
    response = llm.generate(prompt=user_query)
    if response:
        return response.get('generated_text', 'Error: No generated text found.')
    else:
        st.error("Error: Unable to fetch response from the Gemini model.")
        return "Error: No response from Gemini model."

def generate_code(detailed_prompt):
    """Generate code using the CodeLlama model based on the detailed prompt."""
    response = query_api(CODELLAMA_API_URL, {"inputs": detailed_prompt})
    if 'error' in response:
        return "Error occurred: " + response['error']
    return response.get('generated_text', 'Error: No generated text found.')

def query_api(api_url, payload):
    """Query a specified API with the given payload and return the response."""
    response = requests.post(api_url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error("Error: Unable to parse response.")
            return {"error": "Invalid response format"}
    else:
        st.error(f"Error: {response.status_code} - Unable to fetch response from the API.")
        return {"error": response.text}

# Create searches
tool_search = DuckDuckGoSearchRun()

# Define Agents
prompt_engineer = Agent(
    role='Prompt Engineer',
    goal='Generate detailed prompts based on user input',
    backstory='Specialized in creating detailed prompts for code generation.',
    verbose=True,
    allow_delegation=False,
    llm=lambda prompt: generate_detailed_prompt(prompt)  # Using Gemini model for prompt generation
)

developer = Agent(
    role='Developer',
    goal='Develop the webpage based on specifications',
    backstory='An expert in web development with a focus on user-friendly interfaces.',
    verbose=True,
    allow_delegation=False,
    llm=lambda prompt: generate_code(prompt)  # Using CodeLlama model for code generation
)

# Define the Project Manager
manager = Agent(
    role='Project Manager',
    goal='Manage the web development project',
    backstory='Experienced in coordinating web development tasks.',
    verbose=True,
    allow_delegation=True,
    llm=lambda prompt: generate_code(prompt),  # Ensure proper lambda wrapping
    tools=[tool_search]
)

# Streamlit interface for user input
st.title("Web Development Task Manager")

user_query = st.text_area("Enter your HTML and CSS development prompt:")

# Define the main task for the prompt engineer and developer
combined_task = Task(
    description=f"Generate detailed prompt based on the user's input: {user_query}",
    agent=prompt_engineer,
    expected_output="Detailed prompt generated successfully",
    subtasks=[
        "1. Create a detailed prompt for the developer based on the user's input."
    ]
)

# Define the task for the developer
development_task = Task(
    description="Develop HTML and CSS content based on the detailed prompt.",
    agent=developer,
    expected_output="HTML and CSS development completed successfully",
    subtasks=[
        "1. Design and implement the header section with a logo and navigation.",
        "2. Create a responsive layout for the main content area.",
        "3. Integrate a contact form in the footer for user inquiries.",
        "4. Apply the user-specified theme, such as using red as the primary color.",
        "5. Optimize the webpage for performance and load times.",
        "6. Generate CSS file based on the detailed prompt and integrate CSS into the HTML file."
    ]
)

# Setup the Crew
web_development_crew = Crew(
    agents=[manager, prompt_engineer, developer],
    tasks=[combined_task, development_task],
    verbose=True,
    process=Process.sequential
)

temp_file_name = "trial_page.html"

# Generate webpage on button click
if st.button("Generate Webpage"):
    # Run the prompt engineer task first
    detailed_prompt_output = web_development_crew.kickoff()  # This uses API for prompt generation.
    
    if isinstance(detailed_prompt_output, str) and not detailed_prompt_output.startswith("Error"):
        st.write("**Detailed Prompt Generated:**")
        st.code(detailed_prompt_output)
        
        # Run the developer task with the detailed prompt
        combined_task.description = f"Develop HTML and CSS content based on the detailed prompt: {detailed_prompt_output}"
        development_task.description = combined_task.description
        development_output = web_development_crew.kickoff()  # This uses API for code generation.
        
        if isinstance(development_output, str) and not development_output.startswith("Error"):
            # Save generated output to an HTML file
            with open(temp_file_name, "w") as trial_file:
                trial_file.write(development_output)

            st.success(f"Webpage saved to {temp_file_name}")
            st.write("Opening the trial content in the default web browser...")
            file_path = os.path.join(os.getcwd(), temp_file_name)
            webbrowser.open(f"file://{file_path}")
        else:
            st.error(f"Failed to generate code: {development_output}")
    else:
        st.error(f"Failed to generate detailed prompt: {detailed_prompt_output}")

# User Feedback and Iteration
user_feedback = st.text_area("Provide feedback on the trial webpage (type 'done' when satisfied, 'modify' to provide modifications): ")

if user_feedback.lower() == 'done':
    st.write("Webpage finalized. No further modifications.")
elif user_feedback.lower() == 'modify':
    modified_query = st.text_area("Enter your modified prompt: ")
    if modified_query:
        # Generate a new detailed prompt based on modified input
        detailed_prompt_output = generate_detailed_prompt(modified_query)
        st.write("**Detailed Prompt Generated:**")
        st.code(detailed_prompt_output)
        
        if not detailed_prompt_output.startswith("Error"):
            # Generate modified code using the new detailed prompt
            final_code = generate_code(detailed_prompt_output)
            if not final_code.startswith("Error"):
                temp_file_name = "modified_page.html"
                
                # Save the modified content to an HTML file
                with open(temp_file_name, "w") as trial_file:
                    trial_file.write(final_code)

                st.success(f"Modified webpage saved to {temp_file_name}")
                file_path = os.path.join(os.getcwd(), temp_file_name)
                webbrowser.open(f"file://{file_path}")
            else:
                st.error(f"Failed to generate modified code: {final_code}")
        else:
            st.error(f"Failed to generate detailed prompt: {detailed_prompt_output}")
    else:
        st.error("Please enter a modified prompt.")
