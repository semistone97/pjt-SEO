from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from prompts.prompts_preprocess import filter_prompt
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import pandas as pd
from schemas.states import State
from utils.funcs import preprocess_keywords, scaler
from dotenv import load_dotenv

load_dotenv()


# ===== ResponseSchema =====
response_schemas = [
    ResponseSchema(
        name="keywords",
        description="조건을 적용한 키워드 리스트, 문자열 리스트 또는 dict 리스트 가능"
    )
]
parser = StructuredOutputParser.from_response_schemas(response_schemas)

def keyword_process(state: State):
    
    llm = ChatOpenAI(model="gpt-5-mini")
    
    df = pd.DataFrame(state["data"])

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
    return {"data": processed_df}