import streamlit as st
import openai
import os
import requests
import json

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
    .step-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: #f9f9f9;
    }
    .research-box {
        background-color: #f0f8ff;
        border-left-color: #4CAF50;
    }
    .code-box {
        background-color: #fff5f5;
        border-left-color: #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_data' not in st.session_state:
    st.session_state.research_data = None
if 'chart_code' not in st.session_state:
    st.session_state.chart_code = None

def search_duckduckgo(query, max_results=5):
    """Simple DuckDuckGo search function"""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    'title': r.get('title', ''),
                    'body': r.get('body', ''),
                    'href': r.get('href', '')
                })
            return results
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

def call_openai(messages, temperature=0.1):
    """Call OpenAI API"""
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
        if not openai_api_key:
            st.error("❌ OpenAI API key not found!")
            return None
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=messages,
            temperature=temperature,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return None

def research_agent(query):
    """Research agent that searches for data"""
    st.markdown("""
    <div class="step-box research-box">
        <h3>🔍 RESEARCH AGENT WORKING...</h3>
        <p>Searching for data related to your query...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search for information
    search_results = search_duckduckgo(query, max_results=3)
    
    if not search_results:
        return "No search results found. Please try a different query."
    
    # Prepare context for OpenAI
    search_context = "\n\n".join([
        f"Title: {r['title']}\nContent: {r['body'][:500]}..."
        for r in search_results
    ])
    
    messages = [
        {
            "role": "system",
            "content": """You are a research specialist. Your job is to:
            1. Analyze the search results provided
            2. Extract specific numerical data, statistics, or relevant information
            3. Present the data in a clear, structured format
            4. Focus on data that can be visualized in charts
            
            Present your findings in a clear format with specific numbers, dates, and sources when available."""
        },
        {
            "role": "user",
            "content": f"Query: {query}\n\nSearch Results:\n{search_context}\n\nPlease extract and organize the relevant data for visualization."
        }
    ]
    
    response = call_openai(messages)
    return response

def chart_generator_agent(research_data, original_query):
    """Chart generator that creates Python code"""
    st.markdown("""
    <div class="step-box code-box">
        <h3>📊 CHART GENERATOR WORKING...</h3>
        <p>Creating Python code for your visualization...</p>
    </div>
    """, unsafe_allow_html=True)
    
    messages = [
        {
            "role": "system",
            "content": """You are a data visualization specialist. Your job is to:
            1. Take the research data provided
            2. Create complete, runnable Python code using matplotlib
            3. Generate professional charts with proper labels, titles, and formatting
            4. Include all necessary imports and data setup
            
            Always create complete code that users can copy and run locally. Include:
            - All necessary imports (matplotlib.pyplot, pandas, numpy if needed)
            - Data setup from the research
            - Chart creation with proper styling
            - Labels, titles, legends, and grid
            - plt.show() at the end
            
            Choose the appropriate chart type based on the data and query."""
        },
        {
            "role": "user",
            "content": f"Original Query: {original_query}\n\nResearch Data:\n{research_data}\n\nPlease create complete Python code for visualization."
        }
    ]
    
    response = call_openai(messages)
    return response

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Research & Chart Generator</h1>
        <p>AI-Powered Data Research and Visualization Code Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 How it works")
        st.markdown("""
        1. **🔍 Research**: AI searches for your data online
        2. **📊 Generate**: AI creates Python chart code
        3. **📝 Copy**: Copy the code to run locally
        """)
        
        st.header("💡 Example Queries")
        example_queries = [
            "Top 10 most populated countries bar chart",
            "UK GDP past 3 years line chart",
            "Bitcoin price trend last 6 months",
            "Global temperature trends decade",
            "IPL winners last 5 years scores"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query}", key=query, use_container_width=True):
                st.session_state.selected_query = query
    
    # Check API key
    openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    if not openai_api_key:
        st.error("❌ OpenAI API key not found! Please add it in Streamlit secrets.")
        st.stop()
    else:
        st.success("✅ AI System Ready!")
    
    # Main input
    user_query = st.text_input(
        "🎯 What would you like to research and visualize?",
        value=st.session_state.get('selected_query', ''),
        placeholder="e.g., Show me top 10 most populated countries with a bar chart"
    )
    
    # Generate button
    if st.button("🚀 Generate Research & Chart Code", type="primary", use_container_width=True):
        if user_query:
            # Reset session state
            st.session_state.research_data = None
            st.session_state.chart_code = None
            
            # Step 1: Research
            with st.spinner("🔍 Researching data..."):
                research_data = research_agent(user_query)
                st.session_state.research_data = research_data
            
            if research_data:
                # Display research results
                st.markdown("""
                <div class="step-box research-box">
                    <h3>🔍 Research Results</h3>
                </div>
                """, unsafe_allow_html=True)
                st.write(research_data)
                
                # Step 2: Generate chart code
                with st.spinner("📊 Generating chart code..."):
                    chart_code = chart_generator_agent(research_data, user_query)
                    st.session_state.chart_code = chart_code
                
                if chart_code:
                    # Display chart code
                    st.markdown("""
                    <div class="step-box code-box">
                        <h3>📊 Generated Chart Code</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.code(chart_code, language='python')
                    
                    st.success("🎉 Chart code generated successfully!")
                    st.info("💡 Copy the code above and run it in your local Python environment with matplotlib installed.")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Python Code",
                        data=chart_code,
                        file_name=f"chart_code_{user_query[:20].replace(' ', '_')}.py",
                        mime="text/plain"
                    )
        else:
            st.warning("⚠️ Please enter a query!")
    
    # Display previous results if available
    if st.session_state.research_data and st.session_state.chart_code:
        st.markdown("---")
        st.header("📋 Previous Results")
        
        with st.expander("View Research Data", expanded=False):
            st.write(st.session_state.research_data)
        
        with st.expander("View Chart Code", expanded=False):
            st.code(st.session_state.chart_code, language='python')

if __name__ == "__main__":
    main()
