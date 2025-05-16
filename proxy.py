from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/proxy/huggingface', methods=['POST'])
def proxy_huggingface():
    try:
        # Forward the request to Hugging Face
        response = requests.post(
            'https://huggingface.co',
            headers={
                'Content-Type': request.headers.get('Content-Type', 'application/json'),
                'Accept': 'application/json'
            },
            data=request.data
        )
        
        # Return the response with proper CORS headers
        return response.text, response.status_code, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/gradio', methods=['GET'])
def proxy_gradio():
    try:
        # Forward the request to Gradio assets
        response = requests.get(
            'https://gradio.s3-us-west-2.amazonaws.com/assets/' + request.args.get('path'),
            headers={
                'Accept': 'text/css'
            }
        )
        
        # Return the response with proper CORS headers
        return response.text, response.status_code, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
