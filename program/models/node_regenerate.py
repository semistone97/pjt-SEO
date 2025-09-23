from schemas.global_state import State
from schemas.schema import TitleOutput, BPOutput, DescriptionOutput
from prompts.prompt_listing import title_prompt, bp_prompt, description_prompt
from langchain_openai import ChatOpenAI
from utils.config_loader import config
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model=config['llm_listing']['model'], temperature=float(config['llm_listing']['temperature']))

# ====================================================================================================
# Title 노드
def regenerate_title(state: State):
    
    if not state['title_keyword']:
        print('\n[Skipped] Title 재작성용 키워드가 존재하지 않습니다.')
        return {'user_feedback_title': ''}
    
    print(f'\n--- Title 재작성을 시작합니다... ---')
    
    try:
        base_prompt = str(title_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'title_keyword': state['title_keyword'],
            }
        ))
        
        title_feedback_prompt =  '[User Feedback]\n{user_feedback}\nYou are required to take this into consideration.\n' + base_prompt + '[\nCurrent Title\n{title}]'
            
        prompt = title_feedback_prompt.format(
            user_feedback= state['user_feedback_title'],
            title= state['title']
        )
        
        structured_llm = llm.with_structured_output(TitleOutput)
        res = structured_llm.invoke(prompt)
        print(f'\n재작성된 Title: 총 {len(res.title)}자')
        return {'title': res.title, 'user_feedback_title': ''}

    except Exception as e:
        print(f"\n[Error] Title 재작성 중 에러가 발생했습니다: {e}")
        return {'user_feedback_title': ''}

# ====================================================================================================
# BP 노드
def regenerate_bp(state: State):
    
    if not state['bp_keyword']:
        print('\n[Skipped] Bullet Point 재작성용 키워드가 존재하지 않습니다.')
        return {'user_feedback_bp': ''}

    print(f'\n--- Bullet Point 재작성을 시작합니다... ---')
    
    try:
        base_prompt = str(bp_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'bp_keyword': state['bp_keyword'],
            }
        ))
        
        bp_feedback_prompt = '[User Feedback]\n{user_feedback}\nYou are required to take this into consideration.' + base_prompt + '[\nCurrent BP\n{bp}]'

        prompt = bp_feedback_prompt.format(
            user_feedback= state['user_feedback_bp'],
            bp= state['bp']
        )
        
        structured_llm = llm.with_structured_output(BPOutput)
        res = structured_llm.invoke(prompt)
        bp_length = []
        for bp in res.bp:
            bp_length.append(len(bp))    
        print(f'\n재작성된 Bullet Point: 각 {bp_length}자')
        return {'bp': res.bp, 'user_feedback_bp': ''}
    
    except Exception as e:
        print(f"\n[Error] Bullet Point 재작성 중 에러가 발생했습니다: {e}")
        return {'user_feedback_bp': ''}

# ====================================================================================================
# Description 노드
def regenerate_description(state: State):
    
    if not state['description_keyword']:
        print('\n[Skipped] Description 재작성용 키워드가 존재하지 않습니다.')
        return {'user_feedback_description': ''}
    
    print(f'\n--- Description 재작성을 시작합니다... ---')
    
    try:
        base_prompt = str(description_prompt.invoke(
            {
                'bp_result': state['bp'],
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'description_keyword': state['description_keyword'],
            }
        ))
        
        description_feedback_prompt = '[User Feedback]\n{user_feedback}\nYou are required to take this into consideration.' + base_prompt + '[\nCurrent Description\n{description}]'
        
        prompt = description_feedback_prompt.format(
            user_feedback= state['user_feedback_description'],
            description= state['description']
        )

        structured_llm = llm.with_structured_output(DescriptionOutput)
        res = structured_llm.invoke(prompt)
        print(f'\n재작성된 Description: 총 {len(res.description)}자')
        return {'description': res.description, 'user_feedback_description': ''}

    except Exception as e:
        print(f"\n[Error] Description 재작성 중 에러가 발생했습니다: {e}")
        return {'user_feedback_description': ''}
    