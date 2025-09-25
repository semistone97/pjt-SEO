from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from schemas.global_state import State
from models.node_preprocess import keyword_preprocess, relevance_categorize, select_keywords, information_refine
from models.node_listing import keyword_distribute, generate_title, generate_bp, generate_description, listing_verificate
from models.node_feedback import user_input, parse_user_feedback, feedback_check
from models.node_regenerate import regenerate_title, regenerate_bp, regenerate_description

from graph.router import status_router, feedback_router, no_pdf_router

load_dotenv()

def build_graph():
    builder = StateGraph(State)
    
    # 키워드 분배
    builder.add_sequence([keyword_preprocess, relevance_categorize, select_keywords])
    builder.add_node('information_refine', information_refine)
    
    # 초안 작성
    builder.add_edge("select_keywords", "keyword_distribute")
    builder.add_sequence([keyword_distribute, generate_title, generate_bp, generate_description])
    builder.add_node('listing_verificate', listing_verificate)

    # 사용자 피드백
    builder.add_node('user_input', user_input)
    builder.add_node('parse_user_feedback', parse_user_feedback)
    builder.add_node('feedback_check', feedback_check)

    # 재생성 노드
    builder.add_node('regenerate_title', regenerate_title)
    builder.add_node('regenerate_bp', regenerate_bp)
    builder.add_node('regenerate_description', regenerate_description)
    
    # ====================================================================================================
    # 연결
   
    builder.add_conditional_edges(
        START,
        no_pdf_router,
        {
            'yes_pdf': 'information_refine',
            'no_pdf': 'keyword_preprocess'
        }
    )
    
    builder.add_edge('information_refine', 'keyword_preprocess')
    
    builder.add_conditional_edges(
        'generate_description',
        no_pdf_router,
        {
            'yes_pdf': 'listing_verificate',
            'no_pdf': 'user_input'
        }
    )
    
    builder.add_edge('listing_verificate', 'user_input')
    
    builder.add_conditional_edges(
        'user_input',
        status_router,
        {
            'ONGOING': 'parse_user_feedback',
            'FINISHED': END
        }
    )
    
    builder.add_edge('parse_user_feedback', 'feedback_check')
    
    builder.add_conditional_edges(
        'feedback_check',
        feedback_router,
        {
            'regenerate_title': 'regenerate_title',
            'regenerate_bp': 'regenerate_bp',
            'regenerate_description': 'regenerate_description',
            'user_input': 'user_input'
        }
    )
    
    builder.add_edge('regenerate_title', 'feedback_check')
    builder.add_edge('regenerate_bp', 'feedback_check')
    builder.add_edge('regenerate_description', 'feedback_check')    
    
    return builder.compile()