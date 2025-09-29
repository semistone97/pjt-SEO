import pandas as pd
from typing import List
from langchain_core.documents import Document
from pypdf import PdfReader


def load_keywords_csv_streamlit(uploaded_files):
    """Streamlit용 키워드 CSV 로더"""
    if not uploaded_files:
        return None
    
    # 들어올 csv 파일 형식들...(추가 가능)
    required_cols_variants = [
        ['Keywords', 'Search Volume', 'Competing Products'],
        ['Phrase', 'Search Volume', 'Keyword Sales']
    ]
    
    dfs = []
    good_files = []
    messages = []

    # 업로드된 파일들 처리
    for uploaded_file in uploaded_files:
        
        # 파일 읽기 시도
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            messages.append(f"파일 읽기 실패: {uploaded_file.name} ({e})")
            continue
        
        # 키워드 컬럼을 찾고, 존재하면 다른 컬럼은 옵션으로 처리 (대소문자 구분 없음)
        df_col_map = {col.lower(): col for col in df.columns}
        keyword_col_names = [variant[0] for variant in required_cols_variants]
        
        found_keyword_col_original_name = None
        for name in keyword_col_names:
            if name.lower() in df_col_map:
                found_keyword_col_original_name = df_col_map[name.lower()]
                break

        if found_keyword_col_original_name:
            df_processed = pd.DataFrame()
            df_processed['keyword'] = df[found_keyword_col_original_name]

            # Search Volume (optional)
            sv_col_name = df_col_map.get('search volume')
            if sv_col_name:
                df_processed['search_volume'] = pd.to_numeric(df[sv_col_name], errors='coerce')
            else:
                df_processed['search_volume'] = pd.NA

            # Competing Products / Keyword Sales (optional)
            cp_col_name = df_col_map.get('competing products') or df_col_map.get('keyword sales')
            if cp_col_name:
                df_processed['competing_products'] = pd.to_numeric(df[cp_col_name].astype(str).str.replace('>', ''), errors='coerce')
            else:
                df_processed['competing_products'] = pd.NA

            # Convert to nullable integer type
            df_processed['search_volume'] = df_processed['search_volume'].astype('Int64')
            df_processed['competing_products'] = df_processed['competing_products'].astype('Int64')
            
            dfs.append(df_processed)
            good_files.append(uploaded_file.name)
            messages.append(f"파일 처리 완료: {uploaded_file.name}")
        else:
            messages.append(f"컬럼 형식 불일치: {uploaded_file.name} (키워드 컬럼 부재)")
    
    # 결과 반환
    if not good_files:
        return None, messages, []
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    return combined_df.to_dict(orient='records'), messages, good_files

def load_information_pdf_streamlit(uploaded_files):
    """Streamlit용 PDF 로더"""
    if not uploaded_files:
        return None, 'Product information not found', ["주어진 PDF 파일이 없습니다. 리스팅 검증 과정을 생략합니다."]
    
    product_docs: List[Document] = []
    product_information = []
    messages = []

    # 업로드된 파일들 처리
    for uploaded_file in uploaded_files:

        # 파일 읽기 시도
        try:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            product_docs.append(Document(page_content=text, metadata={"source": uploaded_file.name}))
            product_information.append(text)
            messages.append(f"읽어온 PDF 파일: {uploaded_file.name}")

        except Exception as e:
            messages.append(f"파일 읽기 실패: {uploaded_file.name} ({e})")
            continue
    
    if not product_docs:
        return None, 'Product information not found', ["PDF 파일을 읽을 수 없습니다. 리스팅 검증 과정을 생략합니다."]

    return product_docs, product_information, messages
