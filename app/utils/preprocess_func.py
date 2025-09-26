import re
import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler

# LLM 필터링을 위한 라이브러리 추가
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from prompts.prompt_preprocess import filter_prompt
from schemas.schema import FilteredKeywords
from utils.config_loader import config

def clean_keyword_column(df: pd.DataFrame) -> pd.DataFrame:
    
    if 'keyword' not in df.columns:
        return df.copy()

    df_copy = df.copy()
    valid_mask = df_copy['keyword'].apply(lambda x: bool(re.fullmatch(r"[A-Za-z0-9 &'().-]+", str(x))))
    df_copy = df_copy[valid_mask].copy()
    df_copy.drop_duplicates(subset=['keyword'], inplace=True)
    df_copy.reset_index(drop=True, inplace=True)
    
    return df_copy

def filter_by_llm(df: pd.DataFrame) -> pd.DataFrame:
    
    if df.empty:
        return df

    try:
        llm = ChatOpenAI(model=config['llm_keyword']['model'], temperature=float(config['llm_keyword']['temperature']))
        
        prompt = filter_prompt.invoke(
            {
                'data': df['keyword'].tolist()
            }
        )
        
        structured_llm = llm.with_structured_output(FilteredKeywords)
        res = structured_llm.invoke(prompt)

        cleaned_keywords = set(res.keywords)

        filtered_df = df[df['keyword'].isin(cleaned_keywords)].copy()
        st.write(f"LLM 필터링 후 {len(filtered_df)}개 키워드 남음.")
        
        return filtered_df
    
    except Exception as e:
        st.warning(f"LLM 필터링 중 오류가 발생하여 해당 단계를 건너뜁니다: {e}")
        return df

def clean_sv_column(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    
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