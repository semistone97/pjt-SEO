import pandas as pd
import re

def preprocess_keywords(series: pd.Series) -> pd.Series:
    """영어 알파벳/숫자/특수문자만 허용"""
    series = series[series.apply(lambda x: bool(re.fullmatch(r"[A-Za-z0-9 &'().-]+", str(x))))]
    return series.drop_duplicates().reset_index(drop=True)
