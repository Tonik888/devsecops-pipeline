import sys
import json
from gpt4all import GPT4All

def generate_recommendations(prompt, model_path):
    # Load the GPT4All model
    gpt = GPT4All(model_path, allow_download=False)

    # Generate text with max 400 tokens
    response = gpt.generate(prompt, max_tokens=400)
    return response

def main():
    # Check command-line arguments
    if len(sys.argv) != 4:
        print("Usage: python gpt4all_recommend.py <sonar-json> <trivy-json> <model-path>")
        sys.exit(1)

    sonar_path = sys.argv[1]
    trivy_path = sys.argv[2]
    model_path = sys.argv[3]

    # Load SonarQube JSON report
    with open(sonar_path, 'r') as f:
        sonar_data = json.load(f)

    # Load Trivy JSON report
    with open(trivy_path, 'r') as f:
        trivy_data = json.load(f)

    # Prepare prompt for GPT4All
    prompt = f"""
You are a DevOps security expert. Analyze the following SonarQube and Trivy scan results from a CI/CD pipeline.

SonarQube scan data:
{json.dumps(sonar_data, indent=2)}

Trivy vulnerability scan data:
{json.dumps(trivy_data, indent=2)}

Based on this data, provide a prioritized, concise, and actionable list of security recommendations
to fix vulnerabilities and improve the security posture of the pipeline.
"""

    # Generate recommendations
    recommendations = generate_recommendations(prompt, model_path)

    print("\n=== GPT4All Recommendations ===\n")
    print(recommendations)

if __name__ == "__main__":
    main()

