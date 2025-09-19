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
        return {'status': 'FINISHED'}

    return {'user_feedback': user_feedback}

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
    data = json.loads(res.content)
    
    print()
    
    if data.get('title', ''):
        print('Title: ', state['user_feedback_title']) 
    
    if data.get('bp', ''):
        print('BP: ', state['user_feedback_bp'])
    
    if data.get('description', ''):
        print('Description: ', state['user_feedback_description'])
    
    return {
        'user_feedback_title': data.get('title', ''), 
        'user_feedback_bp': data.get('bp', ''), 
        'user_feedback_description': data.get('description', '')
    }

