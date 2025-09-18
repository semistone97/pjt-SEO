import json
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from prompts.prompts_preprocess import relevance_prompt, select_prompt
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from schemas.states import State
from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(model='gpt-4-turbo', temperature=0)

# --- 노드 함수 정의 ---

def generate_relevance(state: State) -> Dict:
    """
    LLM을 사용하여 각 키워드의 연관성을 4가지 카테고리(직접, 중간, 간접, 없음)로 분류합니다.
    """
    print("--- [Node: generate_relevance] - 연관성 분류 시작 ---")
    
    product_name = state.get("product_name")
    product_description = state.get("product_description")
    data = state.get("data", [])

    # 데이터가 비어있으면 중단
    if not data:
        print("데이터가 없어 연관성 분류를 건너뜁니다.")
        return {}

    # DataFrame을 dict 리스트로 변환 (만약 DataFrame으로 들어올 경우)
    if isinstance(data, pd.DataFrame):
        data = data.to_dict(orient='records')

    keywords = [row['keyword'] for row in data if 'keyword' in row]
    if not keywords:
        print("키워드가 없어 연관성 분류를 건너뜁니다.")
        return {}

    
    chain = relevance_prompt | llm | StrOutputParser()
    
    print(f"LLM에게 {len(keywords)}개 키워드의 연관성 분류를 요청합니다...")
    
    try:
        response_str = chain.invoke({
            "product_name": product_name,
            "product_description": product_description,
            "keyword_list_str": json.dumps(keywords, ensure_ascii=False)
        })
        
        print("--- LLM으로부터 응답을 받았습니다. 카테고리를 파싱합니다. ---")
        
        classifications = json.loads(response_str)
        
        classification_map = {item['keyword']: item['relevance_category'] for item in classifications}
        
        for row in data:
            if 'keyword' in row:
                row['relevance_category'] = classification_map.get(row['keyword'], '없음')
        
        print("--- 모든 키워드에 연관성 카테고리를 부여했습니다. ---")
        return {"data": data}

    except Exception as e:
        print(f"연관성 분류 중 에러가 발생했습니다: {e}")
        for row in data:
            row['relevance_category'] = '분류 실패'
        return {"data": data}

def select_top_keywords(state: State) -> Dict:
    """
    LLM을 사용해 상위 30개 키워드를 선별하고, 나머지는 backend_keywords에 저장합니다.
    실패 시 최대 3회 재시도하고, 최종 실패 시 대체 로직을 실행합니다.
    """
    print("--- [Node: select_top_keywords] - 상위 키워드 선별 및 백엔드 키워드 저장 시작 ---")
    
    data = state.get("data", [])

    if not data:
        print("데이터가 없어 키워드 선별을 건너뜁니다.")
        return {"data": [], "backend_keywords": []}

    simplified_data = [
        {
            "keyword": row.get("keyword"),
            "relevance_category": row.get("relevance_category"),
            "value_score": row.get("value_score")
        }
        for row in data
    ]

    chain = select_prompt | llm | StrOutputParser()

    max_retries = 3
    retries = 0
    
    while retries < max_retries:
        try:
            print(f"LLM에게 {len(simplified_data)}개 후보 중 상위 30개 키워드 선별을 요청합니다... (시도 {retries + 1}/{max_retries})")
            
            response_str = chain.invoke({
                "data_list_str": json.dumps(simplified_data, ensure_ascii=False)
            })

            print("--- LLM으로부터 응답을 받았습니다. 최종 키워드 목록을 파싱합니다. ---")
            
            top_keywords_list = json.loads(response_str)
            top_keywords_set = set(top_keywords_list)

            final_data = [row for row in data if row.get("keyword") in top_keywords_set]
            
            all_keywords_set = {row.get("keyword") for row in data}
            backend_keywords_set = all_keywords_set - top_keywords_set
            backend_keywords_list = list(backend_keywords_set)

            print(f"--- 최종 {len(final_data)}개 키워드를 선별했습니다. ---")
            print(f"--- {len(backend_keywords_list)}개의 백엔드 키워드를 저장합니다. ---")
            
            return {"data": final_data, "backend_keywords": backend_keywords_list}

        except Exception as e:
            retries += 1
            print(f"상위 키워드 선별 중 에러가 발생했습니다: {e}")
            if retries < max_retries:
                print(f"재시도합니다... ({retries}/{max_retries})")
            else:
                print(f"최대 재시도 횟수({max_retries}회)를 초과했습니다. LLM 호출에 최종 실패했습니다.")
                break # while 루프 탈출

    # LLM 호출이 최종 실패했을 때 실행되는 대체 로직
    print("에러 발생으로 인해, value_score 기준 상위 30개를 대신 선택합니다.")
    
    data_copy = [d for d in data if d.get('relevance_category') in ['직접', '중간']]
    if not data_copy:
        data_copy = data

    sorted_data = sorted(data_copy, key=lambda x: x.get('value_score', 0), reverse=True)
    final_data = sorted_data[:30]

    top_keywords_set = {row.get("keyword") for row in final_data}
    all_keywords_set = {row.get("keyword") for row in data}
    backend_keywords_set = all_keywords_set - top_keywords_set
    backend_keywords_list = list(backend_keywords_set)

    return {"data": final_data, "backend_keywords": backend_keywords_list}