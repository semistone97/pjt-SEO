import pandas as pd
from langgraph.graph import MessagesState
from typing_extensions import List, Dict
from pydantic import Field
from langgraph.graph import MessagesState

class KeywordState(MessagesState):
    data: pd.DataFrame
    
class State(MessagesState):
    data: List[Dict]
    product_name: str
    product_description: str
    backend_keywords: List[str]
    category: str
    title_keyword: List[str] = Field(default_factory=list)
    bp_keyword: List[str] = Field(default_factory=list)
    description_keyword: List[str] = Field(default_factory=list)
    leftover: List[str] = Field(default_factory=list)
    title: str = ""
    bp: List[str] = Field(default_factory=list)
    description: str = ""
