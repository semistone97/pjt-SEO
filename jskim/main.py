import pandas as pd
from dotenv import load_dotenv
from src.graph_builder import build_graph
from src.scaler import scaler

def main():
    load_dotenv()

    # 데이터 로드
    raw_df = pd.read_csv('./data/raw_keywords.csv')[['Keywords', 'Search Volume', 'Competing Products']]
    raw_df.columns = ['keyword', 'search_volume', 'competing_products']
    raw_df['competing_products'] = raw_df['competing_products'].fillna(0)
    raw_df['competing_products'] = raw_df['competing_products'].astype(str).str.replace('>', '').astype('Int64')

    # 그래프 실행
    graph = build_graph()
    final_state = graph.invoke({"data": raw_df})
    df_cleaned = final_state["data"]

    # 스케일링 및 value_score 계산
    processed_df = scaler(df_cleaned)

    # 저장
    processed_df.to_csv('./data/processed_keywords.csv', index=False)
    print("완료: ./data/processed_keywords.csv")

if __name__ == "__main__":
    main()