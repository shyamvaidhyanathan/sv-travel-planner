###############################################################################
#   Travel Research and Planning Crew                                         #
#                                                                             #
#   Author: Shyam Vaidhyanathan                                               #
#                                                                             #
#   Genuine thanks to many open source projects and communities that          #
#   made this possible.                                                       #  
###############################################################################
import streamlit as st
from crewai import Agent, Crew, Process, Task,LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from crewai_tools import WebsiteSearchTool

from crewai.utilities.events import (LLMStreamChunkEvent)
from crewai.utilities.events.base_event_listener import BaseEventListener
from crewai.agents.parser import AgentAction, AgentFinish
from crewai.agents.crew_agent_executor import ToolResult
import re

# Get the OPEN API KEY FROM THE LOCAL .env FILE
import os
from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())




###############################################################################
class MyCustomListener(BaseEventListener):
    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(LLMStreamChunkEvent)
        def on_llm_stream_chunk(self, event: LLMStreamChunkEvent):
            # Process each chunk as it arrives
            print(f"Received chunk: {event.chunk}")

my_listener = MyCustomListener()


###############################################################################


def streamlit_agent_step_callback(step_output):
    # This function will be called after each step of the agent's execution
    st.markdown("---")
    st.markdown(step_output)

    if isinstance(step_output, AgentAction):
        st.markdown(f"Action: {step_output.text}")
    elif isinstance(step_output, AgentFinish):
        st.markdown(f"Action: {step_output.text}")
    elif isinstance(step_output, ToolResult):
        st.markdown(f"Result: {step_output.result}")



def streamlit_task_step_callback(task_output):
    # This function will be called after each step of the agent's execution
    st.markdown("---")
    st.markdown(task_output)





# Set up environment variables
# Make sure to set these in your .env file
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
OPEN_AI_KEY=os.getenv("OPEN_AI_KEY")
OPEN_AI_MODEL_NAME=os.getenv("OPEN_AI_MODEL_NAME")
SERPER_API_KEY=os.getenv("SERPER_API_KEY")


@CrewBase
class TA():

    agents: List[BaseAgent]
    tasks: List[Task]

    #Groq LLM
    llm = LLM(model="groq/gemma2-9b-it", stream=True,)  # Enable streaming
    search_tool = SerperDevTool(base_url='https://google.serper.dev')
    website_search_tool = WebsiteSearchTool()

    # AGENT #1 - Country Researcher and Planner 
    @agent
    def country_researcher_and_planning_agent(self) -> Agent:
        return Agent(
            role='Country Researcher and Planner Agent',
            config=self.agents_config['country_researcher_and_planning_agent'], # type: ignore[index]
            verbose=True,
            tools=[self.search_tool,self.website_search_tool], 
            allow_delegation=False,
            step_callback=streamlit_agent_step_callback, # type: ignore[index]
            #llm=self.localollama, # Use the local LLM instance 
        )


    @task
    def country_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['country_research_task'], # type: ignore[index]
            async_execution=True,
            markdown=True,
            output_file='country_researcher.md',
            callback=streamlit_task_step_callback, # type: ignore[index]
        )

    @task
    def country_planner_task(self) -> Task:
        return Task(
            config=self.tasks_config['country_planner_task'], # type: ignore[index]
            markdown=True,
            output_file='country_planner.md',
            #will wait for country_research_task to complete.
            context=[self.country_research_task()], # type: ignore[index]   
            callback=streamlit_task_step_callback, # type: ignore[index]
        )


    # AGENT #2 - City Researcher and Planner 
    @agent
    def city_researcher_and_planning_agent(self) -> Agent:
        return Agent(
            role='City Researcher and Planner Agent',
            config=self.agents_config['city_researcher_and_planning_agent'], # type: ignore[index]
            verbose=True,
            tools=[self.search_tool,self.website_search_tool,], 
            allow_delegation=False,
            step_callback=streamlit_agent_step_callback, # type: ignore[index]
            #llm=self.localollama, # Use the local LLM instance
        )


    @task
    def city_researcher_task(self) -> Task:
        return Task(
            config=self.tasks_config['city_researcher_task'],# type: ignore[index]
            #will wait for country_research_task and country_planner_task to complete. 
            context=[self.country_research_task(), self.country_planner_task()],
            markdown=True,
            output_file='city_researcher.md',
            callback=streamlit_task_step_callback, # type: ignore[index]
        ) 

    @task
    def city_planner_task(self) -> Task:
        return Task(
            config=self.tasks_config['city_planner_task'],# type: ignore[index]
            markdown=True,
            output_file='city_planner.md',
            #will wait for city_researcher_task, country_research_task and country_planner_task to complete. 
            context=[self.city_researcher_task(), self.country_research_task(), self.country_planner_task()], 
            callback=streamlit_task_step_callback, # type: ignore[index]
        ) 




    # AGENT #3 - Final Report Creator  
    @agent
    def final_reporting_agent(self) -> Agent:
        return Agent(
            role='Final Reporting Agent',
            config=self.agents_config['final_reporting_agent'], 
            verbose=True,
            allow_delegation=False,
            step_callback=streamlit_agent_step_callback, # type: ignore[index]
            #llm=self.localollama, # Use the local LLM instance
        ) # type: ignore


    @task
    def final_reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_reporting_task'],
            markdown=True,
            output_file='final_report.md',
            #will wait for country_research_task and country_planner_task, country_research_task and country_planner_task  to complete. 
            context=[self.country_research_task(), self.country_planner_task(), self.city_researcher_task(), self.city_planner_task()],
            callback=streamlit_task_step_callback, # type: ignore[index]
        ) # type: ignore



    # DEFINE THE CREW
    @crew
    def crew(self) -> Crew:
        """Creates the TA crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )




###########################################################################################
# Print agent process to Streamlit app container                                          #
# This portion of the code is adapted from @AbubakrChan; thank you!                       #
# https://github.com/AbubakrChan/crewai-UI-business-product-launch/blob/main/main.py#L210 #
###########################################################################################
class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a list of colors
        self.color_index = 0  # Initialize color index

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "City Selection Expert" in cleaned_data:
            # Apply different color 
            cleaned_data = cleaned_data.replace("City Selection Expert", f":{self.colors[self.color_index]}[City Selection Expert]")
        if "Local Expert at this city" in cleaned_data:
            cleaned_data = cleaned_data.replace("Local Expert at this city", f":{self.colors[self.color_index]}[Local Expert at this city]")
        if "Amazing Travel Concierge" in cleaned_data:
            cleaned_data = cleaned_data.replace("Amazing Travel Concierge", f":{self.colors[self.color_index]}[Amazing Travel Concierge]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []