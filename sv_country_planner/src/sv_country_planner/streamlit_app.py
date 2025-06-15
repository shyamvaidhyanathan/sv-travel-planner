###############################################################################
#   Travel Research and Planning Crew                                         #
#                                                                             #
#   Author: Shyam Vaidhyanathan                                               #
#                                                                             #
#   Genuine thanks to many open source projects and communities that          #
#   made this possible.                                                       #  
###############################################################################
#   This file is part of the CrewAI project, which is licensed under the       #
#   GNU General Public License v3.0 (GPL-3.0).                                #
#                                                                             #
#   You can redistribute it and/or modify it under the terms of the GPL-3.0.   #
#   See the LICENSE file in the root directory of this project for more details.#
#                                                                             #
#   This project is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU General Public License for more details.                              #
###############################################################################

import streamlit as st
import os
import markdown
import sys
import warnings
import re
from crew import TA
import datetime
from datetime import date
from crew import StreamToExpander


import importlib

def install_and_import(package):
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)




warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

st.set_page_config(page_title="CrewAI Streamlit Country Researcher and Planner",page_icon="✈️", layout="wide")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write( f'<span style="font-size: 48px; line-height: 1">{emoji}</span>', unsafe_allow_html=True, )


def run(homecountry,country,start_date,end_date, activity='Kayaking', openai_api_key=''):
    """
    Run the crew.
    """

    print(homecountry,country,start_date,end_date)
    inputs = {
        'HomeCountry': ''+ homecountry,
        'StartDate': ''+ start_date.strftime('%d %B %Y'),
        'EndDate': ''+ end_date.strftime('%d %B %Y'),
        'Country': '' + country,
        'PreferredActivity': '' + activity, 
        }

    try:
        print(inputs)
        result = TA().crew().kickoff(inputs=inputs)
        return result

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")



def train():
    """
    Train the crew for a given number of iterations.
    """
    print(homecountry,country,start_date,end_date)
    inputs = {
        'HomeCountry': ''+ homecountry,
        'StartDate': ''+ start_date.strftime('%d %B %Y'),
        'EndDate': ''+ end_date.strftime('%d %B %Y'),
        'Country': '' + country,
        'PreferredActivity': '' + activity, 
        }
    try:
        TA().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")



def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TA().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")



def test():
    """
    Test the crew execution and returns the results.
    """
    print(homecountry,country,start_date,end_date)
    inputs = {
        'HomeCountry': ''+ homecountry,
        'StartDate': ''+ start_date.strftime('%d %B %Y'),
        'EndDate': ''+ end_date.strftime('%d %B %Y'),
        'Country': '' + country,
        'PreferredActivity': '' + activity, 
        }

    try:
        TA().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")





###############################################################################
# main section of the script
#
###############################################################################
if __name__ == "__main__":


    install_and_import('markdown')


    st.title("Shyam 's Travel Planner - PoC")
    icon("🏖️ CrewAI + Streamlit")

    st.subheader("Let AI agents plan your next vacation!",divider="rainbow", anchor=False)

    with st.sidebar:
        st.header("👇 Enter your trip details")
        with st.form("my_form"):
            openai_api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
            if openai_api_key:
                st.session_state.openai_api_key = openai_api_key
                os.environ["OPENAI_API_KEY"] = openai_api_key
                st.write("OpenAI API Key set successfully!")
            else:   
                st.write("Please enter your OpenAI API Key to proceed.")

                
            st.divider()


            homecountry  = st.text_input("What's your home country ?", placeholder="USA")
            country      = st.text_input("Country are you interested in ?", placeholder="Indonesia")
            default_start_date = date(2025, 12, 10)
            default_end_date = date(2026, 1, 1)
            start_date         = st.date_input("Start Date:",
                                          value=default_start_date,  # Optional: Default 
                                          min_value=date(2025, 12, 1),  # Optional: Minimum date
                                          max_value=date(2030, 12, 31) ) # Optional: Maximum date
            end_date           = st.date_input("End Date:",
                                          value=default_end_date,  # Optional: Default 
                                          min_value=date(2025, 12, 1),  # Optional: Minimum date
                                          max_value=date(2030, 12, 31) ) # Optional: Maximum date
            
            activity            = st.text_input("Any preferred activity you like to do ?", placeholder="Kayaking")
            submitted = st.form_submit_button("Submit")

        st.divider()
        st.sidebar.markdown(body="", unsafe_allow_html=True,)
    

    if submitted:
        with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
            with st.container(height=500, border=False):
                #sys.stdout = StreamToExpander(st)
                
                result     = run(homecountry,country,start_date,end_date,openai_api_key)
                

            status.update(label="✅ Trip Plan Ready!",state="complete", expanded=False)

        st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
        st.markdown(result)
        
        st.subheader("Execution Data", anchor=False, divider="rainbow")
        st.markdown(f"**Token Usage:** {result.token_usage}")
        st.markdown(f"**Token Usage:** {result.to_dict()}")




