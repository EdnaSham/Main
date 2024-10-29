#to test run the python3 app.py first in a split command screen, then run a route to test like 'curl -i -d '{ "issue_description": "broken laptop" }' -H "Content-Type: application/json" -X POST http://localhost:3000/create_jira_issue' 
#to run the python3 app.py first , then go to url http://localhost:3000/ 

import openai, config_prod, requests, json, re, os
from flask import Flask, request, jsonify, send_from_directory
from requests.auth import HTTPBasicAuth
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import HfApi


app = Flask(__name__)

# Route to serve index.html by the flask web server
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Route to serve style.css by the flask web server
@app.route('/style.css')
def styles():
    return send_from_directory('.', 'style.css')

# Route to serve app_frontend.js by the flask web server
@app.route('/app_frontend.js')
def js():
    return send_from_directory('.', 'app_frontend.js')

# Route to create a new Jira issue
@app.route('/create_jira_issue', methods=['POST'])
def create_jira_issue():
   
   data = request.get_json()
   full_name = data.get('full_name')
   issue_title = data.get('issue_title')
   issue_description = data.get('issue_description')

   headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
   
   adf_description = {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": issue_description,
                    }
                ]
            }
        ]
    }
   
   payloadP = json.dumps({ 
        "fields": {
            "project": {
                "key": config_prod.JIRA_PROJECT_KEY
            },
            "summary": issue_title,
            "reporter": full_name,
            "description": adf_description,
            "issuetype": {
                "id": config_prod.JIRA_ISSUE_TYPE_ID
            }
        }
    })
   
   try:
        response = requests.post(
            config_prod.JSM_Backend_API_Base_URL,
            data=payloadP,
            headers=headers,
            auth=HTTPBasicAuth(config_prod.EMAIL, config_prod.JSM_API_KEY)
        )
        if response.status_code == 201:
            issue_key = response.json()['key']
            print(f"Issue created successfully. Issue ID: {issue_key}")
            return jsonify({"issue_key": issue_key})
        else:
            print(f"Failed to create issue. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return jsonify({"error": response.text}), response.status_code
   except Exception as e:
        print(f"Exception occurred while creating issue: {e}")
        return jsonify({"error": str(e)}), 500

# Route to get a Jira issue's status
@app.route('/get_jira_issue_status', methods=['POST'])
def get_jira_issue_status():

    data = request.get_json()
    issue_id = data.get('issue_id')

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{config_prod.JSM_Backend_API_Base_URL}/{issue_id}"

    response = requests.get(
        url,
        headers=headers, 
        auth=HTTPBasicAuth(config_prod.EMAIL, config_prod.JSM_API_KEY))
    print(response.status_code)

    #response.json() converts json from api to a python object
    if response.status_code == 200:
        issue_status = response.json()['fields']['status']['name']
        print(f"The status is {issue_status}")
        return jsonify({"issue_status": issue_status})
    else:
        print(f"Failed to get the issue status. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return jsonify({"error": response.text}), response.status_code

# Load the tokenizer and model for Llama 7B Chat from Hugging Face
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-7b-chat-hf', token= config_prod.HUGGINGFACE_API_KEY)
model = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-2-7b-chat-hf', token= config_prod.HUGGINGFACE_API_KEY)

# Route to for the service desk chat bot virtual assistant
@app.route('/virtual_assistant_response', methods=['POST'])
def virtual_assistant_response():

    data = request.get_json()
    chat_box_prompt= data.get('chat_box_prompt')
    print(chat_box_prompt)
    
    if chat_box_prompt:
        # Tokenize the input text
        inputs = tokenizer(chat_box_prompt, return_tensors='pt')
        print(f"The input is {inputs}")


        # Get the outputs from the model, adjusting temperature for balanced creativity, top-p sampling for more coherent output
        outputs = model.generate(inputs['input_ids'], max_length=500, num_return_sequences=1, temperature=0.7, top_p=0.9)
        print(f"The output is {outputs}")

        # Decode the generated text
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"The response is {response}")

        return jsonify({"message": "Success", "data": response})
    else:
        return jsonify({"error": "No input provided"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=3000)
