from schemas.states import State
from schemas.schemas import KeywordDistribute, TitleOutput, BPOutput, DescriptionOutput
from prompts.prompts import keyword_prompt, title_prompt, bp_prompt, description_prompt
from langchain_openai import ChatOpenAI
from utils.config_loader import config
from dotenv import load_dotenv


load_dotenv()

llm = ChatOpenAI(model=config['llm_listing']['model'], temperature=float(config['llm_listing']['temperature']))

# 키워드 분배 노드
def keyword_distribute(state: State):
    
    if not state['data']:
        print("데이터가 없어 키워드 분배를 종료합니다.")
        return {}
    
    print(f'--- 키워드 {len(state['data'])}개에 대해 분배를 시작합니다 ---')
    
    try:
        prompt = keyword_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_description': state['product_description'], 
                'data': state['data'],
            }
        )
        structured_llm = llm.with_structured_output(KeywordDistribute)
        res = structured_llm.invoke(prompt)
        
        print('키워드 분배 결과')
        print(f'Title Keyword: {len(res.title_keyword)}개')
        print(f'BP Keyword: {len(res.bp_keyword)}개')
        print(f'Description Keyword: {len(res.description_keyword)}개')
        print(f'Leftover: {len(res.leftover)}개')
        
        return {
            'title_keyword': res.title_keyword, 
            'bp_keyword': res.bp_keyword, 
            'description_keyword': res.description_keyword, 
            'leftover': res.leftover
        }    

    except Exception as e:
        print(f"키워드 분배 중 에러가 발생했습니다: {e}")
        return {}

# Title 노드
def generate_title(state: State):
    
    if not state['title_keyword']:
        print('Title 작성용 키워드가 존재하지 않습니다.')
        return {}
    
    print(f'--- Title 작성을 시작합니다 ---')
    
    try:
        prompt = title_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_description': state['product_description'], 
                'title_keyword': state['title_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(TitleOutput)
        res = structured_llm.invoke(prompt)
        print(f'작성된 Title: 총 {len(res.title)}자')
        return {'title': res.title}

    except Exception as e:
        print(f"Title 작성 중 에러가 발생했습니다: {e}")
        return {}


# BP 노드
def generate_bp(state: State):
    
    if not state['bp_keyword']:
        print('Bullet Point 작성용 키워드가 존재하지 않습니다.')
        return {}

    print(f'--- Bullet Point 작성을 시작합니다 ---')
    
    try:
        prompt = bp_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_description': state['product_description'], 
                'bp_keyword': state['bp_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(BPOutput)
        res = structured_llm.invoke(prompt)
        bp_length = []
        for bp in res.bp:
            bp_length.append(len(bp))    
        print(f'작성된 Bullet Point: 각 {bp_length}자')
        return {'bp': res.bp}
    
    except Exception as e:
        print(f"Title 작성 중 에러가 발생했습니다: {e}")
        return {}

# Description 노드
def generate_description(state: State):
    
    if not state['description_keyword']:
        print('Description 작성용 키워드가 존재하지 않습니다.')
        return {}
    
    print(f'--- Description 작성을 시작합니다 ---')
    
    try:
        prompt = description_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_description': state['product_description'], 
                'description_keyword': state['description_keyword'],
            }
        )
        structured_llm = llm.with_structured_output(DescriptionOutput)
        res = structured_llm.invoke(prompt)
        print(f'작성된 Description: 총 {len(res.description)}자')
        return {'description': res.description}

    except Exception as e:
        print(f"Title 작성 중 에러가 발생했습니다: {e}")
        return {}
