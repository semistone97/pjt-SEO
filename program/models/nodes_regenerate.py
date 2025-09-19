from schemas.states import State
from schemas.schemas import TitleOutput, BPOutput, DescriptionOutput
from prompts.prompts import title_prompt, bp_prompt, description_prompt
from langchain_openai import ChatOpenAI
from utils.config_loader import config
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model=config['llm_listing']['model'], temperature=float(config['llm_listing']['temperature']))


# regenerate prompt
regen_template = '''
아래의 


'''











# Title 노드
def regenerate_title(state: State):
    
    if not state['title_keyword']:
        print('Title 작성용 키워드가 존재하지 않습니다.')
        return {}
    
    print(f'--- Title 작성을 시작합니다 ---')
    
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
        print(f'작성된 Title: 총 {len(res.title)}자')
        return {'title': res.title}

    except Exception as e:
        print(f"Title 작성 중 에러가 발생했습니다: {e}")
        return {}


# BP 노드
def regenerate_bp(state: State):
    
    if not state['bp_keyword']:
        print('Bullet Point 작성용 키워드가 존재하지 않습니다.')
        return {}

    print(f'--- Bullet Point 작성을 시작합니다 ---')
    
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
        print(f'작성된 Bullet Point: 각 {bp_length}자')
        return {'bp': res.bp}
    
    except Exception as e:
        print(f"Title 작성 중 에러가 발생했습니다: {e}")
        return {}

# Description 노드
def regenerate_description(state: State):
    
    if not state['description_keyword']:
        print('Description 작성용 키워드가 존재하지 않습니다.')
        return {}
    
    print(f'--- Description 작성을 시작합니다 ---')
    
    try:
        prompt = description_prompt.invoke(
            {
                'product_name': state['product_name'], 
                'category': state['category'],
                'product_information': state['product_information'], 
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
