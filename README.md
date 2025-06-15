🌍 AI Travel Planner
A powerful Streamlit application that uses CrewAI to plan personalized travel itineraries with multiple AI agents working together.

Features
🔍 Research Agent: Gathers comprehensive destination information
📋 Planning Agent: Creates optimized day-by-day itineraries
💰 Budget Agent: Analyzes costs and provides budget breakdowns
🏛️ Local Expert: Provides authentic cultural insights and insider tips
Demo
Show Image

Quick Start
Prerequisites
Python 3.8+
OpenAI API Key (Get one here)
Serper API Key (Optional, for web search - Get one here)
Installation
Clone the repository:
bash
git clone https://github.com/yourusername/ai-travel-planner.git
cd ai-travel-planner
Install dependencies:
bash
pip install -r requirements.txt
Set up environment variables:
bash
# Create a .env file or set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export SERPER_API_KEY="your-serper-api-key"  # Optional
Run the application:
bash
streamlit run app.py
Configuration
API Keys
The app requires an OpenAI API key to function. You can provide it in several ways:

Through the UI: Enter your API key in the sidebar
Environment Variable: Set OPENAI_API_KEY
Streamlit Secrets: Add to .streamlit/secrets.toml (for deployment)
Optional: Serper API Key
For enhanced research capabilities with real-time web search, add your Serper API key:

Get it from serper.dev
Add as SERPER_API_KEY environment variable
Usage
Enter Travel Details: Destination, dates, budget, travel style
Specify Preferences: Interests, activities, food preferences, etc.
Click "Plan My Trip": AI agents will collaborate to create your plan
Review Results: Detailed itinerary, budget analysis, local insights
Export: Download your complete travel plan
Project Structure
ai-travel-planner/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
└── .streamlit/
    └── secrets.toml     # Streamlit secrets (for deployment)
Deployment on Streamlit Community Cloud
Push your code to GitHub
Go to share.streamlit.io
Connect your GitHub repository
Add secrets in the Streamlit dashboard:
OPENAI_API_KEY = your OpenAI API key
SERPER_API_KEY = your Serper API key (optional)
Deploy!
Features in Detail
🔍 Research Agent
Destination information and attractions
Weather and seasonal considerations
Transportation options
Safety and visa requirements
📋 Planning Agent
Day-by-day detailed itineraries
Optimized routing and timing
Activity recommendations
Weather contingency plans
💰 Budget Agent
Detailed cost breakdowns
Money-saving recommendations
Daily spending estimates
Payment and currency tips
🏛️ Local Expert
Cultural customs and etiquette
Authentic local experiences
Hidden gems and insider tips
Local food recommendations
Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
License
This project is licensed under the MIT License - see the LICENSE file for details.

Support
If you encounter any issues or have questions:

Open an issue on GitHub
Check the Streamlit documentation
Review CrewAI documentation
Acknowledgments
Built with Streamlit
Powered by CrewAI
Uses OpenAI's GPT models
Web search via Serper API
