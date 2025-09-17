from langgraph.graph import START, END, StateGraph
from src.nodes import keyword_process
from src.states import State
from src.nodes_sems import generate_relevance, select_top_keywords
from src.listing_nodes import keyword_distribute, generate_title, generate_bp, generate_description
from dotenv import load_dotenv

load_dotenv()


def build_graph():
    builder = StateGraph(State)
    builder.add_sequence([keyword_process, generate_relevance, select_top_keywords, keyword_distribute, generate_title, generate_bp, generate_description])

    builder.add_edge(START, "keyword_process")
    builder.add_edge('select_top_keywords', END)
    
    return builder.compile()