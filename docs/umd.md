# pjt-SEO 유스케이스 다이어그램 (UCD)

이 문서는 `pjt-SEO` 시스템의 사용자 상호작용을 정의하는 유스케이스 다이어그램입니다.
아래 Mermaid 코드를 복사하여 Markdown을 지원하는 에디터나 [Mermaid.live](https://mermaid.live/)와 같은 온라인 툴에 붙여넣으면 다이어그램을 시각적으로 확인할 수 있습니다.

## Mermaid 코드

```mermaid
---
title: pjt-SEO 유스케이스 다이어그램 (UCD)
---
use-case
    actor "상품 리스팅 담당자" as User

    rectangle "pjt-SEO 시스템" {
        use-case "리스팅 초안 생성" as Generate
        use-case "키워드 데이터 업로드" as UploadCSV
        use-case "상품 정보(PDF) 업로드" as UploadPDF
        use-case "생성된 리스팅 검토" as Review
        use-case "리스팅 수정 요청 (피드백)" as Feedback
        use-case "사실성 검증" as Verify
    }

    actor "LLM" as LargeLanguageModel
    actor "Helium10" as KeywordTool

    User -- (Generate)
    User -- (Review)
    User -- (Feedback)

    (Generate) .> (UploadCSV) : <<include>>
    (Generate) .> (Verify) : <<extend>>
    (Verify) .> (UploadPDF) : <<include>>

    (Generate) -- LargeLanguageModel
    (UploadCSV) -- KeywordTool
```

## 다이어그램 설명

### 액터 (Actor)
- **상품 리스팅 담당자 (User)**: 시스템의 주 사용자로, 리스팅 생성을 요청하고 피드백을 제공합니다.
- **LLM (LargeLanguageModel)**: 리스팅 텍스트 생성을 담당하는 외부 AI 모델입니다.
- **Helium10 (KeywordTool)**: 키워드 데이터를 제공하는 외부 전문 툴입니다.

### 유스케이스 (Use Case)
- **리스팅 초안 생성**: 시스템의 핵심 기능으로, 키워드와 상품 정보를 바탕으로 리스팅 초안을 만듭니다.
- **키워드 데이터 업로드**: 리스팅 생성을 위해 반드시 필요한(`<<include>>`) 선행 작업입니다. Helium10과 같은 외부 툴로부터 데이터를 받습니다.
- **상품 정보(PDF) 업로드**: '사실성 검증'이라는 확장 기능을 트리거하는 선택적 작업입니다.
- **사실성 검증**: PDF가 업로드되었을 경우에만 수행되는(`<<extend>>`) 확장 기능입니다.
- **생성된 리스팅 검토**: 사용자가 생성된 결과물을 확인하는 과정입니다.
- **리스팅 수정 요청 (피드백)**: 검토 후, 사용자가 원하는 대로 결과물을 수정하도록 시스템에 요청하는 과정입니다. 이 요청은 다시 '리스팅 초안 생성' 프로세스(또는 일부)를 트리거합니다.
