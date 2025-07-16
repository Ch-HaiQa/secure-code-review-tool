import os
import cohere
import json
import subprocess
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_api_key)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    code_content = file.read().decode('utf-8')
    analysis_type = request.form.get('analysis_type')

    if analysis_type == 'api':
        # Use Cohere's API for analysis
        try:
            prompt = f"Analyze the following code for security vulnerabilities:\n\n{code_content}\n\nProvide a detailed explanation of potential vulnerabilities and risks."

            response = co.generate(
                model='command-xlarge-nightly',
                prompt=prompt,
                max_tokens=300,
                temperature=0.5
            )

            analysis = response.generations[0].text

            # Generate PDF report
            pdf_path = generate_pdf_report(analysis, "API-Based Code Analysis Report")
            
            # Render the analysis result and provide download link
            return render_template('report.html', analysis=analysis, pdf_path=pdf_path)

        except Exception as e:
            print(e)
            return render_template('error.html', message="API request failed.")

    elif analysis_type == 'bandit':
        try:
            temp_filename = 'temp_code.py'
            with open(temp_filename, 'w') as temp_file:
                temp_file.write(code_content)

            analysis = run_bandit(temp_filename)
            os.remove(temp_filename)
            
            # Generate PDF report
            pdf_path = generate_pdf_report(analysis, "Bandit Analysis Report")
            return render_template('banditReport.html', analysis=analysis, pdf_path=pdf_path)

        except Exception as e:
            print(e)
            return render_template('error.html', message="Bandit analysis failed.")

    else:
        return "Invalid analysis type selected", 400
def run_bandit(filename):
    """
    Runs Bandit on the given filename and returns results.
    """
    try:
        # Ensure the file exists before running Bandit
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} does not exist.")
        
        # Run Bandit command with quiet mode to suppress info logs
        command = ['bandit', '-r', filename, '--format', 'json', '-q']  # Added '-q' flag
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # If stderr contains errors, raise an exception
        if stderr:
            raise Exception(f"Bandit error: {stderr.decode('utf-8')}")
        
        # Parse Bandit output
        analysis_results = json.loads(stdout.decode('utf-8'))
        results = analysis_results.get('results', [])
        formatted_results = []

        # Format the results for better readability
        for result in results:
            issue_text = (
                f"File: {result['filename']}\n"
                f"Issue: {result['issue_text']}\n"
                f"Severity: {result['issue_severity']}\n"
                f"Confidence: {result['issue_confidence']}\n"
                f"Line Number: {result['line_number']}\n"
                "---------------------------------------"
            )
            formatted_results.append(issue_text)

        # Return formatted results
        return "\n\n".join(formatted_results) if formatted_results else "No issues found."

    except FileNotFoundError as fnf_error:
        print(fnf_error)
        return "Error: The temporary file could not be found. Please check the upload and try again."
    except json.JSONDecodeError as json_error:
        print(f"JSON Decode Error: {json_error}")
        return "Error: Failed to parse Bandit JSON output."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"Unexpected error occurred: {e}"


def generate_pdf_report(analysis_text, title):
    """
    Generates a PDF report based on the analysis text.
    """
    pdf_path = 'analysis_report.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Analysis Results:", styles['Heading2']))
    elements.append(Spacer(1, 12))

    analysis_paragraphs = [Paragraph(line, styles['BodyText']) for line in analysis_text.split('\n') if line.strip()]
    elements.extend(analysis_paragraphs)
    elements.append(Spacer(1, 12))

    doc.build(elements)
    return pdf_path

@app.route('/download_report')
def download_report():
    """
    Endpoint to download the generated PDF report.
    """
    pdf_path = 'analysis_report.pdf'
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
