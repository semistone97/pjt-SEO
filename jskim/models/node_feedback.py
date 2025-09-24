from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI
from schemas.global_state import State
from schemas.schema import Feedback
from prompts.prompt_feedback import feedback_prompt
from utils.config_loader import config
import os, sys
import streamlit as st
load_dotenv()

llm = ChatOpenAI(model=config['llm_feedback']['model'], temperature=float(config['llm_feedback']['temperature']))

# ====================================================================================================
# 사용자 피드백 입력

def user_input(state: State):
    """
    사용자 피드백 처리 노드
    
    LangGraph의 피드백 루프 구조를 유지하면서
    Streamlit에서 UI는 별도로 처리
    """
    
    # 이미 사용자 피드백이 있다면 (Streamlit에서 설정됨)
    if 'user_feedback' in state and state.get('user_feedback'):
        print(f"[user_input] 피드백 받음: {state['user_feedback'][:50]}...")
        return {
            'user_feedback': state['user_feedback'],
            'status': 'ONGOING'
        }
    
    # 피드백이 없다면 - 초기 결과 생성 완료 상태
    print("[user_input] 초기 결과 생성 완료, 사용자 피드백 대기 중...")
    
    # 현재 결과를 그대로 유지하면서 사용자 입력 대기
    # Streamlit UI에서 이 상태를 감지하고 피드백 UI를 표시
    return {
        'title': state.get('title'),
        'bp': state.get('bp'),
        'description': state.get('description'),
        'status': 'WAITING_FOR_FEEDBACK'  # 사용자 입력 대기 상태
    }

# ====================================================================================================
# 피드백 분류
def parse_user_feedback(state: State):
    
    
    st.write('\n--- 피드백 내용을 정리합니다... ---')
    
    structured_llm = llm.with_structured_output(Feedback)
    prompt = feedback_prompt.invoke(
        {
            'user_feedback': state['user_feedback'],
        }
    )
    res = structured_llm.invoke(prompt)
    
    feedback_title = res.title or ''
    
    bp_raw = res.bp or ''
    if isinstance(bp_raw, (list, tuple)):
        feedback_bp = '\n'.join(bp_raw).strip()
    else:
        feedback_bp = bp_raw or ''
        
    feedback_description = res.description or ''
    
    st.write()
    if feedback_title:
        st.write('Title: ', feedback_title) 
    
    if feedback_bp:
        st.write('BP: ', feedback_bp)

    if feedback_description:
        st.write('Description: ', feedback_description)
    
    return {
        'user_feedback_title': feedback_title,
        'user_feedback_bp': feedback_bp,
        'user_feedback_description': feedback_description
    }     
    
# ====================================================================================================
# 피드백 라우팅용 노드
def feedback_check(state: State):
    
    st.write('\n--- 남은 피드백이 있는지 확인합니다...')
    
    if state['user_feedback_title']:
        st.write('\nTitle 피드백이 존재합니다') 
        return {}
    
    elif state['user_feedback_bp']:
        st.write('\nBP 피드백이 존재합니다') 
        return {}
    
    elif state['user_feedback_description']:
        st.write('\nDescription 피드백이 존재합니다') 
        return {}
    
    else:
        st.write('\n모든 피드백이 처리되었습니다')
        return {}

