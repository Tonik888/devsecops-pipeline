from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import torch
import sys
import json

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
        for issue in issues[:10]:
            prompt += f"- Severity: {issue.get('severity')}, Type: {issue.get('type')}, File: {issue.get('component')}, Message: {issue.get('message')}\n"

    prompt += "\nTrivy Vulnerabilities:\n"
    vulnerabilities = trivy_data.get('Results', [])
    if not vulnerabilities:
        prompt += "No vulnerabilities found.\n"
    else:
        count = 0
        for target in vulnerabilities:
            vulns = target.get('Vulnerabilities', [])
            for vuln in vulns[:5]:
                prompt += f"- Severity: {vuln.get('Severity')}, Package: {vuln.get('PkgName')}, VulnerabilityID: {vuln.get('VulnerabilityID')}, Description: {vuln.get('Description')[:100]}...\n"
                count += 1
                if count >= 10:
                    break
            if count >= 10:
                break

    prompt += "\nPlease provide practical and prioritized recommendations."
    return prompt

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_gptneo_cpu.py <sonar-json> <trivy-json>")
        sys.exit(1)

    sonar_file = sys.argv[1]
    trivy_file = sys.argv[2]

    sonar_data = load_json(sonar_file)
    trivy_data = load_json(trivy_file)

    prompt = build_prompt(sonar_data, trivy_data)

    model_name = "EleutherAI/gpt-neo-125M"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    device = torch.device("cpu")
    model.to(device)

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    # Greedy decoding (fastest) to reduce runtime on CPU
    outputs = model.generate(inputs['input_ids'], max_length=150, do_sample=False)

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("=== GPT-Neo 125M CPU Generated Recommendations ===\n")
    print(text)

if __name__ == "__main__":
    main()
