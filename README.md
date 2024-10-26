# Automated Website Development Using Streamlit and Google Gemini API

## Table of Contents
* Overview
* Features
* Requirements
* Setup
* Usage
* File Structure
---------------------
## Overview

This application leverages Streamlit as a frontend to take user inputs and Google Gemini's API to generate detailed prompts for website development. The generated code is automatically saved to an HTML file, allowing users to preview the resulting website.

## Features
* Responsive Website Generation: Automatically generates responsive HTML, CSS, and JavaScript code.
* Customization: Users can specify design details such as color scheme, theme, and layout structure.
* API Integration: Uses Google Gemini's API for prompt generation and natural language processing.
* Preview Option: After generating the website code, users can preview the result directly in a browser.

## Requirements

* Python 3.8 or higher
* Streamlit
* Google Gemini API access
* Additional dependencies are specified in requirements.txt.

## Setup

### 1. Clone the repository:
<pre/>git clone https://github.com/username/automated-web-development.git
 cd automated-web-development </pre>
### 2. Create a virtual environment and activate it:
<pre/>python -m venv myenv
myenv\Scripts\activate  # On Windows
source myenv/bin/activate  # On macOS/Linux </pre>
### 3. Install the required packages:
<pre/>pip install -r requirements.txt</pre>
### 4. Add Google Gemini API credentials:
* Ensure you have access to the Google Gemini API.
* Set up your credentials following the API documentation and save them in an .env file or your environment variables.
## Usage

### Run the Streamlit app:

<pre/>streamlit run app.py </pre>

Fill out the form on the app interface:

Enter details such as business name, niche, theme, color scheme, and any additional functionality.
Generate the website by clicking the "Generate Website" button:

The app will call the Google Gemini API to generate prompts and code for the website based on the entered details.

## File Structure
* app.py: Main Streamlit app script.
* requirements.txt: List of dependencies.
* index.html: Generated HTML file for the website preview.
* README.md: Documentation file.
