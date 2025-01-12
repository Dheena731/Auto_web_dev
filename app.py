import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import webbrowser

# Load environment variables
load_dotenv()

# Configure Google API key for prompt generation
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-8b')

# Initialize chat session and memory
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

if "history" not in st.session_state:
    st.session_state.history = []

# Step 1: User Inputs for Business Information
st.title("WebGenie")

business_name = st.text_input("Enter your business name:")
niche = st.text_input("What is the niche or industry of your business?")
theme = st.text_input("What theme would you like for the website? (e.g., Modern, Minimalistic, Colorful)")
color_scheme = st.text_input("Preferred color scheme (e.g., blue, white):")
layout = st.radio("Select website layout:", ["Single Page", "Multi Page"])

# User query input
user_query = st.text_area("Enter additional details about your website requirements:")

# Additional functionality input for Developer agent
additional_functionality = st.text_area("Enter any specific functionality or features you want in the code (e.g., animations, specific libraries):")

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
    
    Previous Context (shortened for token efficiency): 
    {memory}
    """
    return prompt

# Function for Manager agent
def manager_agent():
    manager_goal = f"Oversee the creation of a website for {business_name} in the {niche} niche. Ensure design, development, and prompt generation flow smoothly."
    manager_backstory = "Responsible for managing the web development team."
    manager_prompt = generate_prompt("Manager", manager_goal, manager_backstory)
    
    manager_response = st.session_state.chat_session.send_message(manager_prompt)
    st.write("Manager Response:", manager_response)
    store_in_memory("Manager", manager_goal, manager_response)

# Function for Designer agent
def designer_agent(manager_response):
    designer_goal = f"""
    Create the design for a responsive website for {business_name} in the {niche} niche, 
    using a {theme} theme and {color_scheme} color scheme.
    Consider the following directives from the Manager: {manager_response}
    """
    designer_backstory = "Expert in designing web layouts and aesthetics."
    designer_prompt = generate_prompt("Designer", designer_goal, designer_backstory)
    
    designer_response = st.session_state.chat_session.send_message(designer_prompt)
    st.write("Designer Response:", designer_response)
    store_in_memory("Designer", designer_goal, designer_response)
    
    return designer_response 

# Function for Developer agent with detailed prompt generation
def developer_agent_with_detailed_prompt(manager_response, designer_response):
    # Generate a detailed prompt based on user inputs and responses from Manager and Designer
    detailed_prompt_goal = f"""
    Based on the design details from the Designer: {designer_response}, 
    and considering the Manager's directives: {manager_response},
    generate a comprehensive prompt for developing the website's HTML, CSS, and JavaScript code.
    
    The user has specified the following additional requirements:
    - Specific functionality: {additional_functionality}
    - Theme: {theme}
    - Color scheme: {color_scheme}

    The generated code should be efficient, maintainable, and follow best practices for web development.
    Please also include comments and explanations for the structure and design choices in your code.
    Include any insights that should be considered during development.
    The generated prompt should guide the code generation to ensure that it meets all requirements and adheres to best practices for web development.
    """
    # Call Gemini API to generate the detailed prompt
    detailed_prompt_response = model.generate_content(detailed_prompt_goal)
    detailed_prompt = detailed_prompt_response._result.candidates[0].content.parts[0].text
    
    # Now, use this detailed prompt to generate the actual code
    developer_goal = f"Create the prompt for HTML, CSS, and JavaScript code based on the detailed requirements: {detailed_prompt}"
    developer_backstory = "Expert in implementing web designs into code."
    developer_prompt = generate_prompt("Developer", developer_goal, developer_backstory)
    
    # Call Gemini API for code generation
    developer_response = st.session_state.chat_session.send_message(developer_prompt)
    st.write("Developer Response:", developer_response)
    store_in_memory("Developer", developer_goal, developer_response)
    
    return developer_response  # Pass the code to the code generation step

# Function for generating website code using Gemini API
def generate_website_code(designer_response, developer_response):
    # Prepare the code generation goal prompt
    code_generation_goal = f"""
Generate the HTML, CSS, and JavaScript code to create a fully responsive and visually appealing website for a business called {business_name} in the {niche} industry.
Incorporate the following design elements: {designer_response}
Follow the developer's instructions as a guide: {developer_response}
The website should have the following structure and features:
1. **Header**:
   - Includes the business name "{business_name}" prominently.
   - A navigation bar with links to sections like Home, About, Services, and Contact Us.
2. **Hero Section**:
   - A full-width section with a high-quality image or background video (you can just provide the HTML structure).
   - Include a headline summarizing the business's unique value proposition.
   - A call-to-action button (e.g., "Learn More" or "Contact Us").
3. **About Section**:
   - A section providing information about the business, its mission, and what it offers.
   - Use a simple, professional layout with text and images.
4. **Services Section**:
   - List the services the business provides in a grid format, with icons or images and short descriptions.
5. **Contact Us Section**:
   - A contact form with fields for name, email, subject, and message.
   - Display contact information, including phone number, email, and address.
6. **Footer**:
   - Social media links (icons with hover effects).
   - Copyright information and additional navigation links.

### Design Guidelines:
- Use the {theme} theme with {color_scheme} as the primary color scheme (be specific with colors if necessary).
- The layout should be responsive, adjusting to mobile, tablet, and desktop screen sizes smoothly.
- The font style should be modern and professional.
- Include CSS for hover effects, transitions, and any animations to improve the user experience.
- Ensure accessibility (use `aria-labels`, and alt-text for images).

### JavaScript:
- Use JavaScript to implement basic interactions, such as:
   - A smooth scrolling effect for navigation links.
   - Form validation for the contact form.
   - A mobile-friendly hamburger menu for the navigation bar on smaller screens.

### Please generate only the code with no additional text or explanations.
### please generate the CSS and JavaScript codes without missing them; it's mandatory.
### Inline the CSS and JavaScript into the generated HTML.
"""

    # Call Gemini API to generate the code
    with st.spinner("Generating website..."):
        code_response = model.generate_content(code_generation_goal)
        generated_text = code_response._result.candidates[0].content.parts[0].text

    # Display the generated code in the app
    st.write("Generated Code:", generated_text)

    # Store in memory
    store_in_memory("Code Generator", code_generation_goal, generated_text)

    # Create a single HTML file with the generated code directly
    complete_html = generated_text  # Use the entire generated code directly

    # Save the complete HTML file
    with open("index.html", "w") as html_file:
        html_file.write(complete_html)

    st.success("Website code saved to 'index.html'.")

    # Button to preview the website
    if st.button("Preview Website"):
        # Open the local HTML file in a browser
        webbrowser.open("index.html")
        st.markdown(f"<a href='index.html' target='_blank'>Click here to view your website!</a>", unsafe_allow_html=True)


# Button to submit input and start generating prompts
if st.button("Generate Website"):
    if business_name and niche and theme and color_scheme and user_query and additional_functionality:
        
        # Manager initiates the flow
        manager_response = manager_agent()

        # Step 1: Designer creates the layout
        designer_response = designer_agent(manager_response)

        # Step 2: Developer generates a detailed prompt for code generation
        developer_response = developer_agent_with_detailed_prompt(designer_response, manager_response)

        # Step 3: Generate the website code using Gemini API
        generate_website_code(designer_response, developer_response)

    else:
        st.error("Please fill in all the fields.")
