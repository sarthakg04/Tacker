from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import anthropic


app = Flask(__name__)

# Placeholder for HTML template with a form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Policy Analysis</title>
</head>
<body>
    <h2>Policy Text Analysis</h2>
    <form method="post">
        URL: <input type="text" name="url" /><br>
        <input type="submit">
    </form>

    {% if analysis %}
        <h3>Analysis Result:</h3>
        <pre>{{ analysis }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def analyze_policy():
    if request.method == 'POST':
        url = request.form['url']
        policy_text = fetch_policy_text(url)
        analysis = get_policy_analysis(policy_text)
        return render_template_string(HTML_TEMPLATE, analysis=analysis)
    return render_template_string(HTML_TEMPLATE, analysis=None)

def fetch_policy_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract all text from the webpage
    text = ' '.join(soup.stripped_strings)
    return text


def get_policy_analysis(policy_text):
    # Initialize Anthropic API client
    client = anthropic.Anthropic(api_key="api-key")
    prompt = f"""
Given the text of a company's data policy provided below, please evaluate it according to specific criteria for each category: Data Collection, Data Retention, IP and Data Ownership, Data Privacy & Sharing, and Liability and Indemnification. After evaluating, populate the JSON structure with your analysis, marking each category as "true" for "Good" or "false" for "Bad" based on the following criteria:

- Data Collection:
   - Good: minimal data needed to operate the platform.
   - Bad: The T&C doesn't state that only minimal data is collected.
- Data Retention:
   - Good: No data is retained unless the user provides explicit permission/consent/request.
   - Bad: Data is retained without permission or it is not defined.
- IP and Data Ownership:
   - Good: The user owns all IP/data that the user creates on the platform.
   - Bad: The platform owns the user's data in part or whole, or it is not explicitly stated that the user owns all data.
- Data Privacy & Sharing:
   - Good: Data is not shared with any third party or used for any other purpose than providing the service to the user.
   - Bad: Data is shared with third parties or used by the company for purposes beyond what is needed for the services rendered to the user, or is left undefined.
- Liability and Indemnification:
   - Good: An indemnification or limits of liability clause exists.
   - Bad: Undefined or clause does not exist.

Please populate the following JSON structure with your analysis:

{{
  "id": 1,
  "company": "[Company Name]",
  "sys_queried_on": "[Date]",
  "toc_last_updated_on": "[Date]",
  "Analysis": {{
    "properties": {{
      "Data Collection": {{"text": "", "score": null}},
      "Data Retention": {{"text": "", "score": null}},
      "IP and Data Ownership": {{"text": "", "score": null}},
      "Data Privacy & Sharing": {{"text": "", "score": null}},
      "Liability and Indemnification": {{"text": "", "score": null}}
    }}
  }}
}}

{policy_text}
"""
    # Sending the request to Claude
    response = client.beta.tools.messages.create(
        model="claude-3-opus-20240229",  # Use the correct model identifier
        messages=[
        {"role": "user", "content": prompt}
    ],
        max_tokens=4000,  # Adjust as necessary
    )

    # Assuming the response is in JSON format or convert as needed
    return response.content.text  # Or extract and format the response as required

if __name__ == '__main__':
    app.run(debug=True)
