from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import pandas as pd
from src.states import State
from src.funcs import preprocess_keywords
from src.scaler import scaler
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

# ===== Prompt Template =====
template = """
다음 키워드 리스트에 대해 조건을 적용하되, 삭제는 가능한 한 신중히 수행한다:

[조건]
1. 영어 이외의 외국어 키워드 삭제 권장. 
2. 같은 키워드의 단수형과 복수형 단어가 동시에 존재할 경우에만, 복수형 키워드를 제거함 
3. 오타로 판단되는 키워드의 경우, 원본 키워드가 존재할 경우 오타 키워드를 제거함

[데이터]
{data}

[출력]
{format_instructions}
"""

def keyword_process(state: State):
    
    llm = ChatOpenAI(model="gpt-5-mini")
    
    df = pd.DataFrame(state["data"])

    # 1. 사전 필터링
    filtered_series = preprocess_keywords(df['keyword'])

    # 2. 프롬프트 생성
    prompt = PromptTemplate.from_template(template)
    keyword_prompt = prompt.format(
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