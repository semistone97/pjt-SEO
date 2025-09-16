from typing import List, Dict, TypedDict, Literal

# 각 키워드에 대한 라벨과 연관성 점수를 포함할 데이터 구조
class State(TypedDict):
	product_name: str
	product_description: str
	category: str
	data: list[Dict]