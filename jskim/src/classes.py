import pandas as pd
from langgraph.graph import MessagesState

class State(MessagesState):
    data: pd.DataFrame