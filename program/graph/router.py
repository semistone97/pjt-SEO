def status_router(state):
    
    if state.get('status') == 'ONGOING':
        return 'parse_user_feedback'
    return 'END'

def feedback_router(state):
    
    if state.get("user_feedback_title", "").strip():
        return "generate_title"

    if state.get("user_feedback_bp", "").strip():
        return "generate_bp"

    if state.get("user_feedback_description", "").strip():
        return "generate_description"

    return 'user_input'
