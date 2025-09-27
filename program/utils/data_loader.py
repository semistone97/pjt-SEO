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
        ['Phrase', 'Search Volume', 'Keyword Sales'],
        ['Keyword Phrase', 'Search Volume', 'Keyword Sales']
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
        
        # 키워드 컬럼을 찾고, 존재하면 다른 컬럼은 옵션으로 처리
        keyword_col_names = [cols[0] for cols in required_cols_variants]
        found_keyword_col = next((col for col in keyword_col_names if col in df.columns), None)

        if found_keyword_col:
            # 'keyword' 컬럼을 필수로 포함하는 새 DataFrame 생성
            df_processed = pd.DataFrame()
            df_processed['keyword'] = df[found_keyword_col]

            # 'search_volume' 컬럼이 있으면 추가, 없으면 NA로 채움
            if 'Search Volume' in df.columns:
                df_processed['search_volume'] = pd.to_numeric(df['Search Volume'], errors='coerce')
            else:
                df_processed['search_volume'] = pd.NA

            # 'competing_products' 컬럼 처리
            competing_col = None
            if 'Competing Products' in df.columns:
                competing_col = 'Competing Products'
            elif 'Keyword Sales' in df.columns:
                competing_col = 'Keyword Sales'
            
            if competing_col:
                df_processed['competing_products'] = pd.to_numeric(df[competing_col].astype(str).str.replace('>', ''), errors='coerce').fillna(pd.NA)
            else:
                df_processed['competing_products'] = pd.NA
            
            # 최종적으로 데이터 타입 변환
            df_processed['search_volume'] = df_processed['search_volume'].astype('Int64')
            df_processed['competing_products'] = df_processed['competing_products'].astype('Int64')

            dfs.append(df_processed)
            good_files.append(file_path.name)
        
        # 컬럼 불일치
        else:
            print(f"[Skipped] 키워드 컬럼을 찾을 수 없음: {file_path}")

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
