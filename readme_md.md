# 🤖 AI Research & Chart Generator

A multi-agent system powered by LangGraph that combines intelligent research and data visualization. Two AI agents collaborate to find data and create beautiful charts automatically.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![LangChain](https://img.shields.io/badge/langchain-latest-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

- **🔍 Research Agent**: Automatically searches for data using Tavily or DuckDuckGo
- **📊 Chart Generator**: Creates professional visualizations with matplotlib
- **🤝 Multi-Agent Collaboration**: Two AI agents work together seamlessly
- **🎨 Beautiful UI**: Streamlit interface with custom styling
- **📱 Responsive Design**: Works on desktop and mobile
- **⚡ Real-time Processing**: See agents collaborate in real-time

## 🛠️ Architecture

```
User Query → Research Agent → Chart Generator → Final Visualization
     ↑              ↓              ↓              ↓
   Input        Web Search    Python Code    Chart Display
```

### Agents:
1. **Research Agent**: Uses search tools to find relevant data
2. **Chart Generator**: Uses Python REPL to create visualizations

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Tavily API key (optional, will use DuckDuckGo as fallback)

## 🔧 Installation

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-research-chart-generator.git
cd ai-research-chart-generator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Run the application**
```bash
streamlit run app.py
```

### 🌐 Streamlit Cloud Deployment

1. **Fork this repository** to your GitHub account

2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**

3. **Click "New app"** and connect your GitHub repository

4. **Set up secrets** in Streamlit Cloud:
   - Go to your app settings
   - Add these secrets:
     ```toml
     OPENAI_API_KEY = "your_openai_api_key_here"
     TAVILY_API_KEY = "your_tavily_api_key_here"  # Optional
     ```

5. **Deploy**: Click "Deploy" and your app will be live!

## 🎯 Usage Examples

### Example Queries You Can Try:

- `"Show me top 10 most populated countries with a bar chart"`
- `"What is UK's GDP in past 3 years, draw line chart"`
- `"Create a line chart of Bitcoin price trend in last 6 months"`
- `"IPL winners in last 5 years with their final match scores"`
- `"Global temperature trends in last decade visualization"`

### How It Works:

1. **Enter your query** in the text input
2. **Click "Generate Research & Chart"**
3. **Watch the agents collaborate**:
   - Research Agent searches for data
   - Chart Generator creates visualization
4. **View the results** and download the chart

## 🔑 API Keys Setup

### OpenAI API Key (Required)
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and navigate to API keys
3. Create a new API key
4. Add it to your `.env` file or Streamlit secrets

### Tavily API Key (Optional)
1. Visit [Tavily](https://tavily.com/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add it to your `.env` file or Streamlit secrets

*Note: If Tavily is not available, the app will automatically fallback to DuckDuckGo search.*

## 📁 Project Structure

```
ai-research-chart-generator/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # Project documentation
├── .gitignore           # Git ignore file
└── generated_charts/    # Folder for saved charts (created automatically)
```

## 🔧 Configuration

### Recursion Limit
- Default: 15 steps
- Range: 5-25 steps
- Higher values allow more complex research but take longer

### Supported Chart Types
- Line charts (time series, trends)
- Bar charts (comparisons, rankings)
- Scatter plots (relationships)
- Histograms (distributions)
- Pie charts (proportions)

## 🐛 Troubleshooting

### Common Issues:

1. **"OpenAI API key not found"**
   - Make sure your API key is correctly set in `.env` or Streamlit secrets
   - Check that the key is valid and has sufficient credits

2. **"Search tool error"**
   - If Tavily fails, the app will automatically use DuckDuckGo
   - Check your internet connection

3. **"Chart not generating"**
   - The chart generator needs specific numerical data
   - Try rephrasing your query to be more specific

4. **"Recursion limit reached"**
   - Increase the "Max Steps" value
   - Simplify your query

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the amazing framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) for multi-agent orchestration
- [Streamlit](https://streamlit.io/) for the beautiful web interface
- [OpenAI](https://openai.com/) for the powerful language models
- [Tavily](https://tavily.com/) for the search API

## 📊 Live Demo

🌐 **[Try the live demo here!](https://your-app-name.streamlit.app)**

---

⭐ **If you find this project helpful, please give it a star!**

## 🔗 Connect

- 📧 Email: your.email@example.com
- 💼 LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- 🐦 Twitter: [@YourTwitter](https://twitter.com/yourhandle)
