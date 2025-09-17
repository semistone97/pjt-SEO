from typing_extensions import List, Dict, TypedDict, Annotated
from pydantic import Field, BaseModel
from langgraph.graph import MessagesState
from pydantic.types import StringConstraints


# 데이터 들어갈 State
class State(MessagesState):
    data: List[Dict]
    product_name: str
    product_description: str
    category: str
    title_keyword: List[str] = Field(default_factory=list)
    bp_keyword: List[str] = Field(default_factory=list)
    description_keyword: List[str] = Field(default_factory=list)
    leftover: List[str] = Field(default_factory=list)
    title: str = ""
    bp: List[str] = Field(default_factory=list)
    description: str = ""

# 결과물 형식 지정
class KeywordDistribute(BaseModel):
    title_keyword: List[str] = Field(..., description='Title에 들어갈 키워드들')
    bp_keyword: List[str] = Field(..., description='Bullet Point에 들어갈 키워드들')
    description_keyword: List[str] = Field(..., description='Description에 들어갈 키워드들')
    leftover: List[str] = Field(..., description='사용되지 않은 키워드들')
    
class TitleOutput(BaseModel):
    title: Annotated[
        str,
        StringConstraints(min_length=1, max_length=200),
        Field(description="최대 200자까지 허용")
    ]
    
class BPOutput(BaseModel):
    bp: Annotated[
        List[
            Annotated[
                str, 
                StringConstraints(min_length=1, max_length=250)
            ]
        ],
        Field(..., description="각 항목 최대 250자")
    ]
    
class DescriptionOutput(BaseModel):    
    description: Annotated[
        str,
        StringConstraints(min_length=1, max_length=2000),
        Field(description="최대 2000자까지 허용")
    ]