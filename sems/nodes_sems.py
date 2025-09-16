import pandas as pd
import glob
from typing import Dict, List
# State.py에서 정의한 State를 가져옵니다.
from State import State
from dotenv import load_dotenv
load_dotenv()

# Langchain 관련 라이브러리를 가져옵니다.
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

# 이 코드는 pandas, langchain-openai, python-dotenv 라이브러리가 필요합니다.
# pip install pandas langchain-openai python-dotenv

# --- 노드 함수 정의 ---

def read_csv(state: State) -> Dict:
    """
    현재 폴더에서 'keyword_data_*.csv' 패턴의 파일을 찾아 읽어옵니다.
    파일 데이터를 state의 'data' 필드에 저장합니다.
    """
    print("--- [Node: read_csv] - CSV 파일을 읽기 시작합니다. ---")
    
    # 현재 폴더에서 패턴에 맞는 파일 검색
    # 상대경로를 사용하여 동일 폴더 내에서 파일을 찾습니다.
    file_pattern = 'keyword_data_*.csv'
    file_list = glob.glob(file_pattern)
    
    if not file_list:
        print(f"에러: 현재 폴더에 '{file_pattern}' 패턴의 파일이 없습니다.")
        return {"data": []}
    
    # 여러 파일이 발견될 경우, 첫 번째 파일을 사용
    if len(file_list) > 1:
        print(f"경고: 여러 개의 파일이 발견되었습니다. 첫 번째 파일인 '{file_list[0]}'을 사용합니다.")
    
    file_path = file_list[0]
    print(f"파일을 찾았습니다: {file_path}")
    
    try:
        # pandas를 사용하여 CSV 파일 읽기
        df = pd.read_csv(file_path)
        
        # DataFrame을 dictionary의 리스트 형태로 변환 (State 구조에 맞춤)
        data = df.to_dict(orient='records')
        
        print(f"성공: {file_path} 파일에서 {len(data)}개의 행을 읽었습니다.")
        
        return {"data": data}
        
    except Exception as e:
        print(f"파일을 읽는 중 에러가 발생했습니다: {e}")
        return {"data": []}

def generate_relevance(state: State) -> Dict:
    """
    LLM을 사용하여 제품 정보와 각 키워드 간의 관련성 점수를 계산합니다.
    """
    print("--- [Node: generate_relevance] - 관련성 점수 계산을 시작합니다. ---")
    
    product_name = state.get("product_name")
    product_description = state.get("product_description")
    data = state.get("data", [])

    if not data:
        print("데이터가 없어 관련성 계산을 건너뜁니다.")
        return {}
    
    if not product_name or not product_description:
        print("제품 이름 또는 설명이 없어 관련성 계산을 건너뜁니다. 모든 점수를 0으로 설정합니다.")
        for row in data:
            row['relevance_score'] = 0
        return {"data": data}

    # 요청하신 대로 LLM을 초기화합니다. 모델명은 'gpt-4-turbo'를 사용했습니다.
    llm = ChatOpenAI(model='gpt-4-turbo', temperature=0)

    # 데이터에서 키워드 리스트를 추출합니다.
    keywords = [row['keyword'] for row in data if 'keyword' in row]
    if not keywords:
        print("데이터에 'keyword' 필드가 없어 관련성 계산을 건너뜁니다.")
        return {}

    # LLM에게 역할을 부여하고, 출력 형식을 지정하는 프롬프트 템플릿
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", '''
You are an expert in Amazon SEO and keyword analysis.
Your task is to evaluate the relevance of a list of keywords to a given product.
Provide a relevance score from 0 (not relevant at all) to 100 (perfectly relevant).
The score should reflect how likely a customer searching for that keyword is to purchase the given product.

Consider the product's name, description, and primary function.

Please return your response ONLY as a valid JSON array of objects, where each object has two keys: "keyword" and "relevance_score". Do not include any other text, explanation, or markdown.

Example format:
[
  {{"keyword": "example keyword 1", "relevance_score": 95}},
  {{"keyword": "example keyword 2", "relevance_score": 20}}
]
'''),
        ("human", '''
