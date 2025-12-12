from flask import Blueprint, request, jsonify

assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/query', methods=['POST'])
def query():
    data = request.json
    user_query = data.get('query', '').lower()
    
    response = {
        "text": "I can help you with expiration data, scheduling, and defect inspection.",
        "action": None,
        "data": None
    }
    
    import re

    # 1. Vision / Inspection Intents
    if any(k in user_query for k in ["analyze", "image", "check", "inspect", "defect", "camera", "photo"]):
        if "history" in user_query and "uid" in user_query:
            # "Show inspection history for UID 123"
            match = re.search(r'uid\s*[:#]?\s*(\w+)', user_query)
            if match:
                uid = match.group(1)
                response["text"] = f"Here is the inspection history for UID {uid}."
                response["action"] = "open_inspection_history"
                response["data"] = {"uid": uid}
            else:
                 response["text"] = "Please specify the UID to view inspection history."
        else:
            response["text"] = "Please upload the image of the component using the camera icon below, and I will analyze it for defects."

    # 2. Expiry / Buckets Intents
    elif "top" in user_query and ("7" in user_query or "30" in user_query):
        response["text"] = "Here are the top lots expiring in the next 7-30 days."
        response["action"] = "open_bucket"
        response["data"] = {"bucket_id": "7-30"}
        
    elif "expired" in user_query or "overdue" in user_query:
        response["text"] = "Showing you the list of already expired items."
        response["action"] = "open_bucket"
        response["data"] = {"bucket_id": "expired"}

    # 3. Scheduler Intents
    elif "schedule" in user_query:
        if any(k in user_query for k in ["optimize", "critical", "ai", "smart"]):
            response["text"] = "I am generating an AI-optimized schedule for critical lots."
            response["action"] = "open_optimized_scheduler"
        else:
            response["text"] = "Opening the standard maintenance scheduler."
            response["action"] = "open_scheduler"

    # 4. Search / Navigation Intents
    elif "vendor" in user_query:
        response["text"] = " navigating to external vendors page."
        response["action"] = "navigate"
        response["data"] = {"url": "/vendors"}

    elif "item" in user_query or "search" in user_query:
        # Check for specific item UID
        match = re.search(r'(uid|item)\s*[:#]?\s*(\w+)', user_query)
        if match:
             uid = match.group(2)
             response["text"] = f"Searching for item {uid}..."
             response["action"] = "navigate"
             response["data"] = {"url": f"/items?search={uid}"}
        else:
            response["text"] = "Taking you to the items inventory."
            response["action"] = "navigate"
            response["data"] = {"url": "/items"}

    # 5. Help / Fallback
    elif any(k in user_query for k in ["help", "hi", "hello", "what can you do"]):
        response["text"] = "I can assist with:\n- Identifying expiring lots (e.g., 'show top 7-30')\n- Scheduling maintenance (e.g., 'optimize schedule')\n- Visual inspection (e.g., 'analyze image')\n- Searching items (e.g., 'search item 123')"
    
    else:
        response["text"] = "I didn't capture that. Try 'optimize schedule', 'analyze image', or 'show top expiring'."
        
    return jsonify(response)
