import streamlit as st

st.title('Hello World!')

st.text('is the file uploader')
x=st.text_input('number? ')
# uploaded = st.file_uploader("CSV 파일을 올려줘", type=["csv"])
files = st.file_uploader("CSV 파일들을 올려줘 (여러 개 가능)", type=["csv"], accept_multiple_files=True)
st.write(f'## number = {x}')