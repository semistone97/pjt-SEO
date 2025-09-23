import sys
from langgraph.graph import END

def status_router(state):

    if state.get('status') == 'ONGOING':
        return 'parse_user_feedback'
    
    if state.get('status') == 'FINISHED':
        return END
    
    if state.get('status') == 'ERROR':
        sys.exit(1)
    
    return END

def feedback_router(state):
    
    if str(state.get("user_feedback_title") or "").strip():
        return "regenerate_title"
    
    if str(state.get("user_feedback_bp") or "").strip():
        return "regenerate_bp"
    
    if str(state.get("user_feedback_description") or "").strip():
        return "regenerate_description"
    
    return 'user_input'
