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
                StringConstraints(min_length=150, max_length=250)
            ]
        ],
        Field(
            ..., 
            max_items=7, 
            min_items=5,
            description="각 항목별 최소 150자, 최대 250자, 리스트 길이 최소 5개, 최대 7개", 
        )
    ]
    
class DescriptionOutput(BaseModel):    
    description: Annotated[
        str,
        StringConstraints(min_length=1, max_length=2000),
        Field(description="최대 2000자까지 허용")
    ]
    
class Feedback(BaseModel):
    title: str = Field(
        default="",
        description="사용자가 Title에 대해 요청한 수정사항. 수정사항이 없다면 빈 문자열로 반환."
    )
    bp: str = Field(
        default="",
        description="사용자가 Bullet Points 전체에 대해 요청한 수정사항. 수정사항이 없다면 빈 문자열로 반환."
    )
    description: str = Field(
        default="",
        description="사용자가 Description에 대해 요청한 수정사항. 수정사항이 없다면 빈 문자열로 반환."
    )
