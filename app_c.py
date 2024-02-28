from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI                 #pip install langchain-openai
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
import google.generativeai as genai 
#from openai import GPT3Model
from dotenv import load_dotenv
import streamlit as st 
import os 
import time

load_dotenv()
#genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
#llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature = 0.7, convert_system_message_to_human=True)

genai.configure(api_key=os.environ["OPENAI_API_KEY"])
llm = ChatOpenAI(temperature=0.7, max_tokens=1000, model_name="gpt-3.5-turbo")
#llm = ChatOpenAI(temperature=0.7, max_tokens=1000, model_name="ft:gpt-3.5-turbo-0613:langchain::7qTVM5AR")
#llm = ChatOpenAIGenerativeAI(model="gpt-3.5-turbo", temperature = 0.7, convert_system_message_to_human=True)
# Chain ----------------------------------------------------------------------------------------
template1 = """
As a visionary leader skilled in strategic analysis and decision-making,
please analyze the problem statement, goals, and constraints outlined in {input}.
Generate {number} distinct solutions while meticulously considering the needs
of stakeholders and the relevant decision criteria specified for {factors}.
Ensure that all responses remain contextually relevant to {elements}, if applicable, throughout the process.
Additionally, for each solution, provide a few business scenarios tailored 
to the chosen {elements}, if applicable, to illustrate practical applications.
"""
prompt1 = PromptTemplate(input_variables=["input", "factors", "number","elements"],template=template1)
chain1= LLMChain(llm=llm,prompt=prompt1,output_key="prop_soln")

template4 = """
Each solution should be elaborate further into 7 points: 
- Detail Solution
- Probability of success (%)
- Key Features and Functionality
- Implementation Process
- Justification 
- Pros and Cons
- Final thoughts
Rank according to the highest probability of success. Seperate solutions using horizontal lines.
{prop_soln}
"""
prompt4 = PromptTemplate(input_variables=["prop_soln"],template=template4)
chain4 = LLMChain(llm=llm,prompt=prompt4,output_key="result")

chain = SequentialChain(
    chains=[chain1, chain4],
    input_variables=["input", "factors", "number","elements"],
    output_variables=["result"]
)

# Set page configuration to wide layout
st.set_page_config(layout="wide", page_title="Beta-SDMS", page_icon="ai.png")

# Theme Dark or Light, https://discuss.streamlit.io/t/changing-the-streamlit-theme-with-a-toggle-button-solution/56842/2
ms = st.session_state
if "themes" not in ms: 
  ms.themes = {"current_theme": "light",
                    "refreshed": True,
                    
                    "light": {"theme.base": "dark",
                              "theme.backgroundColor": "#131314",
                              "theme.primaryColor": "#474747",
                              "theme.secondaryBackgroundColor": "#1e1f20",
                              "theme.textColor": "white",
                              "button_face": "🌙"},

                    "dark":  {"theme.base": "light",
                              "theme.backgroundColor": "white",
                              "theme.primaryColor": "#172d67",
                              "theme.secondaryBackgroundColor": "#22ddd2",
                              "theme.textColor": "#0a1464",
                              "button_face": "☀️"},
                    }
def ChangeTheme():
  previous_theme = ms.themes["current_theme"]
  tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
  for vkey, vval in tdict.items(): 
    if vkey.startswith("theme"): st._config.set_option(vkey, vval)

  ms.themes["refreshed"] = False
  if previous_theme == "dark": ms.themes["current_theme"] = "light"
  elif previous_theme == "light": ms.themes["current_theme"] = "dark"

btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]["button_face"]

# Align the button to the right
st.write("")  # Add an empty space to push the button to the right
col1, col2 = st.columns([20, 1])  # Adjust column widths as needed
with col1:
    st.header("Strategic Decision Making - Beta")
with col2:
    st.button(btn_face, on_click=ChangeTheme)

if ms.themes["refreshed"] == False:
    ms.themes["refreshed"] = True
    st.rerun()

# Sidebar ---------------------------------------------------------------------------------
# Create a container to center the image & logo image 
col1, col2, col3 = st.sidebar.columns([1, 1, 2])
with col2: st.image("Cognimus Round.png", width=130)

# Add an expander for the entire sidebar
with st.sidebar.expander("Selection Panel", expanded=True):  # Set expanded=True if you want the sidebar expanded by default
    # Select business elements
    elements = st.multiselect(
        "Select a maximum of three (3) business elements:\n\n",
        [
            "Financial",
            "Resources",
            "Technology",
            "Ownership",
            "Data",
            "Infrastructure",
            "Security",
            "Agility",
            "People",
            "Process",
        ],
        key="elements",  # Set a unique key for the multiselect widget
    )
    # Select distinct solution slider
    num = st.slider("Number of distinct solutions?", 2, 5, step=1)

# About Cognimus AI
with st.sidebar.expander("**About Cognimus AI**"):
    st.write("Cognimus AI is your premier strategic decision-making companion designed to elevate your organizational prowess to new heights. In the dynamic landscape of today's business world, informed decisions are the cornerstone of success, and Cognimus AI is here to empower you with the tools and insights you need to navigate with confidence.")

# Additional information at the bottom, bottom-centered and smaller font size
additional_info = "<p style='font-size:smaller; text-align:center;'>This is a beta version of Cognimus AI</p>"
st.sidebar.markdown(additional_info, unsafe_allow_html=True)

# Main + Input --------------------------------------------------------------------------------------
# Input
st.subheader("Problem description, Goals and Constraints/Limitation")
inp     = st.text_area("The current [process/procedure/system] at [Organization/Department] is inefficient, leading to delays in [desired outcome]. This problem is significant as it hampers [impact on stakeholders or goals], impacting the organization's ability to [relevant organizational objectives], (Copy, paste and change accordingly)", placeholder="Problem description, Goals and Constraints/Limitation", label_visibility='visible')

# Factors
st.subheader("Stakeholders & Decision Criteria")
factors = st.text_area("Addressing this problem is crucial for the organization as it aims to [desired improvement], ultimately [benefit to the organization or stakeholders] (Copy, paste and change accordingly).", placeholder="Stakeholders & Decision Criteria", label_visibility='visible')

# Disclaimer
st.write("<span style='font-size: 12px; color: red;'>Disclaimer: While Cognimus AI aims for accuracy, it may occasionally provide incomplete or inaccurate information, including details about individuals. Therefore, it's recommended to verify its responses, especially for sensitive matters. Additionally, Cognimus AI cannot ensure a 100% success rate in strategy formulation, nor can it be held responsible for execution outcomes.</span>", unsafe_allow_html=True)

# Output -------------------------------------------------------------------------------------------- 
def simulate_long_running_task_progbar():
    for i in range(100):
        # Simulate a long-running task
        time.sleep(0.1)
        # Update the progress bar
        progress_bar.progress(i + 1)
    st.success('Thinking completed!')

if st.button("THINK", use_container_width=True):
    with st.spinner("Thinking..."):
        # Include selected elements in the input dictionary
        input_data = {"input": inp, "factors": factors, "number": num, "elements": elements}
        # Call the chain function with the updated input
        res = chain(input_data)
        progress_bar = st.progress(0)
        simulate_long_running_task_progbar()
        st.write("")
        st.subheader(":red[Response]")
        st.markdown(res['result'])

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
