# GitHub Action-based AI PR Reviewer (Python, OpenAI v1.0+ API)

import os
import openai
import requests

# Inputs from GitHub Actions ENV
REPO = os.environ.get("GITHUB_REPOSITORY")
PR_NUMBER = os.environ.get("PR_NUMBER")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Step 1: Fetch PR diff
def get_pr_diff():
    pr_url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    pr_response = requests.get(pr_url, headers=headers).json()
    diff_url = pr_response.get("diff_url")
    diff = requests.get(diff_url, headers=headers).text
    return diff

# Step 2: Generate review using OpenAI (v1.0+)
def generate_review(diff):
    prompt = f"""
    You are a senior DevOps and Python engineer. Review this PR diff focusing on:
    - Code quality
    - Security flaws
    - Terraform/Ansible best practices
    - Clarity and maintainability

    PR Diff:
    {diff}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# Step 3: Post comment to PR
def post_review_comment(review):
    comment_url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    requests.post(
        comment_url,
        headers=headers,
        json={"body": review}
    )

if __name__ == "__main__":
    diff = get_pr_diff()
    review = generate_review(diff)
    post_review_comment(review)
    print("✅ AI PR review posted successfully.")
