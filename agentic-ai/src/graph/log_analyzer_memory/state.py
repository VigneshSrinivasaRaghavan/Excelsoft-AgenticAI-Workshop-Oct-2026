"""
Log Analyzer - State Definition
"""
from typing import TypedDict, Dict, List

class LogAnalyzerState(TypedDict):
    """State for log analysis pipeline."""
    log_content: str
    user_instruction: str             # follow-up instruction typed in the driver loop
    conversation_history: List[Dict]  # STM — restored by MemorySaver between invocations
    past_incidents: str               # LTM — retrieved from ChromaDB at session start
    retrieved_context: str
    analysis_text: str
    analysis_json: Dict
    executive_summary: str
    errors: List[str]
