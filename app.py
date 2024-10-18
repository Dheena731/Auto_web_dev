import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from transformers import pipeline
import webbrowser

# Load environment variables
load_dotenv()

# Configure Google API key for prompt generation
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize code generation model (replace GPT-2 with CodeLlama or another suitable code generation model)
code_gen_model = pipeline('text-generation', model='meta-llama/CodeLlama-7b-Instruct-hf')  # Use CodeLlama

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
color_scheme = st.text_input("Preferred color scheme (e.g., blue, white):")
layout = st.radio("Select website layout:", ["Single Page", "Multi Page"])

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
def designer_agent():
    designer_goal = f"Create the design for a responsive website for {business_name} in the {niche} niche, using a {theme} theme and {color_scheme} color scheme."
    designer_backstory = "Expert in designing web layouts and aesthetics."
    designer_prompt = generate_prompt("Designer", designer_goal, designer_backstory)
    
    designer_response = st.session_state.chat_session.send_message(designer_prompt)
    st.write("Designer Response:", designer_response)
    store_in_memory("Designer", designer_goal, designer_response)
    
    return designer_response  # Pass design response to the developer

# Function for Developer agent
def developer_agent(design_details):
    developer_goal = f"Develop the HTML, CSS, and JavaScript code based on the design: {design_details}"
    developer_backstory = "Expert in implementing web designs into code."
    developer_prompt = generate_prompt("Developer", developer_goal, developer_backstory)
    
    developer_response = st.session_state.chat_session.send_message(developer_prompt)
    st.write("Developer Response:", developer_response)
    store_in_memory("Developer", developer_goal, developer_response)
    
    return developer_response  # Pass the code to the code generation step

# Button to submit input and start generating prompts
if st.button("Generate Website"):
    if business_name and niche and theme and color_scheme:
        
        # Manager initiates the flow
        manager_agent()

        # Step 1: Designer creates the layout
        design_details = designer_agent()

        # Step 2: Developer implements the design
        code_details = developer_agent(design_details)

        # Step 3: Prompt Engineer generates optimized prompts
        prompt_engineer_goal = f"Generate concise and accurate prompts for building a website for {business_name} in the {niche} niche, using a {theme} theme with a {color_scheme} color scheme."
        p_e_backstory = "Specialized in creating efficient prompts for code generation in web development."
        p_e_prompt = generate_prompt("Prompt Engineer", prompt_engineer_goal, p_e_backstory)
        
        # Get prompt engineering response
        prompt_engineer_response = st.session_state.chat_session.send_message(p_e_prompt)
        st.write("Prompt Engineer Response:", prompt_engineer_response)
        store_in_memory("Prompt Engineer", prompt_engineer_goal, prompt_engineer_response)

        # Step 4: Code Generation using CodeLlama
        code_generation_goal = f"""
Generate the HTML, CSS, and JavaScript code to create a fully responsive and visually appealing website for a business called {business_name} in the {niche} industry.
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
"""

        code_prompt = f"""
Generate the complete HTML, CSS, and JavaScript code for a responsive website for "{business_name}", a business in the {niche} industry.
The website must follow this structure:
1. A **Header** with the business name, a navigation bar (links to Home, About, Services, and Contact Us), and a mobile-friendly hamburger menu.
2. A **Hero Section** with a headline, background image, and a call-to-action button.
3. An **About Section** with text and images explaining the business.
4. A **Services Section** with a grid of services (with icons or images and short descriptions).
5. A **Contact Us Section** with a contact form and the business’s contact details.
6. A **Footer** with social media links and copyright information.

**Design Details**:
- Use the {theme} theme with a {color_scheme} color palette.
- Make the layout fully responsive for different devices (mobile, tablet, desktop).
- Ensure clean, professional typography and padding/margins for good readability.
- Add hover effects for navigation links and buttons.
- Include CSS animations for smooth scrolling and transitions.

**JavaScript**:
- Smooth scrolling for navigation links.
- Validate the contact form fields (e.g., ensure email is in a valid format).
- Implement the hamburger menu for mobile navigation.

The website must have clean and modular HTML and CSS, ensuring it is readable and maintainable. 
"""


        # Get code generation response using CodeLlama
        code_response = code_gen_model(code_prompt, max_length=2000, num_return_sequences=1, truncation=True)[0]['generated_text']
        st.write("Generated Code:", code_response)
        store_in_memory("Code Generator", code_generation_goal, code_response)

        # Split the generated code into HTML, CSS, and JS
        html_code = code_response.split("<style>")[0]  # Everything before <style> is HTML
        css_code = code_response.split("<style>")[1].split("</style>")[0]  # CSS between <style> tags
        js_code = code_response.split("<script>")[1].split("</script>")[0]  # JS between <script> tags

        # Save HTML, CSS, and JS files
        with open("index.html", "w") as html_file:
            html_file.write(html_code)
        with open("style.css", "w") as css_file:
            css_file.write(css_code)
        with open("script.js", "w") as js_file:
            js_file.write(js_code)

        st.success("Website code saved to 'index.html', 'style.css', and 'script.js'.")

        # Ensure HTML file correctly links to CSS and JS
        with open("index.html", "a") as html_file:
            html_file.write('\n<link rel="stylesheet" href="style.css">\n')
            html_file.write('<script src="script.js"></script>\n')

        # Button to preview the website
        if st.button("Preview Website"):
            # Open the local HTML file in a browser
            webbrowser.open("index.html")
            st.markdown(f"<a href='index.html' target='_blank'>Click here to view your website!</a>", unsafe_allow_html=True)

    else:
        st.error("Please fill in all the fields.")
