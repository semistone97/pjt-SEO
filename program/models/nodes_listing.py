from schemas.states import State
from schemas.schemas import KeywordDistribute, TitleOutput, BPOutput, DescriptionOutput
from prompts.prompts import keyword_prompt, title_prompt, bp_prompt, description_prompt
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model='gpt-4o', temperature=0)

# 키워드 분배 노드
def keyword_distribute(state: State):
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
    return {
        'title_keyword': res.title_keyword, 
        'bp_keyword': res.bp_keyword, 
        'description_keyword': res.description_keyword, 
        'leftover': res.leftover
    }    


# Title 노드
def generate_title(state: State):
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
    return {'title': res.title}

# BP 노드
def generate_bp(state: State):
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
    return {'bp': res.bp}

# Description 노드
def generate_description(state: State):
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
    return {'description': res.description}