## AI-Agents

# 📚 AI Research Assistant (Google ADK)

A multi-agent AI research system built using Google ADK that generates structured research reports through a workflow of planning, validation, and writing agents.

## 🏗️ Architecture

```text
User Input (Topic)
→ Research Planner
→ Plan Validator
→ Research Writer
→ Report Validator
→ Final Research Report
```

## 📁 Project Structure

```text
research_assistant/
│
├── agent.py              # Main ADK agent (workflow + root agent)
├── .env                  # Environment variables
├── requirements.txt      # Dependencies
└── README.md             # Project documentation
```

##  🔧 Tech Stack
1. Google ADK
2. Gemini Models
3. Python 3.10+
4. dotenv

