import streamlit as st
import os
# from dotenv import load_dotenv
# Load environment variables (only for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available in Streamlit Cloud, use Streamlit secrets instead
    pass
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Import required packages
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from typing_extensions import Literal
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from typing import Annotated
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from pydantic import SecretStr
from langchain_core.runnables import RunnableConfig

# Page configuration
st.set_page_config(
    page_title="AI Research & Chart Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .researcher-message {
        background-color: #f0f8ff;
        border-left-color: #4CAF50;
    }
    .chart-generator-message {
        background-color: #fff5f5;
        border-left-color: #FF6B6B;
    }
    .user-message {
        background-color: #f9f9f9;
        border-left-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_result' not in st.session_state:
    st.session_state.workflow_result = None
if 'chart_generated' not in st.session_state:
    st.session_state.chart_generated = False

@st.cache_resource
def initialize_workflow():
    """Initialize the workflow with proper configuration."""
    
    # Get API keys from environment or Streamlit secrets
    openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    tavily_api_key = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY", "")
    
    if not openai_api_key:
        st.error("❌ OpenAI API key not found! Please add it in Streamlit secrets or .env file")
        st.stop()
    
    # Set up LLM
    llm = ChatOpenAI(
        model="gpt-4.1-2025-04-14",
        api_key=SecretStr(openai_api_key) if openai_api_key else None,
        temperature=0.1
    )
    
    # Set up search tool
    if tavily_api_key:
        search_tool = TavilySearchResults(tavily_api_key=tavily_api_key)
    else:
        search_tool = DuckDuckGoSearchRun()
    
    # Set up Python REPL
    repl = PythonREPL()
    
    # Define Python REPL tool
    @tool
    def python_repl_tool(
        code: Annotated[str, "The python code to execute to generate your chart."],
    ):
        """Use this to execute python code. If you want to see the output of a value,
        you should print it out with `print(...)`. This is visible to the user."""
        
        try:
            # Enhanced code with matplotlib backend for Streamlit
            enhanced_code = f"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configure for better display
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100

{code}

# Check if plot was created and save
if plt.get_fignums():
    plt.savefig('generated_chart.png', bbox_inches='tight', dpi=150)
    print("Chart created and saved successfully!")
    chart_created = True
else:
    chart_created = False
    print("No chart was created.")
"""
            
            # Execute the enhanced code
            result = repl.run(enhanced_code)
            
            # Check if chart file was actually created
            if os.path.exists('generated_chart.png'):
                st.session_state.chart_generated = True
                # Display the chart immediately in Streamlit
                try:
                    import matplotlib.pyplot as plt
                    import matplotlib.image as mpimg
                    
                    # Read and display the saved image
                    img = mpimg.imread('generated_chart.png')
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.imshow(img)
                    ax.axis('off')
                    st.pyplot(fig)
                    plt.close('all')  # Clean up
                    
                except Exception as display_error:
                    st.warning(f"Chart saved but display failed: {display_error}")
            else:
                st.session_state.chart_generated = False
                
            return f"Successfully executed:\n```python\n{code}\n```\nOutput: {result}\n\nIf you have completed all tasks, respond with FINAL ANSWER."
            
        except Exception as e:
            return f"Failed to execute. Error: {repr(e)}"
    
    # System prompt function
    def make_system_prompt(instruction: str) -> str:
        return (
            "You are a helpful AI assistant, collaborating with other assistants."
            " Use the provided tools to progress towards answering the question."
            " If you are unable to fully answer, that's OK, another assistant with different tools "
            " will help where you left off. Execute what you can to make progress."
            " If you or any of the other assistants have the final answer or deliverable,"
            " prefix your response with FINAL ANSWER so the team knows to stop."
            f"\n{instruction}"
        )
    
    # Node routing function
    def get_next_node(last_message: BaseMessage, goto: str):
        if "FINAL ANSWER" in last_message.content:
            return END
        return goto
    
    # Agent 1: Research Node
    def research_node(state: MessagesState) -> Command:
        research_agent = create_react_agent(
            llm,
            tools=[search_tool],
            prompt=make_system_prompt(
                """You can only do research. You are working with a chart generator colleague.
                Your job is to:
                1. Search for the requested data
                2. Gather specific numerical data, statistics, or information needed
                3. Present the data in a clear, structured format
                4. Do NOT attempt to create charts yourself
                
                When you have sufficient data, clearly indicate that your chart_generator 
                colleague should take over to create the visualization."""
            ), 
        )
        
        result = research_agent.invoke(state)
        goto = get_next_node(result["messages"][-1], "chart_generator")
        result["messages"][-1] = HumanMessage(
            content=result["messages"][-1].content, 
            name="researcher"
        )
        return Command(update={"messages": result["messages"]}, goto=goto)
    
    # Agent 2: Chart Generator Node
    def chart_node(state: MessagesState) -> Command:
        chart_agent = create_react_agent(
            llm,
            tools=[python_repl_tool],
            prompt=make_system_prompt(
                """You can only generate charts. You are working with a researcher colleague.
                Your job is to:
                1. Take the data provided by the researcher
                2. Create the requested visualization using matplotlib
                3. Use proper labels, titles, and formatting
                4. Once the chart is created successfully, respond with FINAL ANSWER
                
                Available libraries: matplotlib, pandas, numpy, seaborn
                IMPORTANT: Always include plt.show() at the end of your code to ensure the chart is displayed.
                
                Do NOT search for additional data - use what the researcher provided.
                
                Example chart code structure:
                ```python
                # Your data processing here
                plt.figure(figsize=(12, 8))
                # Your plotting code here
                plt.title('Your Chart Title')
                plt.xlabel('X Label')
                plt.ylabel('Y Label')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.show()  # This is essential for display
                ```"""
            ),
        )
        
        result = chart_agent.invoke(state)
        goto = get_next_node(result["messages"][-1], "researcher")
        result["messages"][-1] = HumanMessage(
            content=result["messages"][-1].content, 
            name="chart_generator"
        )
        return Command(update={"messages": result["messages"]}, goto=goto)
    
    # Build the workflow
    workflow = StateGraph(MessagesState)
    workflow.add_node("researcher", research_node)
    workflow.add_node("chart_generator", chart_node)
    workflow.add_edge(START, "researcher")
    
    # Compile the workflow
    app = workflow.compile()
    
    return app

def display_conversation(messages):
    """Display the conversation in a nice format."""
    for i, msg in enumerate(messages):
        if hasattr(msg, 'name') and msg.name:
            if msg.name == "researcher":
                st.markdown(f"""
                <div class="chat-message researcher-message">
                    <strong>🔍 RESEARCHER:</strong><br>
                    {msg.content}
                </div>
                """, unsafe_allow_html=True)
            elif msg.name == "chart_generator":
                st.markdown(f"""
                <div class="chat-message chart-generator-message">
                    <strong>📊 CHART GENERATOR:</strong><br>
                    {msg.content}
                </div>
                """, unsafe_allow_html=True)
        elif i == 0:  # User message
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 USER:</strong><br>
                {msg.content}
            </div>
            """, unsafe_allow_html=True)

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Research & Chart Generator</h1>
        <p>Multi-Agent System for Intelligent Data Research and Visualization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 How it works")
        st.markdown("""
        1. **🔍 Research Agent**: Searches for data online
        2. **📊 Chart Generator**: Creates visualizations
        3. **🤝 Collaboration**: Agents work together seamlessly
        """)
        
        st.header("💡 Example Queries")
        example_queries = [
            "Show me top 10 most populated countries with a bar chart",
            "What is UK's GDP in past 3 years, draw line chart",
            "Create a line chart of Bitcoin price trend in last 6 months",
            "IPL winners in last 5 years with their final match scores",
            "Global temperature trends in last decade visualization"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query[:30]}...", key=query, use_container_width=True):
                st.session_state.selected_query = query
    
    # Initialize workflow
    try:
        app = initialize_workflow()
        st.success("✅ Multi-Agent System Initialized Successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize: {str(e)}")
        st.stop()
    
    # Main input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input(
            "🎯 What would you like to research and visualize?",
            value=st.session_state.get('selected_query', ''),
            placeholder="e.g., Show me top 10 most populated countries with a bar chart"
        )
    
    with col2:
        recursion_limit = st.number_input("Max Steps", min_value=5, max_value=25, value=15)
    
    # Generate button
    if st.button("🚀 Generate Research & Chart", type="primary", use_container_width=True):
        if user_query:
            st.session_state.chart_generated = False
            
            with st.spinner("🤖 Agents are working together..."):
                try:
                    config: RunnableConfig = {"recursion_limit": recursion_limit}
                    result = app.invoke(
                        {"messages": [("user", user_query)]},
                        config=config
                    )
                    st.session_state.workflow_result = result
                    
                except Exception as e:
                    st.error(f"❌ Error during execution: {str(e)}")
                    st.exception(e)
        else:
            st.warning("⚠️ Please enter a query!")
    
    # Display results
    if st.session_state.workflow_result:
        st.header("🗣️ Agent Conversation")
        
        with st.expander("View Full Conversation", expanded=True):
            display_conversation(st.session_state.workflow_result["messages"])
        
        # Check for generated chart file
        chart_path = "generated_chart.png"
        if os.path.exists(chart_path):
            st.success("🎉 Chart generated successfully!")
            st.image(chart_path, caption="Generated Chart", use_column_width=True)
            st.session_state.chart_generated = True
            
            # Download option
            with open(chart_path, "rb") as file:
                st.download_button(
                    label="📥 Download Chart",
                    data=file.read(),
                    file_name="ai_generated_chart.png",
                    mime="image/png"
                )
        elif st.session_state.chart_generated:
            st.warning("⚠️ Chart was generated but file not found.")
        else:
            st.info("ℹ️ No chart generated yet or agents are still working.")

if __name__ == "__main__":
    main()