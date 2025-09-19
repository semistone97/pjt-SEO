from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from schemas.global_state import State
from models.node_preprocess import keyword_preprocess, relevance_categorize, select_keywords
from models.node_listing import keyword_distribute, generate_title, generate_bp, generate_description
from models.node_info import information_extract, listing_verificate
from models.node_feedback import user_input, parse_user_feedback
from graph.router import status_router, feedback_router

load_dotenv()


def build_graph():
    builder = StateGraph(State)
    
    # 키워드 분배
    builder.add_sequence([keyword_preprocess, relevance_categorize, select_keywords])

    # 초안 작성
    builder.add_edge("select_keywords", "keyword_distribute")
    builder.add_sequence([keyword_distribute, generate_title, generate_bp, generate_description, information_extract, listing_verificate])

    # 사용자 피드백
    builder.add_node('user_input', user_input)
    builder.add_node('parse_user_feedback', parse_user_feedback)

    # 재생성 노드
    builder.add_node('regenerate_title', generate_title)
    builder.add_node('regenerate_bp', generate_bp)
    builder.add_node('regenerate_description', generate_description)
    
    # ====================================================================================================
    # 연결
    builder.add_edge(START, "keyword_preprocess")
    
    builder.add_edge('listing_verificate', 'user_input')
    
    builder.add_conditional_edges(
        'user_input',
        status_router,
        {
            'parse_user_feedback': 'parse_user_feedback',
            'END': END
        }
    )
        
    builder.add_conditional_edges(
        'parse_user_feedback',
        feedback_router,
        {
            'regenerate_title': 'regenerate_title',
            'regenerate_bp': 'regenerate_bp',
            'regenerate_description': 'regenerate_description'
        }
    )
    
    builder.add_edge('regenerate_title', 'parse_user_feedback')
    builder.add_edge('regenerate_bp', 'parse_user_feedback')
    builder.add_edge('regenerate_description', 'parse_user_feedback')    
    
    return builder.compile()