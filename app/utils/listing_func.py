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
        st.info('키워드를 기반으로 Title을 작성합니다.')
        if not state['title_keyword']:
            st.warning('Title 작성용 키워드가 존재하지 않습니다.')
            if st.button("처음으로"):
                st.session_state.current_step = '데이터 입력'
                st.rerun()
            return
                
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
            st.info(f'작성된 Title: 총 {len(res.title)}자')
            status.update(label="Title 작성 완료", state="complete", expanded=False)

            return {'title': res.title}

        except Exception as e:
            st.error(f"Title 작성 중 에러가 발생했습니다: {e}")
            if st.button("처음으로"):
                st.session_state.current_step = '데이터 입력'
                st.rerun()
            return


# ====================================================================================================
# BP 노드
def generate_bp(state: State):
    
    with st.status("Bullet Point 작성 중...", expanded=True) as status:
        st.info('키워드를 기반으로 Bullet Points를 작성합니다.')
        if not state['bp_keyword']:
            st.warning('Bullet Point 작성용 키워드가 존재하지 않습니다.')
            if st.button("처음으로"):
                st.session_state.current_step = '데이터 입력'
                st.rerun()
            return
        
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

            st.success('Bullet Point 작성 성공')

            for bp in bps:
                st.write(bp)
                bp_length.append(str(len(bp)))    

            st.info(f'작성된 Bullet Point: 각 {','.join(bp_length)}자')
            status.update(label="Bullet Point 작성 완료", state="complete", expanded=False)

            return {'bp': bps}
        
        except Exception as e:
            st.error(f"Bullet Point 작성 중 에러가 발생했습니다: {e}")
            if st.button("처음으로"):
                st.session_state.current_step = '데이터 입력'
                st.rerun()
            return


# ====================================================================================================
# Description 노드
def generate_description(state: State):
    with st.status("Description 작성 중...", expanded=True) as status:
        st.info('키워드를 기반으로 Description을 작성합니다.')
        
        if not state['description_keyword']:
            st.warning('Description 작성용 키워드가 존재하지 않습니다.')
            if st.button("처음으로"):
                st.session_state.current_step = '데이터 입력'
                st.rerun()
            return
                
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
            st.info(f'\n작성된 Description: 총 {len(res.description)}자')
            
            status.update(label="Description 작성 완료", state="complete", expanded=False)

            return {'description': res.description}

        except Exception as e:
            st.error(f"Description 작성 중 에러가 발생했습니다: {e}")
            if st.button("처음으로"):
                st.session_state.current_step = '데이터 입력'
                st.rerun()
            return      