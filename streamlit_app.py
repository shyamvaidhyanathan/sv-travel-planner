import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import json
from datetime import datetime, timedelta
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .itinerary-day {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_api_keys():
    """Initialize API keys from Streamlit secrets or environment variables"""
    try:
        # Try to get from Streamlit secrets first
        if hasattr(st, 'secrets'):
            openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
            serper_api_key = st.secrets.get("SERPER_API_KEY", "")
        else:
            openai_api_key = ""
            serper_api_key = ""
        
        # Fallback to environment variables
        if not openai_api_key:
            openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if not serper_api_key:
            serper_api_key = os.getenv("SERPER_API_KEY", "")
            
        return openai_api_key, serper_api_key
    except Exception as e:
        st.error(f"Error initializing API keys: {e}")
        return "", ""

def create_travel_agents(serper_api_key):
    """Create the travel planning crew agents"""
    
    # Initialize search tool
    search_tool = SerperDevTool(api_key=serper_api_key) if serper_api_key else None
    
    # Research Agent
    researcher = Agent(
        role='Travel Research Specialist',
        goal='Research and gather comprehensive information about travel destinations, attractions, and local insights',
        backstory="""You are an expert travel researcher with extensive knowledge of global destinations. 
        You excel at finding hidden gems, local attractions, cultural experiences, and practical travel information.
        You always provide accurate, up-to-date information about destinations.""",
        tools=[search_tool] if search_tool else [],
        verbose=True,
        allow_delegation=False
    )
    
    # Planning Agent
    planner = Agent(
        role='Travel Itinerary Planner',
        goal='Create detailed, optimized travel itineraries based on user preferences and research data',
        backstory="""You are a professional travel planner with years of experience creating perfect itineraries.
        You excel at optimizing travel routes, timing activities, and creating balanced schedules that maximize
        the travel experience while considering budget, time constraints, and personal preferences.""",
        verbose=True,
        allow_delegation=False
    )
    
    # Budget Agent
    budget_analyst = Agent(
        role='Travel Budget Analyst',
        goal='Analyze and optimize travel costs, providing detailed budget breakdowns and cost-saving recommendations',
        backstory="""You are a financial expert specializing in travel budgeting. You have extensive knowledge
        of travel costs worldwide and excel at finding the best deals and cost-effective options while
        maintaining quality experiences.""",
        tools=[search_tool] if search_tool else [],
        verbose=True,
        allow_delegation=False
    )
    
    # Local Expert Agent
    local_expert = Agent(
        role='Local Culture Expert',
        goal='Provide authentic local insights, cultural recommendations, and insider tips for destinations',
        backstory="""You are a cultural anthropologist and local expert who has lived in various destinations
        around the world. You provide authentic cultural insights, local customs, food recommendations,
        and insider tips that only locals would know.""",
        verbose=True,
        allow_delegation=False
    )
    
    return researcher, planner, budget_analyst, local_expert

def create_travel_tasks(researcher, planner, budget_analyst, local_expert, travel_details):
    """Create tasks for the travel planning crew"""
    
    # Research Task
    research_task = Task(
        description=f"""Research comprehensive information about {travel_details['destination']} for a 
        {travel_details['duration']}-day trip from {travel_details['start_date']} to {travel_details['end_date']}.
        
        Focus on:
        - Top attractions and must-see places
        - Weather conditions during travel dates
        - Transportation options
        - Accommodation recommendations
        - Local events and festivals
        - Safety considerations
        - Entry requirements and visa information
        
        Travel preferences: {travel_details['preferences']}
        Budget range: ${travel_details['budget']}
        Travel style: {travel_details['travel_style']}""",
        agent=researcher,
        expected_output="Detailed research report with all relevant destination information"
    )
    
    # Planning Task
    planning_task = Task(
        description=f"""Create a detailed {travel_details['duration']}-day itinerary for {travel_details['destination']}
        based on the research findings.
        
        Requirements:
        - Day-by-day schedule with timing
        - Balance of activities and rest time
        - Optimized routing to minimize travel time
        - Mix of popular attractions and hidden gems
        - Consideration of weather and seasonal factors
        - Flexible options for different interests
        
        Include:
        - Daily activities with descriptions
        - Recommended restaurants and dining
        - Transportation between locations
        - Estimated time for each activity
        - Alternative options for bad weather
        
        Budget: ${travel_details['budget']}
        Preferences: {travel_details['preferences']}""",
        agent=planner,
        expected_output="Complete day-by-day itinerary with detailed scheduling and activities"
    )
    
    # Budget Task
    budget_task = Task(
        description=f"""Analyze and create a detailed budget breakdown for the {travel_details['duration']}-day 
        trip to {travel_details['destination']} with a budget of ${travel_details['budget']}.
        
        Provide:
        - Detailed cost breakdown by category (accommodation, food, activities, transport, etc.)
        - Daily spending estimates
        - Cost-saving recommendations
        - Budget vs. premium options
        - Emergency fund suggestions
        - Payment methods and currency information
        - Tips for getting the best deals
        
        Consider the planned itinerary and provide realistic cost estimates.""",
        agent=budget_analyst,
        expected_output="Comprehensive budget analysis with detailed cost breakdowns and money-saving tips"
    )
    
    # Local Insights Task
    local_task = Task(
        description=f"""Provide authentic local insights and cultural recommendations for {travel_details['destination']}.
        
        Include:
        - Local customs and etiquette
        - Authentic local food experiences
        - Hidden gems known only to locals
        - Cultural events and festivals
        - Local transportation tips
        - Shopping recommendations
        - Language tips and useful phrases
        - Cultural do's and don'ts
        - Local neighborhoods to explore
        - Authentic experiences beyond tourist attractions
        
        Make the recommendations feel authentic and provide insider knowledge.""",
        agent=local_expert,
        expected_output="Authentic local insights with cultural recommendations and insider tips"
    )
    
    return research_task, planning_task, budget_task, local_task

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 AI Travel Planner</h1>
        <p>Let our AI crew plan your perfect trip!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize API keys
    openai_api_key, serper_api_key = initialize_api_keys()
    
    # Sidebar for API configuration
    st.sidebar.header("🔑 API Configuration")
    
    # API Key inputs
    openai_input = st.sidebar.text_input(
        "OpenAI API Key", 
        value=openai_api_key, 
        type="password",
        help="Required for AI agents to function"
    )
    
    serper_input = st.sidebar.text_input(
        "Serper API Key", 
        value=serper_api_key, 
        type="password",
        help="Optional: For real-time web search capabilities"
    )
    
    # Set environment variables
    if openai_input:
        os.environ["OPENAI_API_KEY"] = openai_input
    if serper_input:
        os.environ["SERPER_API_KEY"] = serper_input
    
    # Check if OpenAI API key is provided
    if not openai_input:
        st.error("⚠️ Please provide your OpenAI API Key in the sidebar to use the travel planner.")
        st.info("""
        To get your API keys:
        - **OpenAI API Key**: Visit https://platform.openai.com/api-keys
        - **Serper API Key** (Optional): Visit https://serper.dev/
        """)
        return
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📋 Travel Planning Form")
        
        # Travel details form
        with st.form("travel_form"):
            destination = st.text_input("🏖️ Destination", placeholder="e.g., Paris, France")
            
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input("📅 Start Date", value=datetime.now() + timedelta(days=30))
            with col_date2:
                end_date = st.date_input("📅 End Date", value=datetime.now() + timedelta(days=37))
            
            duration = (end_date - start_date).days
            st.info(f"Trip Duration: {duration} days")
            
            budget = st.number_input("💰 Budget (USD)", min_value=100, max_value=50000, value=2000, step=100)
            
            travel_style = st.selectbox(
                "🎒 Travel Style",
                ["Budget Backpacker", "Mid-range Explorer", "Luxury Traveler", "Business Traveler", "Family Vacation"]
            )
            
            preferences = st.text_area(
                "✨ Preferences & Interests",
                placeholder="e.g., love museums, enjoy local food, prefer walking tours, interested in history..."
            )
            
            submitted = st.form_submit_button("🚀 Plan My Trip", use_container_width=True)
    
    with col2:
        st.header("🤖 Your AI Travel Crew")
        
        agents_info = [
            ("🔍 Research Specialist", "Gathers comprehensive destination information"),
            ("📋 Itinerary Planner", "Creates optimized day-by-day schedules"),
            ("💵 Budget Analyst", "Analyzes costs and finds great deals"),
            ("🏛️ Local Expert", "Provides authentic cultural insights")
        ]
        
        for role, description in agents_info:
            st.markdown(f"""
            <div class="agent-card">
                <strong>{role}</strong><br>
                <small>{description}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Process the travel planning
    if submitted and destination and preferences:
        if duration <= 0:
            st.error("End date must be after start date!")
            return
            
        travel_details = {
            'destination': destination,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'duration': duration,
            'budget': budget,
            'travel_style': travel_style,
            'preferences': preferences
        }
        
        st.header("🎯 Planning Your Trip...")
        
        try:
            with st.spinner("Assembling your AI travel crew..."):
                # Create agents
                researcher, planner, budget_analyst, local_expert = create_travel_agents(serper_input)
                
                # Create tasks
                research_task, planning_task, budget_task, local_task = create_travel_tasks(
                    researcher, planner, budget_analyst, local_expert, travel_details
                )
            
            with st.spinner("AI agents are working on your travel plan..."):
                # Create and run the crew
                crew = Crew(
                    agents=[researcher, planner, budget_analyst, local_expert],
                    tasks=[research_task, planning_task, budget_task, local_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                # Execute the crew
                result = crew.kickoff()
            
            # Display results
            st.success("✅ Your travel plan is ready!")
            
            # Create tabs for different sections
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Itinerary", "💰 Budget", "🏛️ Local Insights", "🔍 Research"])
            
            with tab1:
                st.header("📋 Your Detailed Itinerary")
                st.markdown(planning_task.output.raw if hasattr(planning_task, 'output') else "Itinerary being generated...")
            
            with tab2:
                st.header("💰 Budget Analysis")
                st.markdown(budget_task.output.raw if hasattr(budget_task, 'output') else "Budget analysis being generated...")
            
            with tab3:
                st.header("🏛️ Local Insights & Culture")
                st.markdown(local_task.output.raw if hasattr(local_task, 'output') else "Local insights being generated...")
            
            with tab4:
                st.header("🔍 Destination Research")
                st.markdown(research_task.output.raw if hasattr(research_task, 'output') else "Research being compiled...")
            
            # Export options
            st.header("📤 Export Your Plan")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Download as Text"):
                    full_plan = f"""
TRAVEL PLAN FOR {destination.upper()}
{start_date} to {end_date} ({duration} days)
Budget: ${budget}

ITINERARY:
{planning_task.output.raw if hasattr(planning_task, 'output') else 'Generating...'}

BUDGET ANALYSIS:
{budget_task.output.raw if hasattr(budget_task, 'output') else 'Generating...'}

LOCAL INSIGHTS:
{local_task.output.raw if hasattr(local_task, 'output') else 'Generating...'}

RESEARCH:
{research_task.output.raw if hasattr(research_task, 'output') else 'Generating...'}
                    """
                    st.download_button(
                        label="Download Plan",
                        data=full_plan,
                        file_name=f"travel_plan_{destination.lower().replace(' ', '_')}_{start_date}.txt",
                        mime="text/plain"
                    )
            
            with col2:
                st.info("💡 Tip: Save this page or download your plan for offline reference!")
                
        except Exception as e:
            st.error(f"An error occurred while planning your trip: {str(e)}")
            st.info("Please check your API keys and try again.")

if __name__ == "__main__":
    main()