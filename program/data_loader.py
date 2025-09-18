import os
import pandas as pd

def load_csv(required_cols=None):
    if required_cols is None:
        required_cols = ['Keywords', 'Search Volume', 'Competing Products']

    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if set(required_cols).issubset(df.columns):
                df = df[required_cols].copy()
                df.columns = ['keyword', 'search_volume', 'competing_products']
                df['competing_products'] = df['competing_products'].fillna(0)
                df['competing_products'] = df['competing_products'].astype(str).str.replace('>', '').astype('Int64')
                return df.to_dict(orient='records'), file
            
        except Exception as e:
            print(f"파일 {file} 읽기 오류:", e)

    return None, None
