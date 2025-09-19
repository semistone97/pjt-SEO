from dotenv import load_dotenv
import json
from langchain_openai import ChatOpenAI
from schemas.global_state import State
from schemas.schema import Feedback
from prompts.prompt_feedback import feedback_prompt
from utils.config_loader import config

load_dotenv()

llm = ChatOpenAI(model=config['llm_feedback']['model'], temperature=float(config['llm_feedback']['temperature']))

# ====================================================================================================
# 사용자 피드백 입력
def user_input(state: State):
    
    print("\n=== 결과물 출력 ===")
    print(f'\nTitle:\n{state.get('title')}')
    print('\nBP:')
    for bp in state.get('bp'):
        print(bp)
    print(f'\nDescription:\n{state.get('description')}')
    
    user_feedback = input('\n### 사용자 피드백을 입력해 주세요. 피드백이 없다면, 빈 칸으로 남겨주세요 ###\n')
    
    if not user_feedback.strip():
        print('\n피드백이 없습니다. 결과물을 출력합니다.')
        result = {'status': 'FINISHED'}
        print(f"DEBUG: user_input returning: {result}")  # 디버깅 추가        
        return {'status': 'FINISHED'}


    result = {'user_feedback': user_feedback, 'status': 'ONGOING'}
    print(f"DEBUG: user_input returning: {result}")  # 디버깅 추가

    return {'user_feedback': user_feedback, 'status': 'ONGOING'}

# ====================================================================================================
# 피드백 분류
def parse_user_feedback(state: State):
    print('\n--- 피드백 내용을 정리합니다... ---')
    
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
    
    print()
    if feedback_title:
        print('Title: ', feedback_title) 
    
    if feedback_bp:
        print('BP: ', feedback_bp)

    if feedback_description:
        print('Description: ', feedback_description)
    
    return {
        'user_feedback_title': feedback_title,
        'user_feedback_bp': feedback_bp,
        'user_feedback_description': feedback_description
    }     
# ====================================================================================================
# 피드백 라우팅용 노드
def feedback_check(state: State):
    
    print('\n--- 남은 피드백이 있는지 확인합니다...')
    
    if state['user_feedback_title']:
        print('\nTitle 피드백이 존재합니다') 
        return {}
    
    elif state['user_feedback_bp']:
        print('\nBP 피드백이 존재합니다') 
        return {}
    
    elif state['user_feedback_description']:
        print('\nDescription 피드백이 존재합니다') 
        return {}
    
    else:
        print('\n모든 피드백이 처리되었습니다')
        return {}

