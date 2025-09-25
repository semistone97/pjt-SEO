# builder.py - 수정된 버전
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from schemas.global_state import State
from models.node_preprocess import keyword_preprocess, relevance_categorize, select_keywords, information_refine
from models.node_listing import keyword_distribute, generate_title, generate_bp, generate_description, listing_verificate
from models.node_feedback import parse_user_feedback, feedback_check
from models.node_regenerate import regenerate_title, regenerate_bp, regenerate_description

from graph.router import feedback_router, no_pdf_router

load_dotenv()

def build_initial_graph():
    """
    사용자 피드백 이전까지의 초기 분석 그래프
    """
    builder = StateGraph(State)
    
    # 키워드 전처리
    builder.add_sequence([keyword_preprocess, relevance_categorize, select_keywords])
    builder.add_node('information_refine', information_refine)
    
    # 초안 작성
    builder.add_edge("select_keywords", "keyword_distribute")
    builder.add_sequence([keyword_distribute, generate_title, generate_bp, generate_description])
    builder.add_node('listing_verificate', listing_verificate)

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
            'user_input': END  # 모든 피드백 처리 완료
        }
    )
    
    builder.add_edge('regenerate_title', 'feedback_check')
    builder.add_edge('regenerate_bp', 'feedback_check')
    builder.add_edge('regenerate_description', 'feedback_check')    
    
    return builder.compile()

# 기존 함수는 호환성을 위해 유지 (deprecated)
def build_graph():
    """
    레거시 호환성을 위한 함수 - 사용 권장하지 않음
    """
    return build_initial_graph()