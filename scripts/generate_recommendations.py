import sys
import json
import requests

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def build_prompt(sonar_data, trivy_data):
    prompt = "Analyze the following security and code quality issues and provide actionable recommendations:\n\n"

    prompt += "SonarQube Issues:\n"
    issues = sonar_data.get('issues', [])
    if not issues:
        prompt += "No issues found.\n"
    else:
        for issue in issues[:10]:  # Limit to 10 issues to keep prompt size reasonable
            prompt += f"- Severity: {issue.get('severity')}, Type: {issue.get('type')}, File: {issue.get('component')}, Message: {issue.get('message')}\n"

    prompt += "\nTrivy Vulnerabilities:\n"
    vulnerabilities = trivy_data.get('Results', [])
    if not vulnerabilities:
        prompt += "No vulnerabilities found.\n"
    else:
        # Trivy 'Results' is a list of scanned targets, each with 'Vulnerabilities'
        count = 0
        for target in vulnerabilities:
            vulns = target.get('Vulnerabilities', [])
            for vuln in vulns[:5]:  # Limit to 5 vulns per target
                prompt += f"- Severity: {vuln.get('Severity')}, Package: {vuln.get('PkgName')}, VulnerabilityID: {vuln.get('VulnerabilityID')}, Description: {vuln.get('Description')[:100]}...\n"
                count += 1
                if count >= 10:
                    break
            if count >= 10:
                break

    prompt += "\nPlease provide practical and prioritized recommendations to fix these issues."

    return prompt

def call_gpt_neo(prompt):
    # Using Hugging Face Inference API for GPT-Neo 125M (you need to get a free API token from https://huggingface.co/settings/tokens)
    API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-125M"
    headers = {"Authorization": "Bearer YOUR_HUGGINGFACE_API_TOKEN"}

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150, "temperature": 0.7}
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()
    # The output is usually a list of dicts with generated text
    if isinstance(result, list) and len(result) > 0:
        return result[0].get('generated_text', '')
    else:
        return "No recommendations generated."

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_recommendations.py <sonar-json> <trivy-json>")
        sys.exit(1)

    sonar_file = sys.argv[1]
    trivy_file = sys.argv[2]

    sonar_data = load_json(sonar_file)
    trivy_data = load_json(trivy_file)

    prompt = build_prompt(sonar_data, trivy_data)

    recommendations = call_gpt_neo(prompt)
    print("=== AI-Generated Actionable Recommendations ===\n")
    print(recommendations)

if __name__ == "__main__":
    main()
