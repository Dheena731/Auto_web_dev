import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from transformers import pipeline

# Load environment variables
load_dotenv()

# Configure Google API key for prompt generation
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize code generation model (e.g., Codex)
from transformers import pipeline

# Initialize code generation model (use a valid GPT-2 model)
code_gen_model = pipeline('text-generation', model='gpt2')  # Change this to any other suitable model if needed


# Initialize chat session and memory
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

if "history" not in st.session_state:
    st.session_state.history = []

# Step 1: User Inputs for Business Information
st.title("Website Builder - AI Automation")

business_name = st.text_input("Enter your business name:")
niche = st.text_input("What is the niche or industry of your business?")
theme = st.text_input("What theme would you like for the website? (e.g., Modern, Minimalistic, Colorful)")

# Function to store previous queries and responses in session state
def store_in_memory(role, goal, response):
    st.session_state.history.append({
        "role": role,
        "goal": goal,
        "response": response
    })

# Function to dynamically generate the agent prompts with memory
def generate_prompt(role, goal, backstory):
    memory = "\n".join([f"{item['role']} said: {item['response']}" for item in st.session_state.history])
    prompt = f"""
    Role: {role}
    Goal: {goal}
    Backstory: {backstory}
    
    Previous Context: 
    {memory}
    """
    return prompt

# Button to submit input and start generating prompts
if st.button("Generate Website"):
    if business_name and niche and theme:
        
        # Step 2: Dynamic Prompt Generation for Agents
        # Prompt Engineer
        prompt_engineer_goal = f"Generate detailed prompts for building a website for {business_name} in the {niche} niche, using a {theme} theme."
        p_e_backstory = "Specialized in creating detailed prompts for code generation in the context of web development."
        p_e_prompt = generate_prompt("Prompt Engineer", prompt_engineer_goal, p_e_backstory)
        
        # Get prompt engineering response
        prompt_engineer_response = st.session_state.chat_session.send_message(p_e_prompt)
        st.write("Prompt Engineer Response:", prompt_engineer_response)
        store_in_memory("Prompt Engineer", prompt_engineer_goal, prompt_engineer_response)

        # Code Generation
        code_generation_goal = f"Generate the HTML, CSS, and JavaScript code to create a responsive website for {business_name} in the {niche} niche with a {theme} theme."
        code_prompt = f"Create a responsive website for {business_name} in the {niche} niche, using a {theme} theme. Include HTML, CSS, and JavaScript."
        
        # Get code generation response using Codex or another model
        code_response = code_gen_model(code_prompt, max_length=500, num_return_sequences=1)[0]['generated_text']
        st.write("Generated Code:", code_response)
        store_in_memory("Code Generator", code_generation_goal, code_response)

        # Save generated code to an HTML file
        if code_response:
            with open("website.html", "w") as file:
                file.write(code_response)
            st.success("Website code saved to 'website.html'.")

            # Button to open the generated HTML file in a new tab
            if st.button("Open Website"):
                st.markdown("<a href='website.html' target='_blank'>Click here to view your website!</a>", unsafe_allow_html=True)

    else:
        st.error("Please fill in all the fields.")
