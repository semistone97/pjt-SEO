from langgraph.graph import START, StateGraph
from src.nodes import keyword_process
from src.classes import State

def build_graph():
    builder = StateGraph(State).add_node("keyword_process", keyword_process)
    builder.add_edge(START, "keyword_process")
    return builder.compile()