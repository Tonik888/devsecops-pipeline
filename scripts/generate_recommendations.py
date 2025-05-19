import sys
import json
import requests

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# ... (build_prompt function remains unchanged) ...

def call_gpt_neo(prompt, api_token):
    API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-125M"
    headers = {"Authorization": f"Bearer {api_token}"}

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150, "temperature": 0.7}
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        return result[0].get('generated_text', '')
    else:
        return "No recommendations generated."

def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_recommendations.py <sonar-json> <trivy-json> <api-token>")
        sys.exit(1)

    sonar_file = sys.argv[1]
    trivy_file = sys.argv[2]
    api_token = sys.argv[3]

    sonar_data = load_json(sonar_file)
    trivy_data = load_json(trivy_file)

    prompt = build_prompt(sonar_data, trivy_data)

    recommendations = call_gpt_neo(prompt, api_token)
    print("=== AI-Generated Actionable Recommendations ===\n")
    print(recommendations)

if __name__ == "__main__":
    main()
