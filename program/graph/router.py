def status_router(state):

    if state.get('status') == 'ONGOING':
        return 'ONGOING'
    
    if state.get('status') == 'FINISHED':
        return 'FINISHED'
    
    return 'FINISHED'

def feedback_router(state):
    
    if str(state.get("user_feedback_title") or "").strip():
        return "regenerate_title"
    
    if str(state.get("user_feedback_bp") or "").strip():
        return "regenerate_bp"
    
    if str(state.get("user_feedback_description") or "").strip():
        return "regenerate_description"
    
    return 'user_input'

def no_pdf_router(state):
    
    if state.get('product_docs'):
        return 'yes_pdf'
    
    return 'no_pdf'