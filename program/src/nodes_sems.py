import json
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from src.states import State
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

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", '''
You are an expert in Amazon SEO and keyword analysis.
Your task is to classify the relevance of a list of keywords to a given product into one of four categories:
- '직접': Directly related to the product, indicating high purchase intent. Customers searching this are very likely to buy the product.
- '중간': Related to the product's function or use case, but less specific.
- '간접': Related to the broader product category or a peripheral use case, but not the product itself.
- '없음': Not relevant to the product at all.

Please return your response ONLY as a valid JSON array of objects, where each object has two keys: "keyword" and "relevance_category". Do not include any other text, explanation, or markdown.

Example format:
[
  {{"keyword": "chicken shredder", "relevance_category": "직접"}},
  {{"keyword": "kitchen gadget", "relevance_category": "중간"}},
  {{"keyword": "wedding gift", "relevance_category": "간접"}},
  {{"keyword": "car accessories", "relevance_category": "없음"}}
]
'''),
        ("human", '''
Product Name: {product_name}
Product Description: {product_description}

Please classify the following keywords and provide their relevance categories in the specified JSON format:
{keyword_list_str}
''')
    ])
    
    chain = prompt_template | llm | StrOutputParser()
    
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
    """
    print("--- [Node: select_top_keywords] - 상위 키워드 선별 및 백엔드 키워드 저장 시작 ---")
    
    data = state.get("data", [])

    if not data:
        print("데이터가 없어 키워드 선별을 건너뜁니다.")
        return {"data": [], "backend_keywords": []}

    # LLM에게 전달할 데이터 형식으로 변환
    simplified_data = [
        {
            "keyword": row.get("keyword"),
            "relevance_category": row.get("relevance_category"),
            "value_score": row.get("value_score")
        }
        for row in data
    ]

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", '''
You are a senior marketing strategist building a balanced and powerful keyword portfolio for an Amazon product. 
Your goal is to select the 30 most valuable keywords from the provided list to maximize both immediate sales and long-term market reach.

Each keyword has a 'relevance_category' ('직접', '중간', '간접') and a 'value_score' (representing opportunity).

Think of your selection as a strategic portfolio with three tiers. Your final list of 30 should be a strategic mix of these tiers:

1.  **Core Conversion Keywords (approx. 15-20 slots):**
    *   Select these from the **'직접'** category. These are your most important keywords for driving immediate sales.
    *   Within this category, choose the ones with the **highest `value_score`**.

2.  **Audience Expansion Keywords (approx. 5-10 slots):**
    *   Select these from the **'중간'** category. These keywords will help you reach a broader, but still highly relevant, audience.
    *   Prioritize those with the **highest `value_score`**.

3.  **Strategic Discovery Keywords (approx. 3-5 slots):**
    *   Select these from the **'간접'** category. Look for "hidden gems" here – keywords with an **exceptionally high `value_score`** that can bring in valuable, low-competition traffic.

**Your final goal is a balanced portfolio of 30 keywords.** Avoid simply filling the list only with '직접' keywords. The aim is to ensure both high conversion and wider audience discovery.

Return your response ONLY as a valid JSON array of strings, containing the 30 selected keywords. Do not include any other text, explanation, or markdown.

Example format:
[
  "keyword 1",
  "keyword 2",
  "keyword 3"
]
'''),
        ("human", '''
Here is the list of candidate keywords with their relevance and value scores. Please select the top 30.
{data_list_str}
''')
    ])

    chain = prompt_template | llm | StrOutputParser()

    print(f"LLM에게 {len(simplified_data)}개 후보 중 상위 30개 키워드 선별을 요청합니다...")

    try:
        response_str = chain.invoke({
            "data_list_str": json.dumps(simplified_data, ensure_ascii=False)
        })

        print("--- LLM으로부터 응답을 받았습니다. 최종 키워드 목록을 파싱합니다. ---")
        
        top_keywords_list = json.loads(response_str)
        top_keywords_set = set(top_keywords_list)

        # 상위 키워드 데이터 필터링
        final_data = [row for row in data if row.get("keyword") in top_keywords_set]
        
        # 백엔드 키워드 계산
        all_keywords_set = {row.get("keyword") for row in data}
        backend_keywords_set = all_keywords_set - top_keywords_set
        backend_keywords_list = list(backend_keywords_set)

        print(f"--- 최종 {len(final_data)}개 키워드를 선별했습니다. ---")
        print(f"--- {len(backend_keywords_list)}개의 백엔드 키워드를 저장합니다. ---")
        
        return {"data": final_data, "backend_keywords": backend_keywords_list}

    except Exception as e:
        print(f"상위 키워드 선별 중 에러가 발생했습니다: {e}")
        print("에러 발생으로 인해, value_score 기준 상위 30개를 대신 선택합니다.")
        
        # 대체 로직
        data_copy = [d for d in data if d.get('relevance_category') in ['직접', '중간']]
        if not data_copy:
            data_copy = data

        sorted_data = sorted(data_copy, key=lambda x: x.get('value_score', 0), reverse=True)
        final_data = sorted_data[:30]

        # 백엔드 키워드 계산 (대체 로직용)
        top_keywords_set = {row.get("keyword") for row in final_data}
        all_keywords_set = {row.get("keyword") for row in data}
        backend_keywords_set = all_keywords_set - top_keywords_set
        backend_keywords_list = list(backend_keywords_set)

        return {"data": final_data, "backend_keywords": backend_keywords_list}

# 참고: 김정수 님과 조성희 님이 만드실 다른 노드 함수(예: preprocess_data, build_listing 등)들이
# 이 파일이나 다른 파일에 추가될 수 있습니다.
