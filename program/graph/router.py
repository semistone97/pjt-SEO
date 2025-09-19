def status_router(state):
    
    current_status = state.get('status')
    print(f"DEBUG: status_router received status: '{current_status}'")  # 디버깅 추가

    if state.get('status') == 'ONGOING':
        return 'parse_user_feedback'
    
    return 'END'

def feedback_router(state):
    
    if str(state.get("user_feedback_title") or "").strip():
        return "regenerate_title"
    
    if str(state.get("user_feedback_bp") or "").strip():
        return "regenerate_bp"
    
    if str(state.get("user_feedback_description") or "").strip():
        return "regenerate_description"
    
    return 'user_input'
