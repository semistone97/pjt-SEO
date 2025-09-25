import re, sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from schemas.global_state import State

# LLM 필터링을 위한 라이브러리 추가
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from prompts.prompt_preprocess import filter_prompt
from utils.config_loader import config

def clean_keyword_column(df: pd.DataFrame) -> pd.DataFrame:
    """키워드 컬럼의 유효성을 검사하고 중복을 제거하여 행을 필터링합니다."""
    if 'keyword' not in df.columns:
        return df.copy()

    df_copy = df.copy()
    valid_mask = df_copy['keyword'].apply(lambda x: bool(re.fullmatch(r"[A-Za-z0-9 &'().-]+", str(x))))
    df_copy = df_copy[valid_mask].copy()
    df_copy.drop_duplicates(subset=['keyword'], inplace=True)
    df_copy.reset_index(drop=True, inplace=True)
    return df_copy

def filter_by_llm(df: pd.DataFrame) -> pd.DataFrame:
    """LLM을 사용하여 의미적으로 부적절한 키워드를 필터링합니다."""
    print("\n--- LLM 기반 키워드 필터링 시작... ---")
    if df.empty:
        return df

    try:
        llm = ChatOpenAI(model=config['llm_keyword']['model'], temperature=float(config['llm_keyword']['temperature']))
        
        response_schemas = [ResponseSchema(name="keywords", description="조건을 적용한 키워드 리스트")]
        parser = StructuredOutputParser.from_response_schemas(response_schemas)

        keyword_prompt = filter_prompt.format(
            data=df['keyword'].tolist(),
            format_instructions=parser.get_format_instructions()
        )

        res = llm.invoke([{"role": "user", "content": keyword_prompt}])
        structured = parser.parse(res.content)
        
        raw_keywords = structured.get("keywords", [])
        if raw_keywords and isinstance(raw_keywords[0], dict):
            cleaned_keywords = {k.get('keyword') for k in raw_keywords if 'keyword' in k}
        else:
            cleaned_keywords = set(raw_keywords)

        filtered_df = df[df['keyword'].isin(cleaned_keywords)].copy()
        print(f"LLM 필터링 후 {len(filtered_df)}개 키워드 남음.")
        
        return filtered_df
    except Exception as e:
        print(f"\n[Warning] LLM 필터링 중 오류가 발생하여 해당 단계를 건너뜁니다: {e}")
        return df # 에러 발생 시, 필터링을 건너뛰고 원본 데이터프레임 반환

def clean_sv_column(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Search Volume 컬럼을 정제하고, 결측치는 하위 10% 값으로 채웁니다."""
    df_copy = df.copy()
    col_name = 'search_volume'
    if col_name not in df_copy.columns:
        df_copy[col_name] = 0
        imputed_mask = pd.Series([False] * len(df_copy), index=df_copy.index)
        return df_copy, imputed_mask

    series = pd.to_numeric(
        df_copy[col_name].astype(str).str.replace(r'[^\d.]', '', regex=True),
        errors='coerce'
    )
    
    imputed_mask = series.isnull()

    if imputed_mask.any():
        percentile_10 = series.quantile(0.1)
        series.fillna(percentile_10, inplace=True)

    df_copy[col_name] = series.fillna(0).astype(int)
    return df_copy, imputed_mask

def clean_cp_column(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Competing Products 컬럼을 정제하고, 결측치는 평균값으로 채웁니다."""
    df_copy = df.copy()
    col_name = 'competing_products'
    if col_name not in df_copy.columns:
        df_copy[col_name] = 0
        imputed_mask = pd.Series([False] * len(df_copy), index=df_copy.index)
        return df_copy, imputed_mask

    series = pd.to_numeric(
        df_copy[col_name].astype(str).str.replace(r'[^\d.]', '', regex=True),
        errors='coerce'
    )

    imputed_mask = series.isnull()

    if imputed_mask.any():
        mean_val = series.mean()
        series.fillna(mean_val, inplace=True)

    df_copy[col_name] = series.fillna(0).astype(int)
    return df_copy, imputed_mask

def scaler_and_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    'is_imputed'가 False인 행을 기준으로 Scaler를 학습시키고,
    전체 행에 적용하여 value_score를 계산합니다.
    """
    df_copy = df.copy()
    scale_cols = ['search_volume', 'competing_products']

    real_data = df_copy[df_copy['is_imputed'] == False]
    
    if not real_data.empty and len(real_data) > 1:
        ss = StandardScaler()
        ss.fit(real_data[scale_cols])
        df_copy[scale_cols] = ss.transform(df_copy[scale_cols])
    else:
        df_copy[scale_cols] = 0

    sv_scaled = df_copy['search_volume'] - df_copy['search_volume'].min()
    cp_scaled = df_copy['competing_products'] - df_copy['competing_products'].min()
    
    df_copy['value_score'] = (sv_scaled + 1) / (cp_scaled + 1)
    
    return df_copy

# 삭제 예정.
# def preprocess_data(state: State):
#     if not state['data']:
#         print("\n[Skipped] 데이터가 없어 키워드 정제를 종료합니다.")
#         return sys.exit(1)
    
#     try:
#         """
#         데이터프레임 전체에 대해 정제, 스케일링, 점수 계산을 순차적으로 수행합니다.
#         """
#         print("\n--- 데이터 정제 및 스케일링 시작... ---")
#         df = pd.DataFrame(state["data"])
#         df = clean_keyword_column(df)
#         df = filter_by_llm(df)
#         df, sv_imputed_mask = clean_sv_column(df)
#         df, cp_imputed_mask = clean_cp_column(df)

#         df['is_imputed'] = sv_imputed_mask | cp_imputed_mask

#         df = scaler_and_score(df)

#         df.drop(columns=['is_imputed'], inplace=True, errors='ignore')
#         processed_df = df.to_dict(orient='records')

#         print(f"\n최종 {len(processed_df)}개 키워드 정제 및 점수 계산 완료.")
#         return {'data': processed_df}
#     except Exception as e:
#         print(f"\n[Error] 키워드 정제 중 에러가 발생했습니다: {e}")
#         return {}
