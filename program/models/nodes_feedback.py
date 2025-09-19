from dotenv import load_dotenv
import json
from langchain_openai import ChatOpenAI
from schemas.states import State
from schemas.schemas import Feedback
from prompts.prompts_feedback import feedback_prompt
from utils.config_loader import config

load_dotenv()

llm = ChatOpenAI(model=config['llm_feedback']['model'], temperature=float(config['llm_feedback']['temperature']))

def user_input(state: State):
    
    print("===== 결과물 출력 =====")
    print(f'Title:       ============================================================================================\n{state.get('title')}')
    print('BP:          ============================================================================================')
    for bp in state.get('bp'):
        print(bp)
    print(f'Description: ============================================================================================\n{state.get('description')}')
    
    user_feedback = input('\n사용자 피드백을 입력해 주세요. 피드백이 없다면, 빈 칸으로 남겨주세요:\n')
    
    if not user_feedback.strip():
        print('피드백이 없습니다. 결과물을 출력합니다.')
        return {'status': 'FINISHED'}

    return {'user_feedback': user_feedback}


def parse_user_feedback(state: State):
    
    structured_llm = llm.with_structured_output(Feedback)
    prompt = feedback_prompt.invoke(
        {
            'user_feedback': state['user_feedback'],
        }
    )
    res = structured_llm.invoke(prompt)
    data = json.loads(res.content)
    print(f'피드백이 인식되었습니다. (T: {'O' if data.get('title', '') else 'X'}/ B: {'O' if data.get('bp', '') else 'X'}/ D: {'O' if data.get('description', '') else 'X'})')
    return {
        'user_feedback_title': data.get('title', ''), 
        'user_feedback_bp': data.get('bp', ''), 
        'user_feedback_description': data.get('description', '')
    }

def print_feedback(state: State):
    print('Title: ', state['user_feedback_title'])
    print('BP: ', state['user_feedback_bp'])
    print('Description: ', state['user_feedback_description'])
    return {}