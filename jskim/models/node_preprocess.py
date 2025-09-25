import json, sys
import pandas as pd
from typing import Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from prompts.prompt_preprocess import filter_prompt, relevance_prompt, select_prompt, summarization_prompt
from schemas.global_state import State
from utils.func import preprocess_keywords, scaler
from utils.config_loader import config
import streamlit as st

load_dotenv()

# ====================================================================================================
# 키워드 정제
def keyword_preprocess(state: State):
    with st.status("키워드 전처리 진행 중...", expanded=True) as status:
        
        if not state['data']:
            st.error("\n[Skipped] 데이터가 없어 키워드 정제를 종료합니다.")
            return {}
        
        try:
            st.write(f'\n--- 키워드 {len(state['data'])}개에 대해 정제를 시작합니다... ---')
            
            llm = ChatOpenAI(model=config['llm_keyword']['model'], temperature=float(config['llm_keyword']['temperature']))
        
            df = pd.DataFrame(state["data"])
                
            response_schemas = [
                ResponseSchema(
                    name="keywords",
                    description="조건을 적용한 키워드 리스트, 문자열 리스트 또는 dict 리스트 가능"
                )
            ]
            parser = StructuredOutputParser.from_response_schemas(response_schemas)
            
            # 1. 사전 필터링
            filtered_series = preprocess_keywords(df['keyword'])

            # 2. 프롬프트 생성
            keyword_prompt = filter_prompt.format(
                data=filtered_series.tolist(),
                format_instructions=parser.get_format_instructions()
            )

            # 3. LLM 호출
            res = llm.invoke([{"role": "user", "content": keyword_prompt}])
            structured = parser.parse(res.content)

            # 4. 파싱 처리
            raw_keywords = structured.get("keywords", [])
            if len(raw_keywords) > 0 and isinstance(raw_keywords[0], dict):
                cleaned_keywords = [k.get('keyword') for k in raw_keywords if 'keyword' in k]
            else:
                cleaned_keywords = raw_keywords

            # 5. 원본 DF 필터
            cleaned_data = df[df['keyword'].isin(cleaned_keywords)].reset_index(drop=True)
            
            processed_df = scaler(cleaned_data)
            
            processed_df = processed_df.to_dict(orient='records')
            
            st.success(f'\n키워드 {len(processed_df)}개를 정제하였습니다')
            
            status.update(label="키워드 정제 완료", state="complete", expanded=False)
            
            
            return {"data": processed_df}
            
        except Exception as e:
            st.error(f"\n[Error] 키워드 정제 중 에러가 발생했습니다: {e}")
            return {}


# ====================================================================================================
# 노드 함수 정의

llm = ChatOpenAI(model=config['llm_relevance']['model'], temperature=float(config['llm_keyword']['temperature']))

def relevance_categorize(state: State) -> Dict:
    with st.status("연관성 작업 진행 중...", expanded=True) as status:

        """
        LLM을 사용하여 각 키워드의 연관성을 4가지 카테고리(직접, 중간, 간접, 없음)로 분류합니다.
        """
        st.write("\n--- 연관성 분류를 시작합니다... ---\n")
        
        product_name = state.get("product_name")
        product_information = state.get("product_information")
        data = state.get("data", [])

        # 데이터가 비어있으면 중단
        if not data:
            st.warning("\n[Skipped] 데이터가 없어 연관성 분류를 건너뜁니다.")
            return {}

        # DataFrame을 dict 리스트로 변환 (만약 DataFrame으로 들어올 경우)
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='records')

        keywords = [row['keyword'] for row in data if 'keyword' in row]
        if not keywords:
            st.warning("\n[Warning] 키워드가 없어 연관성 분류를 건너뜁니다.")
            return {}

        
        chain = relevance_prompt | llm | StrOutputParser()
        
        st.write(f"--- {len(keywords)}개 키워드의 연관성 분류를 요청합니다... ---")
        
        try:
            response_str = chain.invoke({
                "product_name": product_name,
                "product_information": product_information,
                "keyword_list_str": json.dumps(keywords, ensure_ascii=False)
            })
            
            
            classifications = json.loads(response_str)
            
            classification_map = {item['keyword']: item['relevance_category'] for item in classifications}
            
            for row in data:
                if 'keyword' in row:
                    row['relevance_category'] = classification_map.get(row['keyword'], '없음')
            
            st.success("\n모든 키워드에 연관성 카테고리를 부여했습니다")
            status.update(label="연관성 카테고리 부여 완료", state="complete", expanded=False)


            return {"data": data}

        except Exception as e:
            st.error(f"\n[Error] 연관성 분류 중 에러가 발생했습니다: {e}")
            for row in data:
                row['relevance_category'] = '분류 실패'
            return {"data": data}


