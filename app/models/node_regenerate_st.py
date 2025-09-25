from schemas.global_state import State
from schemas.schema import TitleOutput, BPOutput, DescriptionOutput, Feedback
from prompts.prompt_listing import title_prompt, bp_prompt, description_prompt
from prompts.prompt_feedback import feedback_prompt
from langchain_openai import ChatOpenAI
from utils.config_loader import config
from dotenv import load_dotenv
import streamlit as st
load_dotenv()


llm = ChatOpenAI(model=config['llm_listing']['model'], temperature=float(config['llm_listing']['temperature']))

# ====================================================================================================
# 피드백 분류
def parse_user_feedback(state: State):
    
    # st.status를 전체 폭으로 표시하기 위해 명시적으로 설정
    with st.container():
        with st.status("피드백 내용 정리 중...", expanded=True) as status:
            
            llm = ChatOpenAI(model=config['llm_feedback']['model'], temperature=float(config['llm_feedback']['temperature']))
            
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
            
            if feedback_title:
                st.write('Title: ', feedback_title) 
            
            if feedback_bp:
                st.write('BP: ', feedback_bp)

            if feedback_description:
                st.write('Description: ', feedback_description)
            
            status.update(label="피드백 정리 완료", state="complete", expanded=False)
        
        return {
            'user_feedback_title': feedback_title,
            'user_feedback_bp': feedback_bp,
            'user_feedback_description': feedback_description
        }
            
# ====================================================================================================
# 피드백 라우팅용 노드
def feedback_check(state: State):

    return state

# ====================================================================================================
# Title 노드
def regenerate_title(state: State):
    
    with st.status("Title 재작성중...", expanded=True) as status:
                
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
            st.success('Title 재작성 성공')
            st.write(res.title)
            st.info(f'재작성된 Title: 총 {len(res.title)}자')
            
            status.update(label="Title 재작성 완료", state="complete", expanded=False)
            
            return {'title': res.title, 'user_feedback_title': ''}

        except Exception as e:
            st.warning(f"Title 재작성 중 에러가 발생했습니다: {e}")
            return {'user_feedback_title': ''}

# ====================================================================================================
# BP 노드
def regenerate_bp(state: State):
    
    with st.status("Bullet Points 재작성중...", expanded=True) as status:

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
            st.success('Bullet Point 재작성 성공')
            bps = res.bp
            bp_length = []
            
            for bp in bps:
                st.write(bp)
                bp_length.append(len(bp))    

            st.info(f'재작성된 Bullet Point: 각 {','.join(bp_length)}자')
            status.update(label="Bullet Points 재작성 완료", state="complete", expanded=False)

            return {'bp': res.bp, 'user_feedback_bp': ''}
        
        except Exception as e:
            st.warning(f"Bullet Point 재작성 중 에러가 발생했습니다: {e}")
            return {'user_feedback_bp': ''}

# ====================================================================================================
# Description 노드
def regenerate_description(state: State):
    with st.status("Description 재작성중...", expanded=True) as status:

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
            
            st.success('Description 재작성 성공')
            st.write(res.description)
            st.info(f'재작성된 Description: 총 {len(res.description)}자')
            
            status.update(label="Description 재작성 완료", state="complete", expanded=False)

            return {'description': res.description, 'user_feedback_description': ''}

        except Exception as e:
            st.warning(f"Description 재작성 중 에러가 발생했습니다: {e}")
            return {'user_feedback_description': ''}
        