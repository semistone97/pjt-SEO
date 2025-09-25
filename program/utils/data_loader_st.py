import pandas as pd
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from pypdf import PdfReader


def load_keywords_csv_streamlit(uploaded_files, product_name):
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
            messages.append(f"[Error] 파일 읽기 실패: {uploaded_file.name} ({e})")
            continue
        
        # 다형식 지원
        required_cols = None
        for cols in required_cols_variants:
            if set(cols).issubset(df.columns):
                required_cols = cols
                break
        
        # 컬럼 형식 맞추기
        if required_cols:
            df_required = df[required_cols].copy()
            df_required.columns = ['keyword', 'search_volume', 'competing_products']
            df_required['competing_products'] = df_required['competing_products'].fillna(0).astype(str).str.replace('>', '').astype('Int64')
            dfs.append(df_required)
            good_files.append(uploaded_file.name)
            messages.append(f"[Success] 파일 처리 완료: {uploaded_file.name}")
        else:
            messages.append(f"[Skipped] 컬럼 형식 불일치: {uploaded_file.name}")
    
    # 결과 반환
    if not good_files:
        return None, messages, []
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # RawData 저장
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f'{"_".join(product_name.split())}_keyword_raw_data.csv'
    combined_df.to_csv(output_file, index=False)
    
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
        # PDF 파일인지 확인
        if not uploaded_file.name.lower().endswith('.pdf'):
            messages.append(f"[Skipped] PDF 파일 아님: {uploaded_file.name}")
            continue
        
        # 파일 읽기 시도
        try:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            product_docs.append(Document(page_content=text, metadata={"source": uploaded_file.name}))
            product_information.append(text)
            messages.append(f"[Success] 읽어온 PDF 파일: {uploaded_file.name}")

        except Exception as e:
            messages.append(f"[Error] 파일 읽기 실패: {uploaded_file.name} ({e})")
            continue
    
    if not product_docs:
        return None, 'Product information not found', ["주어진 파일 중 PDF 파일을 읽을 수 없습니다. 리스팅 검증 과정을 생략합니다."]

    return product_docs, product_information, messages
