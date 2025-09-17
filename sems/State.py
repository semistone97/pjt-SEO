from typing import List, Dict, TypedDict

class State(TypedDict):
    product_name: str
    product_description: str
    data: List[Dict]
    backend_keywords: List[str] # 선별되지 않은 키워드들을 저장