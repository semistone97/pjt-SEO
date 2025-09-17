import pandas as pd
from dotenv import load_dotenv
from models.builder import build_graph

load_dotenv()

def main():

    # 데이터 로드
    raw_df = pd.read_csv('./data/raw_keywords.csv')[['Keywords', 'Search Volume', 'Competing Products']]
    raw_df.columns = ['keyword', 'search_volume', 'competing_products']
    raw_df['competing_products'] = raw_df['competing_products'].fillna(0)
    raw_df['competing_products'] = raw_df['competing_products'].astype(str).str.replace('>', '').astype('Int64')
    raw_df = raw_df.to_dict(orient='records')
    
    # 그래프 실행
    graph = build_graph()
    final_state = graph.invoke({
        'data': raw_df, 
        'product_name': 'Chicken Shredder',
        'category': 'Kitchen Gadgets',
        'product_description': 'it is a tool to rip chicken breasts. easy to use, and easy to dishwash'
    })

if __name__ == "__main__":
    main()