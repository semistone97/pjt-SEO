from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI
from schemas.global_state import State
from schemas.schema import Feedback
from prompts.prompt_feedback import feedback_prompt
from utils.config_loader import config
import os, sys

load_dotenv()

llm = ChatOpenAI(model=config['llm_feedback']['model'], temperature=float(config['llm_feedback']['temperature']))

# ====================================================================================================
# 사용자 피드백 입력
def user_input(state: State):
    
    title, bp_list, description = state.get('title'), state.get('bp'), state.get('description')
    leftover = sorted(state.get('leftover') + state.get('backend_keywords'))
    
    print("\n=== 결과물 출력 ===")
    print(f'\nTitle:\n{title}')
    print('\nBP:')
    for bp in bp_list:
        print(bp)
    print(f'\nDescription:\n{description}')
    
    user_feedback = input('\n### 사용자 피드백을 입력해 주세요. (/help: 도움말) ###\n').strip()
    
    while user_feedback[0] == '/':
        if user_feedback in ['/finish']:
            print('\n작동을 종료합니다.')
            
            save_dir = 'output'
            
            os.makedirs(save_dir, exist_ok=True)
            filename = f'{"_".join(state.get('product_name').split())}_Keyword_Listing_Final.txt'
            file_path = os.path.join(save_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f'\n[Title]\n{state.get('title')}\n')
                f.write('\n[Bullet Point]\n')
                for bp in state.get('bp'):
                    f.write(str(bp) + '\n')
                f.write(f'\n[Description]\n{state.get('description')}\n')
                f.write('\nLeftover Keywords: ' + ', '.join(map(str, sorted(state.get('leftover') + state.get('backend_keywords')))))
                        
                print(f'최종 결과물을 {filename} 파일에 저장합니다. ')
            
            return {'user_feedback': '', 'status': 'FINISHED'}
        
        if user_feedback in ['/q']:
            print('\n작동을 종료합니다.')
            sys.exit(1)
        
        elif user_feedback in ['/export']:
            now = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
            
            save_dir = 'output'
            os.makedirs(save_dir, exist_ok=True)
            filename = f'{"_".join(state.get('product_name').split())}_Temp_Listing({now}).txt'
            file_path = os.path.join(save_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f'\n[Title]\n{title}\n')
                f.write('\n[Bullet Point]\n')
                for bp in bp_list:
                    f.write(str(bp) + '\n')
                f.write(f'\n[Description]\n{description}\n')
                f.write('\nLeftover Keywords: ' + ', '.join(map(str, leftover)))
                        
            print(f'\n현재 초안을 {filename} 파일에 저장합니다. ')
        
        elif user_feedback in ['/help']:
            print('=== 도움말 리스트 ===')
            print('/help: 도움말')
            print('/export: 현재 파일을 저장')
            print('/finish: 현재 초안을 최종 파일로 저장 후 종료')
            print('/q: 프로그램 강제종료(저장 안함)')
        else:
            print('[Warning] 명령어를 인식할 수 없습니다.')

        user_feedback = input('\n### 사용자 피드백을 입력해 주세요 ###\n')


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

