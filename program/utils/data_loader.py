from pathlib import Path
import shlex
import pandas as pd

def load_csv(product_name):
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
    
    required_cols = ['Keywords', 'Search Volume', 'Competing Products']
    dfs = []
    good_files = []

    # 입력 파일 존재 여부 확인
    for file_path in file_list:
        if not file_path.exists():
            print(f"[Warning] 파일 없음: {file_path}")
            continue
        if file_path.suffix.lower() != '.csv':
            print(f"[Skipped] CSV 파일 아님: {file_path}")
            continue

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"[Error] 파일 읽기 실패: {file_path} ({e})")
            continue

        if set(required_cols).issubset(df.columns):
            df_required = df[required_cols].copy()
            df_required.columns = ['keyword', 'search_volume', 'competing_products']
            df_required['competing_products'] = df_required['competing_products'].fillna(0).astype(str).str.replace('>', '').astype('Int64')
            dfs.append(df_required)
            good_files.append(file_path.name)
        else:
            print(f"[Skipped] 컬럼 형식 불일치: {file_path}")

    if not good_files:
        print("\n[Warning] 형식에 맞는 CSV 파일이 없습니다.")
        return None

    combined_df = pd.concat(dfs, ignore_index=True)
    print("\n작업 완료:", good_files)

    # output 경로 설정
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f'{"_".join(product_name.split())}_keyword_raw_data.csv'
    combined_df.to_csv(output_file, index=False)

    return combined_df.to_dict(orient='records')