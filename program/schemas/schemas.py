from typing_extensions import List, Annotated
from pydantic import Field, BaseModel
from pydantic.types import StringConstraints

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