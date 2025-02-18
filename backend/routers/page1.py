from flask import Blueprint, request, jsonify
# from model import rag_model 

page1_bp = Blueprint('page1', __name__)

@page1_bp.route('/data', methods=['POST'])
def page1_data():
    # TODO: Extract the user's identity from the token in the incoming message
    #

    # TODO: Send a request to the database to retrieve user-related information
    #

    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "The 'message' attribute is missing from the request data."}), 400
    user_prompt = data['message']
    response = "Hello World" #rag_model.generate_response(user_prompt) 
    
    return jsonify({"response": response})
