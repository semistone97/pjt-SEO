from langgraph.graph import MessagesState
from langchain_core.documents import Document
from typing_extensions import List, Dict
from pydantic import Field

class State(MessagesState):
    # input data
    data: List[Dict]
    product_name: str
    product_docs: List[Document]
    product_information: str
    category: str
    
    # 백엔드용 키워드
    backend_keywords: List[str]
    
    # 실사용 키워드
    title_keyword: List[str] = Field(default_factory=list)
    bp_keyword: List[str] = Field(default_factory=list)
    description_keyword: List[str] = Field(default_factory=list)
    leftover: List[str] = Field(default_factory=list)
    
    # 결과물
    title: str = ''
    bp: List[str] = Field(default_factory=list)
    description: str = ''
    
    # 사용자 요청
    user_feedback: str = ''
    user_feedback_title: str = ''
    user_feedback_bp: str = ''
    user_feedback_description: str = ''

    # 상태
    status: str = ''