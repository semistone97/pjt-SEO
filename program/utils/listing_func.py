from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from schemas.global_state import State
from schemas.schema import TitleOutput, BPOutput, DescriptionOutput
from prompts.prompt_listing import title_prompt, bp_prompt, description_prompt
from utils.config_loader import config

load_dotenv()

# LLM 정의
llm = ChatOpenAI(model=config['llm_listing']['model'], temperature=float(config['llm_listing']['temperature']))

# ====================================================================================================
# Title 노드
def generate_title(state: State):
    
    if not state.get('title_keyword'):
        print('\n[Skipped] Title 작성용 키워드가 존재하지 않습니다.')
        return {}
    
    print(f'\n--- Title 작성을 시작합니다... ---')
    
    try:
        prompt = title_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'title_keyword': state['title_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(TitleOutput)
        res = structured_llm.invoke(prompt)
        print(f'\n작성된 Title: 총 {len(res.title)}자')
        return {'title': res.title}

    except Exception as e:
        print(f"\n[Error] Title 작성 중 에러가 발생했습니다: {e}")
        return {}

# ====================================================================================================
# BP 노드
def generate_bp(state: State):
    
    if not state.get('bp_keyword'):
        print('\n[Skipped] Bullet Point 작성용 키워드가 존재하지 않습니다.')
        return {}

    print(f'\n--- Bullet Point 작성을 시작합니다... ---')
    
    try:
        prompt = bp_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'bp_keyword': state['bp_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(BPOutput)
        res = structured_llm.invoke(prompt)
        bp_length = []
        for bp in res.bp:
            bp_length.append(len(bp))    
        print(f'\n작성된 Bullet Point: 각 {bp_length}자')
        return {'bp': res.bp}
    
    except Exception as e:
        print(f"\n[Error] Bullet Point 작성 중 에러가 발생했습니다: {e}")
        return {}

# ====================================================================================================
# Description 노드
def generate_description(state: State):
    
    if not state.get('description_keyword'):
        print('\n[Skipped] Description 작성용 키워드가 존재하지 않습니다.')
        return {}
    
    print(f'\n--- Description 작성을 시작합니다... ---')
    
    try:
        prompt = description_prompt.invoke(
            {
                'bp_result': state.get('bp',[]),
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
                'description_keyword': state['description_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(DescriptionOutput)
        res = structured_llm.invoke(prompt)
        print(f'\n작성된 Description: 총 {len(res.description)}자')
        return {'description': res.description}

    except Exception as e:
        print(f"\n[Error] Description 작성 중 에러가 발생했습니다: {e}")
        return {}

# ====================================================================================================
# Listing 통합 노드
def generate_listing(state: State):
    """
    Title, Bullet Points, Description을 순차적으로 생성하기 위해
    기존의 개별 생성 함수들을 호출하는 메인 함수.
    """
    print("\n--- 통합 리스팅 생성을 시작합니다... ---")
    
    # 1. Title 생성 함수 호출
    title_update = generate_title(state)
    
    # 2. BP 생성 함수 호출
    bp_update = generate_bp(state)
    
    # 3. Description 생성을 위해 state를 임시로 업데이트
    # (generate_description 함수는 state에서 'bp' 결과를 필요로 함)
    temp_state = state.copy()
    temp_state.update(bp_update) # bp_update 딕셔너리 {'bp': [...]} 를 추가
        
    description_update = generate_description(temp_state)
    
    # 4. 모든 결과를 취합하여 최종 업데이트 딕셔너리 생xw성
    final_update = {}
    final_update.update(title_update)
    final_update.update(bp_update)
    final_update.update(description_update)
    
    print("\n--- 통합 리스팅 생성 완료 ---")
    return final_update