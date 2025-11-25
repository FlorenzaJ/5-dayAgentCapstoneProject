import os
import time
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from operator import add

os.environ["GEMINI_API_KEY"] = "API_KEY_HERE"
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

class AgentState(TypedDict):
    """
    Shared memory/state passed between all agents/nodes. (Sessions & Memory)
    """
    ticket_details: str
    draft_output: str
    review_status: str
    context_data: str

#Mock External System
MOCK_KNOWLEDGE_BASE = {
    "style_guide": "The tone must be professional. Use Markdown format. All entries must have a '### Overview' section.",
    "existing_entry_summary": "Existing entry covers password reset. This enw entry should focus on 2FA setup.",
}

#Custom Tools
@tool
def check_draft_format(draft_content: str) -> str:
    """
    Checks if the draft content follow the basic formatiing rules (must contin '### Overview' and use Markdown syntax). Returns 'PASS' or 'FAIL'.
    """
    if '### Overview' not in draft_content:
        return "FAIL: Draft must include '### Overview' section. Please correct the formatting."
    return "PASS: Formatting check successful."
    
llm_with_tool = llm.bind_tools([check_draft_format])

#----- Multi-Agent System -----
def ticket_monitor(state: AgentState) -> AgentState:
    """Agent 1: Ingests the ticket and injects Context Engineering data."""
    print("--- 1. TICKET MONITOR: Ingesting Ticket and Context ---")

    #Context Engineering
    context = (
        f"KNOWLEDGE BASE STYLE GUIDE: {MOCK_KNOWLEDGE_BASE['style_guide']}\n"
        f"EXISTING ENTRIES SUMMARY: {MOCK_KNOWLEDGE_BASE['existing_entry_summary']}"
    )

    new_state = state.copy()
    new_state['ticket_details'] = state['ticket_details']
    new_state['context_data'] = context

    print(f"✅ Context Injected. Input Content Length: {len(new_state['ticket_details'])}")
    return new_state

def draft_writer(state: AgentState) -> AgentState:
    """Agent 2: Drafts the FAQ entry and calls the Custom Tool."""
    print("\n--- 2. DRAFT WRITER: Drafting and Formatting Check ---")

    draft_prompt = f"""
    You are the Wiki-Genie Draft Writer. Convert the Ticket Details into a formatted FAQ entry.

    KNOWLEDGE BASE CONTEXT: {state['context_data']}
    TICKET DETAILS: {state['ticket_details']}
    """

    #LLM generates the draft
    response = llm.invoke([HumanMessage(content=draft_prompt)])

    new_state = state.copy()
    new_state['draft_output'] = response.content
    print(f"✅ Drafted and stored {len(response.content)} characters of content.")

    #Agent Evaluation
    format_check_result = check_draft_format.invoke({"draft_content": response.content})
    print(f"🔬 Format Check Result: {format_check_result}")

    return new_state

def human_reviewer(state: AgentState) -> AgentState:
    """
    Agent 3: Manages the human-in-the-loop logic. (Long-Running Operation)
    """
    print("\n--- 3. HUMAN REVIEWER: Waiting for Approval (Long-Running Operation)")

    #Display draft
    print("\n\n-------------------------------------")
    print("DRAFT FOR REVIEW:")
    print("-------------------------------------")
    print(state['draft_output'])
    print("-------------------------------------")

    #Simulate PAUSE and WAIT (Human-in-the-loop)
    print("\n⚠️ WORKFLOW PAUSED: Waiting for human input ('APPROVED' or 'rejected')...")
    review = input("Enter status ('APPROVED' or 'REJECTED'): ").upper().strip()

    new_state = state.copy()
    new_state['review_status'] = review
    return new_state

def route_to_publish(state: AgentState):
    """
    Routing function based on review status. (Agent Evaluation / Conditional Flow)
    """
    if state['review_status'] == "APPROVED":
        return "publish"
    elif state["review_status"] == "REJECTED":
        return "draft_writer"
    return END

def final_publisher(state: AgentState) -> AgentState:
    """Simulated the final pubishing step."""
    print("\n--- 4. FINAL PUBLISHER: Deploying ---")
    print(f"✅ DRAFT APPROVED! Entry published to a mock file.")

    #Observability: Logging the final action
    with open("published_faq.md", "a") as f:
        f.write("\n\n--- NEW ENTRY START ---\n\n") # Add a separator
        f.write(state['draft_output'])
    return state

# LANGGRAPH ORCHESTRATION
workflow = StateGraph(AgentState)

#Adding Sequential nodes
workflow.add_node("monitor", ticket_monitor)
workflow.add_node("draft_writer", draft_writer)
workflow.add_node("reviewer", human_reviewer)
workflow.add_node("publisher", final_publisher)

#Defining edges
workflow.set_entry_point("monitor")
workflow.add_edge("monitor", "draft_writer")
workflow.add_edge("draft_writer", "reviewer")

#Conditional Routing
workflow.add_conditional_edges(
    "reviewer",
    route_to_publish,
    {
        "publish": "publisher",
        "draft_writer": "draft_writer",
        END: END
    }
)

workflow.add_edge("publisher", END)

#Compile and Run
app = workflow.compile()

print("==============================================")
print("     CAPSTONE PROJECT: WIKI-GENIE AGENT")
print("==============================================")

# Run the workflow
def run_agent_workflow():
    print("\n==============================================")
    print("      WIKI-GENIE: NEW DOCUMENT SUBMISSION")
    print("==============================================")

    #Collecting initial content from user.
    #In published app, this would be a file upload.
    print("Please paste the content (e.g., ticket summary, draft) you want the agent to process.")
    print("Press Ctrl+D or Ctrl+Z then Enter when finished.")

    initial_content = input("> ")

    if not initial_content:
        print("❌ Error: No content provided. Exiting.")
        return

    #Setting initial state with user's content
    initial_state = AgentState(
        ticket_details=initial_content,
        draft_output="",
        review_status="",
        context_data=""
    )

    #Running the workflow
    final_state = app.invoke(initial_state)

    print("\n==============================================")
    print(f"WORKFLOW COMPLETED. Final Status: {final_state['review_status']}")
    print("==============================================")

if __name__ == "__main__":
    run_agent_workflow()