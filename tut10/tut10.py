#################################################### PART 1 ####################################################


import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
input_file_path = '/content/Input-1.xlsx'
try:
    input_data = pd.read_excel(input_file_path, sheet_name='Sheet1')
except Exception as e:
    logging.error(f"Error loading input file: {e}")
    raise

grade_distribution = {
    'AA': 5, 'AB': 15, 'BB': 25, 'BC': 30, 'CC': 15, 'CD': 5, 'DD': 5, 'F': 0, 'I': 0, 'PP': 0, 'NP': 0
}

def func(input_df):
    max_marks = input_df.iloc[0, 2:].astype(float)
    weightage = input_df.iloc[1, 2:].astype(float)
    students_df = input_df.drop([0, 1]).reset_index(drop=True)
    original_score_columns = ["Mid Sem", "Endsem", "Quiz 1", "Quiz 2"]
    missing_values = {}
    for i, col in enumerate(original_score_columns, start=2):
        try:
            students_df[f"{col}_Weighted"] = (students_df.iloc[:, i].astype(float) / max_marks.iloc[i-2]) * weightage.iloc[i-2]
        except ValueError:
            missing_values[col] = students_df[pd.to_numeric(students_df.iloc[:, i], errors='coerce').isna()]['Roll'].tolist()
            students_df[f"{col}_Weighted"] = 0
    if missing_values:
        for col, rolls in missing_values.items():
            logging.warning(f"Missing or non-numeric values in {col}: Roll numbers {rolls}")

    students_df['Total Score'] = students_df[[f"{col}_Weighted" for col in original_score_columns]].sum(axis=1)
    return students_df[['Roll', 'Name'] + original_score_columns + ['Total Score']]
try:
    students_df = func(input_data)
    students_df = students_df.sort_values(by='Total Score', ascending=False).reset_index(drop=True)
    total_students = len(students_df)
    initial_counts = {grade: round((percentage / 100) * total_students) for grade, percentage in grade_distribution.items()}
    assigned_count = sum(initial_counts.values())
    if assigned_count < total_students:
        for grade in initial_counts:
            if initial_counts[grade] > 0:
                initial_counts[grade] += 1
                assigned_count += 1
                if assigned_count == total_students:
                    break
    elif assigned_count > total_students:
        for grade in reversed(initial_counts):
            if initial_counts[grade] > 0:
                initial_counts[grade] -= 1
                assigned_count -= 1
                if assigned_count == total_students:
                    break
    grade_data = {
        'grade': list(grade_distribution.keys()),
        'old iapc reco': list(grade_distribution.values()),
        'Counts': [(percentage / 100) * total_students for percentage in grade_distribution.values()],
        'Round': list(initial_counts.values()),
        'Count verified': list(initial_counts.values())
    }
    grade_df = pd.DataFrame(grade_data)
    grades = []
    for grade, count in initial_counts.items():
        grades.extend([grade] * count)
    students_df['Grade'] = grades[:total_students]
    empty_columns = pd.DataFrame([[""] * 4] * len(students_df), columns=["", "", "", ""])
    students_with_empty_cols = pd.concat([students_df, empty_columns], axis=1)
    final_output_df = pd.concat([students_with_empty_cols, grade_df], axis=1)
    grade_sorted_df = pd.concat([students_df, pd.DataFrame([[""] * 4] * total_students, columns=["", "", "", ""]), grade_df], axis=1)
    roll_sorted_df = pd.concat([students_df.sort_values(by='Roll').reset_index(drop=True), pd.DataFrame([[""] * 4] * total_students, columns=["", "", "", ""]), grade_df], axis=1)
    output_generated_path = '/content/Output_file.xlsx'
    with pd.ExcelWriter(output_generated_path) as writer:
        grade_sorted_df.to_excel(writer, sheet_name='Sheet1_Grade_Sorted', index=False)
        roll_sorted_df.to_excel(writer, sheet_name='Sheet2_Roll_Sorted', index=False)
    logging.info(f"Generated output saved at {output_generated_path}")
except Exception as e:
    logging.error(f"An error occurred: {e}")
    raise





#########################################################PART 2 ##################################################################





from flask import Flask, request, render_template_string, send_file
import pandas as pd
import os
import logging

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Grade distribution dictionary
grade_distribution = {
    'AA': 5, 'AB': 15, 'BB': 25, 'BC': 30, 'CC': 15, 'CD': 5, 'DD': 5, 'F': 0, 'I': 0, 'PP': 0, 'NP': 0
}