# ====================================================================================================
# 상위 키워드 선택

def select_keywords(state: State) -> Dict:

    with st.status("상위 키워드 선택 중...", expanded=True) as status:


        st.write("\n--- 상위 키워드 선별 및 백엔드 키워드를 저장합니다... ---")
        
        data = state.get("data", [])

        if not data:
            st.warning("\n[Skipped] 데이터가 없어 키워드 선별을 건너뜁니다.")
            return {"data": [], "backend_keywords": []}

        simplified_data = [
            {
                "keyword": row.get("keyword"),
                "relevance_category": row.get("relevance_category"),
                "value_score": row.get("value_score")  # If문 걸기
            }
            for row in data
        ]

        chain = select_prompt | llm | StrOutputParser()

        max_retries = 3
        retries = 0
        
        while retries < max_retries:
            try:
                st.write(f"\n--- {len(simplified_data)}개 후보 중 상위 키워드 선별을 요청합니다... --- (시도 {retries + 1}/{max_retries})")
                
                response_str = chain.invoke({
                    "data_list_str": json.dumps(simplified_data, ensure_ascii=False)
                })
                
                top_keywords_list = json.loads(response_str)
                top_keywords_set = set(top_keywords_list)

                final_data = [row for row in data if row.get("keyword") in top_keywords_set]
                
                all_keywords_set = {row.get("keyword") for row in data}
                backend_keywords_set = all_keywords_set - top_keywords_set
                backend_keywords_list = list(backend_keywords_set)

                st.success(f"\n최종 {len(final_data)}개 키워드를 선별했습니다. 탈락한 키워드 {len(backend_keywords_list)}개를 백엔드 키워드로 저장합니다.")
                status.update(label="키워드 선별 완료", state="complete", expanded=False)

                return {"data": final_data, "backend_keywords": backend_keywords_list}

            # 에러 발생 시
            except Exception as e:
                retries += 1
                st.warning(f"\n[Error] 상위 키워드 선별 중 에러가 발생했습니다: {e}")
                if retries < max_retries:
                    st.write(f"\n--- 재시도합니다... --- ({retries}/{max_retries})")
                else:
                    st.warning(f"\n[Error] 최대 재시도 횟수({max_retries}회)를 초과했습니다. LLM 호출에 실패했습니다.")
                    break

        # LLM 호출이 최종 실패했을 때 실행되는 대체 로직
        st.write("\n에러 발생으로 인해, value_score 기준 상위 30개를 대신 선택합니다.")
        
        data_copy = [d for d in data if d.get('relevance_category') in ['직접', '중간']]
        if not data_copy:
            data_copy = data

        sorted_data = sorted(data_copy, key=lambda x: x.get('value_score', 0), reverse=True)  # value_score 처리하기!
        final_data = sorted_data[:30]

        top_keywords_set = {row.get("keyword") for row in final_data}
        all_keywords_set = {row.get("keyword") for row in data}
        backend_keywords_set = all_keywords_set - top_keywords_set
        backend_keywords_list = list(backend_keywords_set)
        
        st.success(f"\n최종 {len(final_data)}개 키워드를 선별했습니다. 탈락한 키워드 {len(backend_keywords_list)}개를 백엔드 키워드로 저장합니다.")
        status.update(label="키워드 선별 완료", state="complete", expanded=False)

        return {"data": final_data, "backend_keywords": backend_keywords_list}

def information_refine(state: State):
    
    with st.status("PDF 내용을 요약합니다...", expanded=True) as status:
        
        
        all_extracted_text = state['product_information']
        
        # LLM을 사용하여 텍스트 요약
        full_text = "\n\n---\n\n".join(all_extracted_text)

        # LLM 초기화 및 요약 체인 구성
        llm = ChatOpenAI(model="gpt-4o", temperature=0)

        summarization_chain = summarization_prompt | llm

        # LLM 호출하여 요약 생성
        response = summarization_chain.invoke({"product_text": full_text})
        product_information = response.content
        st.success('PDF 내용을 요약합니다.')
        st.write(f"\n=== 요약된 제품 정보 ===\n{product_information}")
        status.update(label="PDF 요약 완료", state="complete", expanded=False)

        # State 업데이트
        return {"product_information": product_information}