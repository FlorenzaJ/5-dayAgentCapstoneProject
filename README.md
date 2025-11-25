# 5-dayAgentCapstoneProject

------------------------------------------------------------
# 1. The Pitch: Problem, Solution, and Value 
------------------------------------------------------------
# Problem Statement
In a fast-paced development environment, new features, bug fixes, and process changes are tracked via internal tickets (e.g., Jira, Trello). The burden of manually drafting, formatting, and publishing corresponding FAQ entries causes documentation to become outdated, leading to:
1. Increased support costs (employees wasting time searching for answers).
2. Delayed rollouts due to quality assurance bottlenecks.
3. Risk of non-compliance if critical policy updates are missed.🎯 
    
# Solution & Core Concept
The Wiki-Genie Agent System solves this by creating a structured, multi-step pipeline that automates content creation with mandatory Human-in-the-Loop (HITL) governance.

The agent's workflow ingests raw ticket data, intelligently drafts a technical document, and pauses for human approval before publishing.

# Value Proposition
The Wiki-Genie Agent provides quantifiable value by:
1. Time Savings: Reducing the time spent by engineers and technical writers on manual drafting and formatting by an estimated 70%.
2. Quality & Compliance: Ensuring all published content adheres to internal style guides and is vetted by a human reviewer before deployment.

------------------------------------------------------------
# 2. Implementation and Architecture 
------------------------------------------------------------
# System Architecture
The Wiki-Genie uses a Sequential Multi-Agent Pipeline to ensure a high-quality, controlled output. The process relies on a shared AgentState for state management across all nodes.

# Required Course Concepts Applied
This project demonstrates proficiency in five (5) key agentic concepts from the course:

1. Multi-Agent System (Sequential): Three distinct agents (monitor, writer, reviewer/publisher) execute in a fixed linear order, passing the state between them.

2. Long-Running Operations: The Human Reviewer node explicitly pauses the LangGraph execution using an input() prompt, simulating a critical HITL checkpoint that waits indefinitely for approval before resuming.

3. Context Engineering: The Ticket Monitor agent injects pre-defined rules (Style Guide, Existing Entry Summary) directly into the prompt given to the Draft Writer, controlling the LLM's tone and avoiding content redundancy.

4. Tools (Custom Tool): A custom Python function, check_draft_format, is integrated as a tool. The writer's logic is implicitly guided by this tool to ensure the final output contains all required document headers (e.g., ### Overview).

5. Conditional Routing / Agent Evaluation: The workflow uses a conditional edge following the Human Reviewer. If the status is REJECTED, the graph loops the state back to the Draft Writer for a revision cycle.

------------------------------------------------------------
# III. Execution and Demo
------------------------------------------------------------
Prerequisites
Python: Python 3.10+
Libraries: pip install langgraph langchain-google-genai langchain-core
API Key: Set your Gemini API key in the os.environ line of the agent.py file.

Demonstration of the Workflow
The agent successfully handles a full cycle, including a conditional loop (Test #2 below):
1. Agent Start: The user provides the raw content (e.g., a ticket summary).
2. Drafting: The Draft Writer produces the formatted Markdown entry.
3. HITL Pause: The Human Reviewer pauses the workflow and displays the draft.
4. Conditional Routing:
    - User Enters REJECTED: 
    The graph loops back to the Draft Writer node for revision.
    - User Enters APPROVED: 
    The graph proceeds to the Final Publisher.
5. Publishing: The agent saves the final, clean content to the mock file published_faq.md.

# Final Artifact
The final successful entry generated and published by the agent:
1. File: published_faq.md
2. Content: (A large, cleanly formatted Markdown entry on the new feature, complete with the required ### Overview section.)
