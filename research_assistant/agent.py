import os
import datetime

from dotenv import load_dotenv
from google.adk.agents import Agent, LoopAgent
from google.adk.tools import agent_tool

# ------------------------------------------------------------------
# ENV
# ------------------------------------------------------------------

load_dotenv()

MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# ------------------------------------------------------------------
# SESSION KEYS (centralized state management)
# ------------------------------------------------------------------

STATE_TOPIC = "topic"
STATE_OUTLINE = "research_outline"
STATE_REPORT = "research_report"

# ------------------------------------------------------------------
# PLANNER AGENT
# ------------------------------------------------------------------

research_planner = Agent(
    name="ResearchPlanner",
    model=MODEL,
    description="Creates research plan from session topic.",
    instruction=f"""
You are a research planner.

Use session state:
- Topic: {{{STATE_TOPIC}}}

Create a structured Markdown research outline:

Include:
- Title
- Objective
- Key Questions
- Topics to Investigate
- Important Concepts
- Suggested Sources
- Expected Outcome

Store result in: {STATE_OUTLINE}

Return ONLY Markdown.
""",
    output_key=STATE_OUTLINE,
)

# ------------------------------------------------------------------
# PLAN VALIDATOR
# ------------------------------------------------------------------

class ResearchPlanValidator(Agent):
    def __init__(self):
        super().__init__(
            name="ResearchPlanValidator",
            model=MODEL,
            description="Validates research plan.",
            instruction=f"""
Check {STATE_OUTLINE} in session state.

Ensure it has:
- Title
- Objective
- Questions
- Topics
- Sources
- Outcome

If valid return: ok
Else return: retry + missing parts
""",
            output_key="validation_result",
        )

robust_planner = LoopAgent(
    name="RobustPlanner",
    description="Retries until valid research plan is generated.",
    sub_agents=[
        research_planner,
        ResearchPlanValidator(),
    ],
    max_iterations=3,
)

# ------------------------------------------------------------------
# WRITER AGENT
# ------------------------------------------------------------------

research_writer = Agent(
    name="ResearchWriter",
    model=MODEL,
    description="Writes research report from outline.",
    instruction=f"""
Use session state:
- Outline: {{{STATE_OUTLINE}}}

Write a detailed Markdown report:

Include:
- Title
- Executive Summary
- Background
- Analysis
- Key Findings
- Applications
- Conclusion

Store output in: {STATE_REPORT}

Return ONLY Markdown.
""",
    output_key=STATE_REPORT,
)

# ------------------------------------------------------------------
# REPORT VALIDATOR
# ------------------------------------------------------------------

class ResearchReportValidator(Agent):
    def __init__(self):
        super().__init__(
            name="ResearchReportValidator",
            model=MODEL,
            description="Validates research report.",
            instruction=f"""
Validate {STATE_REPORT}.

Must include:
- Executive Summary
- Background
- Analysis
- Findings
- Applications
- Conclusion

Return:
ok OR retry + fixes
""",
            output_key="validation_result",
        )

robust_writer = LoopAgent(
    name="RobustWriter",
    description="Retries until report is valid.",
    sub_agents=[
        research_writer,
        ResearchReportValidator(),
    ],
    max_iterations=3,
)

# ------------------------------------------------------------------
# TOOLS
# ------------------------------------------------------------------

planner_tool = agent_tool.AgentTool(agent=robust_planner)
writer_tool = agent_tool.AgentTool(agent=robust_writer)

# ------------------------------------------------------------------
# ROOT AGENT (SESSION CONTROLLER)
# ------------------------------------------------------------------

root_agent = Agent(
    name="ResearchAssistant",
    model=MODEL,
    description="Session-based AI Research Assistant.",
    instruction=f"""
You are a research assistant with session memory.

FIRST MESSAGE:
- Ask: "What topic would you like me to research?"

WHEN USER PROVIDES TOPIC:
1. Save it in session state as '{STATE_TOPIC}'
2. Call planner tool
3. Call writer tool
4. Return final report

FINAL OUTPUT:
- Research report
- 5 key takeaways
- 3 follow-up research questions

Date: {datetime.datetime.now().strftime("%Y-%m-%d")}
""",
    tools=[
        planner_tool,
        writer_tool,
    ],
)