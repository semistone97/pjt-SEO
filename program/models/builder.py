from langgraph.graph import START, END, StateGraph
from models.nodes_keyword import keyword_process
from schemas.states import State
from models.nodes_relevance import generate_relevance, select_top_keywords
from models.nodes_listing import keyword_distribute, generate_title, generate_bp, generate_description
from dotenv import load_dotenv

load_dotenv()


def build_graph():
    builder = StateGraph(State)
    builder.add_sequence([keyword_process, generate_relevance, select_top_keywords, keyword_distribute, generate_title, generate_bp, generate_description])

    builder.add_edge(START, "keyword_process")
    builder.add_edge('generate_description', END)
    
    return builder.compile()