Product Name: {product_name}
Product Description: {product_description}

Please evaluate the following keywords and provide their relevance scores in the specified JSON format:
{keyword_list_str}
''')
    ])
    
    chain = prompt_template | llm | StrOutputParser()
    
    print(f"LLM에게 {len(keywords)}개 키워드의 관련성 점수 계산을 요청합니다...")
    
    try:
        # 키워드 리스트를 JSON 문자열로 변환하여 프롬프트에 전달
        response_str = chain.invoke({
            "product_name": product_name,
            "product_description": product_description,
            "keyword_list_str": json.dumps(keywords)
        })
        
        print("--- LLM으로부터 응답을 받았습니다. 점수를 파싱합니다. ---")
        
        # LLM의 응답(JSON 문자열)을 파싱
        scores = json.loads(response_str)
        
        # 점수를 빠르게 찾기 위해 딕셔너리 형태로 변환
        score_map = {item['keyword']: item['relevance_score'] for item in scores}
        
        # 기존 데이터에 'relevance_score'를 추가
        for row in data:
            if 'keyword' in row:
                row['relevance_score'] = score_map.get(row['keyword'], 0) # 점수가 없는 경우 0점 부여
        
        print("--- 모든 키워드에 관련성 점수를 부여했습니다. ---")
        return {"data": data}

    except json.JSONDecodeError:
        print(f"에러: LLM의 응답을 파싱하는데 실패했습니다. 응답 내용: \n{response_str}")
        for row in data:
            row['relevance_score'] = -1 # 에러 발생 시 -1점 부여
        return {"data": data}
    except Exception as e:
        print(f"관련성 계산 중 에러가 발생했습니다: {e}")
        for row in data:
            row['relevance_score'] = -1
        return {"data": data}

def keyword_sorting(state: State) -> Dict:
    print("--- [Node: keyword_sorting] - 키워드 정렬을 시작합니다. ---")
    # 이 노드는 다음 단계에서 구현합니다.
    data = state.get('data', [])
    if not data:
        print("데이터가 없어 정렬을 건너뜁니다.")
        return {}
    # TODO: 정렬 로직 추가
    return {"data": data}

# --- 아래는 테스트를 위한 코드입니다 ---
if __name__ == '__main__':
    # .env 파일 로드를 위해 python-dotenv가 필요할 수 있습니다.
    # from dotenv import load_dotenv
    # load_dotenv()

    # 테스트를 위해 임시 'keyword_data_2024.csv' 파일을 생성합니다.
    dummy_data = {
        'keyword': ['chicken shredder', 'meat shredder', 'pulled pork', 'kitchen gadget'],
        'search_volume': [25000, 15000, 30000, 5000],
        'cpr': [800, 500, 1200, 200]
    }
    pd.DataFrame(dummy_data).to_csv('keyword_data_2024.csv', index=False)
    
    # --- 1. 초기 State 정의 ---
    # 실제 실행 시에는 product_name, product_description을 설정해야 합니다.
    initial_state = {
        "product_name": "KitchenMaster Chicken Shredder",
        "product_description": "A tool to easily shred cooked chicken, beef, or pork. Features a non-slip base and easy-to-grip handles. Perfect for preparing tacos, enchiladas, and salads.",
        "category": "Kitchen Gadgets",
        "data": []
    }
    
    # --- 2. read_csv 노드 실행 ---
    read_result = read_csv(initial_state)
    state_after_read = {**initial_state, **read_result}

    # --- 3. generate_relevance 노드 실행 ---
    # .env 파일에 OPENAI_API_KEY가 설정되어 있어야 합니다.
    print("\n--- generate_relevance 노드 테스트를 시작합니다. ---")
    relevance_result = generate_relevance(state_after_read)
    state_after_relevance = {**state_after_read, **relevance_result}

    # --- 4. 결과 출력 ---
    if state_after_relevance.get('data'):
        print("\n--- 관련성 점수 계산 후 데이터 ---")
        # 보기 쉽게 DataFrame으로 변환하여 출력
        final_df = pd.DataFrame(state_after_relevance['data'])
        print(final_df)
