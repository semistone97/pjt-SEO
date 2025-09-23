import shlex, sys
import pandas as pd
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from pypdf import PdfReader

def load_keywords_csv(product_name):
    print('키워드가 들어있는 CSV 파일들이 필요합니다')
    print('키워드 관련 파일 끌어오기')
    print('↓'*25)

    input_str = input()
    
    raw_paths = shlex.split(input_str)
    
    file_list = []
    for p in raw_paths:
        if p.startswith('/c/') or p.startswith('/C/'):
            p = 'C:' + p[2:]
        file_list.append(Path(p))
    
    # 들어올 csv 파일 형식들...(추가 가능)
    required_cols_variants = [
        ['Keywords', 'Search Volume', 'Competing Products'],
        ['Phrase', 'Search Volume', 'Keyword Sales']
    ]
    
    dfs = []
    good_files = []

    # 입력 파일 존재 여부 확인
    for file_path in file_list:
        
        # 파일 없음
        if not file_path.exists():
            print(f"[Warning] 파일 없음: {file_path}")
            continue
        
        # csv 아님
        if file_path.suffix.lower() != '.csv':
            print(f"[Skipped] CSV 파일 아님: {file_path}")
            continue
        
        # 파일 에러
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"[Error] 파일 읽기 실패: {file_path} ({e})")
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
            good_files.append(file_path.name)
            
        # 컬럼 불일치
        else:
            print(f"[Skipped] 컬럼 형식 불일치: {file_path}")

    # 형식 없으면 바로 종료
    if not good_files:
        print("\n[Warning] 형식에 맞는 CSV 파일이 없습니다.")
        sys.exit(1)

    combined_df = pd.concat(dfs, ignore_index=True)
    print("\n작업 완료:", good_files)

    # RawData 저장
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f'{"_".join(product_name.split())}_keyword_raw_data.csv'
    combined_df.to_csv(output_file, index=False)

    return combined_df.to_dict(orient='records')

def load_information_pdf():
    print('상품정보가 들어있는 PDF 파일들이 필요합니다')
    print('상품정보 관련 파일 끌어오기')
    print('없으면 빈 상태로 엔터')
    print('↓'*27)

    input_str = input()

    if not input_str:
        print('주어진 PDF 파일이 없습니다. 리스팅 검증 과정을 생략합니다.')
        return None, 'Product information not found'

    raw_paths = shlex.split(input_str)
    
    file_list = []
    for p in raw_paths:
        if p.startswith('/c/') or p.startswith('/C/'):
            p = 'C:' + p[2:]
        file_list.append(Path(p))
    
    product_docs: List[Document] = []
    product_information = []

    # 입력 파일 존재 여부 확인
    for file_path in file_list:
        
        # 파일 없음
        if not file_path.exists():
            print(f"[Warning] 파일 없음: {file_path}")
            continue
        
        # pdf 아님
        if file_path.suffix.lower() != '.pdf':
            print(f"[Skipped] PDF 파일 아님: {file_path}")
            continue
        
        # 파일 에러
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            product_docs.append(Document(page_content=text, metadata={"source": file_path}))
            product_information.append(text)
            print(f'읽어온 PDF 파일 : {file_path}')

        except Exception as e:
            print(f"[Error] 파일 읽기 실패: {file_path} ({e})")
            continue
    
    if not product_docs:
        print('주어진 파일 중 PDF 파일을 읽을 수 없습니다. 리스팅 검증 과정을 생략합니다.')
        return None, 'Product information not found'

    return product_docs, product_information
