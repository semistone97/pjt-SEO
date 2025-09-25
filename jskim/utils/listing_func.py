import streamlit as st
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
    
    with st.status("Title 작성 중...", expanded=True) as status:

        if not state['title_keyword']:
            st.write('\n[Skipped] Title 작성용 키워드가 존재하지 않습니다.')
            return {}
        
        st.write(f'\n--- Title 작성을 시작합니다... ---')
        
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
            
            st.success('Title 작성 성공')
            st.write(res.title)
            st.write(f'\n작성된 Title: 총 {len(res.title)}자')
            status.update(label="Title 작성 완료", state="complete", expanded=False)

            return {'title': res.title}

        except Exception as e:
            st.write(f"\n[Error] Title 작성 중 에러가 발생했습니다: {e}")
            return {}


# ====================================================================================================
# BP 노드
def generate_bp(state: State):
    
    with st.status("BP 작성 중...", expanded=True) as status:
            
        if not state['bp_keyword']:
            st.write('\n[Skipped] Bullet Point 작성용 키워드가 존재하지 않습니다.')
            return {}

        st.write(f'\n--- Bullet Point 작성을 시작합니다... ---')
        
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
            bps = res.bp

            st.success('BP 작성 성공')

            for bp in bps:
                st.write(bp)
                bp_length.append(len(bp))    
                
            st.write(f'\n작성된 Bullet Point: 각 {bp_length}자')
            status.update(label="BP 작성 완료", state="complete", expanded=False)

            return {'bp': bps}
        
        except Exception as e:
            st.write(f"\n[Error] Bullet Point 작성 중 에러가 발생했습니다: {e}")
            return {}


# ====================================================================================================
# Description 노드
def generate_description(state: State):
    with st.status("Description 작성 중...", expanded=True) as status:

        if not state['description_keyword']:
            st.write('\n[Skipped] Description 작성용 키워드가 존재하지 않습니다.')
            return {}
        
        st.write(f'\n--- Description 작성을 시작합니다... ---')
        
        try:
            prompt = description_prompt.invoke(
                {
                    'bp_result': state['bp'],
                    'product_name': state['product_name'], 
                    'category': state['category'],
                    'product_information': state['product_information'], 
                    'description_keyword': state['description_keyword'],
                }
            )
            structured_llm = llm.with_structured_output(DescriptionOutput)
            res = structured_llm.invoke(prompt)
            
            st.success('Description 작성 성공')
            st.write(res.description)
            st.write(f'\n작성된 Description: 총 {len(res.description)}자')
            
            status.update(label="Description 작성 완료", state="complete", expanded=False)

            return {'description': res.description}

        except Exception as e:
            st.write(f"\n[Error] Description 작성 중 에러가 발생했습니다: {e}")
            return {}
        