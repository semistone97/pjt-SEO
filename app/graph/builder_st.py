from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from schemas.global_state import State
from models.node_preprocess_st import preprocess_data, relevance_categorize, select_keywords, information_refine
from models.node_listing_st import keyword_distribute, generate_listing, listing_verificate
from models.node_regenerate_st import parse_user_feedback, feedback_check, regenerate_title, regenerate_bp, regenerate_description

from graph.router import feedback_router, no_pdf_router

load_dotenv()

def build_initial_graph():
    """
    사용자 피드백 이전까지의 초기 분석 그래프
    """
    builder = StateGraph(State)
    
    # 키워드 전처리
    builder.add_sequence([preprocess_data, relevance_categorize, select_keywords])
    builder.add_node('information_refine', information_refine)
    
    # 초안 작성
    builder.add_edge("select_keywords", "keyword_distribute")
    builder.add_sequence([keyword_distribute, generate_listing])
    builder.add_node('listing_verificate', listing_verificate)

    # 연결
    builder.add_conditional_edges(
        START,
        no_pdf_router,
        {
            'yes_pdf': 'information_refine',
            'no_pdf': 'preprocess_data'
        }
    )
    
    builder.add_edge('information_refine', 'preprocess_data')
    
    builder.add_conditional_edges(
        'generate_listing',
        no_pdf_router,
        {
            'yes_pdf': 'listing_verificate',
            'no_pdf': END
        }
    )
    
    builder.add_edge('listing_verificate', END)
    
    return builder.compile()

def build_feedback_graph():
    """
    사용자 피드백 처리 및 재생성 그래프
    """
    builder = StateGraph(State)
    
    # 피드백 처리
    builder.add_node('parse_user_feedback', parse_user_feedback)
    builder.add_node('feedback_check', feedback_check)
    
    # 재생성 노드
    builder.add_node('regenerate_title', regenerate_title)
    builder.add_node('regenerate_bp', regenerate_bp)
    builder.add_node('regenerate_description', regenerate_description)
    
    # 연결
    builder.add_edge(START, 'parse_user_feedback')
    builder.add_edge('parse_user_feedback', 'feedback_check')
    
    builder.add_conditional_edges(
        'feedback_check',
        feedback_router,
        {
            'regenerate_title': 'regenerate_title',
            'regenerate_bp': 'regenerate_bp',
            'regenerate_description': 'regenerate_description',
            'None': END  # 모든 피드백 처리 완료 시
        }
    )
    
    builder.add_edge('regenerate_title', 'feedback_check')
    builder.add_edge('regenerate_bp', 'feedback_check')
    builder.add_edge('regenerate_description', 'feedback_check')    
    
    return builder.compile()