# HTML Template with CSS Styling
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel File Processor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 800px;
            margin: 50px auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        form {
            text-align: center;
            margin-top: 20px;
        }
        input[type="file"] {
            display: block;
            margin: 20px auto;
            padding: 10px;
        }
        input[type="submit"] {
            background: #007BFF;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background: #0056b3;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 0.9em;
            color: #666;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #007BFF;
            color: white;
        }
        .download-btn {
            display: block;
            text-align: center;
            margin: 20px auto;
        }
        .download-btn a {
            text-decoration: none;
            color: white;
            background: #28a745;
            padding: 10px 20px;
            border-radius: 4px;
        }
        .download-btn a:hover {
            background: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload Your Excel File</h1>
        <form action="/process" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".xlsx">
            <input type="submit" value="Process File">
        </form>
        {% if table_html %}
            <h2>Processed Data (Top 10 Rows)</h2>
            <div>{{ table_html|safe }}</div>
            <div class="download-btn">
                <a href="/download">Download Full Output</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Function to process the Excel file
def process_input_file(input_path):
    input_data = pd.read_excel(input_path, sheet_name='Sheet1')
    max_marks = input_data.iloc[0, 2:].astype(float)
    weightage = input_data.iloc[1, 2:].astype(float)
    students_df = input_data.drop([0, 1]).reset_index(drop=True)
    original_score_columns = ["Mid Sem", "Endsem", "Quiz 1", "Quiz 2"]
    missing_values = {}

    for i, col in enumerate(original_score_columns, start=2):
        try:
            students_df[f"{col}_Weighted"] = (students_df.iloc[:, i].astype(float) / max_marks.iloc[i-2]) * weightage.iloc[i-2]
        except ValueError:
            missing_values[col] = students_df[pd.to_numeric(students_df.iloc[:, i], errors='coerce').isna()]['Roll'].tolist()
            students_df[f"{col}_Weighted"] = 0

    if missing_values:
        for col, rolls in missing_values.items():
            logging.warning(f"Missing or non-numeric values in {col}: Roll numbers {rolls}")

    students_df['Total Score'] = students_df[[f"{col}_Weighted" for col in original_score_columns]].sum(axis=1)
    students_df = students_df[['Roll', 'Name'] + original_score_columns + ['Total Score']].sort_values(by='Total Score', ascending=False).reset_index(drop=True)

    total_students = len(students_df)
    initial_counts = {grade: round((percentage / 100) * total_students) for grade, percentage in grade_distribution.items()}
    assigned_count = sum(initial_counts.values())

    # Adjust grade counts
    while assigned_count < total_students:
        for grade in initial_counts:
            if initial_counts[grade] > 0:
                initial_counts[grade] += 1
                assigned_count += 1
                if assigned_count == total_students:
                    break

    while assigned_count > total_students:
        for grade in reversed(initial_counts):
            if initial_counts[grade] > 0:
                initial_counts[grade] -= 1
                assigned_count -= 1
                if assigned_count == total_students:
                    break

    grades = []
    for grade, count in initial_counts.items():
        grades.extend([grade] * count)

    students_df['Grade'] = grades[:total_students]

    grades_table = pd.DataFrame({
        'Grade': list(initial_counts.keys()),
        'Old IAPC Reco': list(grade_distribution.values()),
        'Formula Counts': [count * total_students / 100 for count in grade_distribution.values()],
        'Formula Round': list(initial_counts.values()),
        'Count Verified': list(initial_counts.values())
    })

    output_path = os.path.join(OUTPUT_FOLDER, 'Output_file.xlsx')
    with pd.ExcelWriter(output_path) as writer:
        students_df.to_excel(writer, sheet_name='Sheet1_Grade_Sorted', index=False)
        grades_table.to_excel(writer, sheet_name='Sheet2_Grade_Distribution', index=False)

    return students_df, output_path

# Route for the home page
@app.route('/')
def upload_file():
    return render_template_string(HTML_TEMPLATE)

# Route to process the uploaded file
@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return "No file uploaded!", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected!", 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    try:
        processed_data, output_path = process_input_file(input_path)
        table_html = processed_data.head(10).to_html(index=False, classes='table')
        return render_template_string(HTML_TEMPLATE, table_html=table_html)
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return "An error occurred while processing the file. Please check the logs for details.", 500

# Route to download the full output file
@app.route('/download')
def download_file():
    output_path = os.path.join(OUTPUT_FOLDER, 'Output_file.xlsx')
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True, download_name='Output_file.xlsx')
    else:
        return "Output file not found!", 404

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)







