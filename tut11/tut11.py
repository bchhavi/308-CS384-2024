import streamlit as st
import pandas as pd



###################################################### PART 1 #######################################################



def process_excel(uploaded_file):
    # Load student data
    student_data = pd.read_excel(uploaded_file, sheet_name='Sheet1')

    # Create Grade Statistics DataFrame
    data = {
        "Subject Code": [None] * 11,
        "Month Year": ["Nov-24"] * 11,
        "Grade": ["AA", "AB", "BB", "BC", "CC", "CD", "DD", "F", "I", "PP", "NP"],
        "a": [91, 81, 71, 61, 51, 41, 31, 0, None, None, None],
        "b": [100, 90, 80, 70, 60, 50, 40, 30, None, None, None],
        "min (x)": [None] * 11,
        "max (x)": [None] * 11,
    }
    df = pd.DataFrame(data)

    # Calculate min and max Total for each grade
    grade_stats = student_data.groupby('Grade')['Total'].agg(['min', 'max']).reset_index()
    for index, row in df.iterrows():
        grade = row['Grade']
        if grade in grade_stats['Grade'].values:
            grade_row = grade_stats[grade_stats['Grade'] == grade]
            df.at[index, 'min (x)'] = grade_row['min'].values[0]
            df.at[index, 'max (x)'] = grade_row['max'].values[0]

    # Scaling formula
    def scale_marks(row, grade_df):
        grade = row['Grade']
        if grade in grade_df['Grade'].values:
            grade_row = grade_df[grade_df['Grade'] == grade]
            a, b = grade_row['a'].values[0], grade_row['b'].values[0]
            min_x, max_x = grade_row['min (x)'].values[0], grade_row['max (x)'].values[0]
            return (((b - a) * (row['Total'] - min_x)) / (max_x - min_x)) + a
        return None

    student_data['Scaled'] = student_data.apply(scale_marks, axis=1, grade_df=df)

    # Calculate Grade Counts and IAPC Difference
    total_students = len(student_data)
    grade_counts = student_data['Grade'].value_counts().reset_index()
    grade_counts.columns = ['Grade', 'Count']

    iapc_values = [5, 15, 25, 30, 15, 5, 5, 0]  # Example IAPC distribution
    iapc_index = ['AA', 'AB', 'BB', 'BC', 'CC', 'CD', 'DD', 'F']
    iapc_dict = dict(zip(iapc_index, iapc_values))

    grade_counts['IAPC'] = grade_counts['Grade'].map(iapc_dict)
    grade_counts['IAPC_count'] = (grade_counts['IAPC'] * total_students / 100).round().astype(int)
    grade_counts['Difference'] = grade_counts['Count'] - grade_counts['IAPC_count']
    grade_counts_sorted = grade_counts.sort_values(by='Grade').reset_index(drop=True)

    return student_data, df, grade_counts_sorted

# Streamlit App
st.title("Excel Processor for Grades and Scaled Scores")
uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])

if uploaded_file:
    st.success("File uploaded successfully!")
    student_data, df, grade_counts_sorted = process_excel(uploaded_file)

    # Display DataFrames
    st.header("Student Data")
    st.dataframe(student_data)
    st.header("Grade Statistics")
    st.dataframe(df)
    st.header("Sorted Grade Counts Difference")
    st.dataframe(grade_counts_sorted)

    # Download Processed Data
    with pd.ExcelWriter("processed_data.xlsx", engine='openpyxl') as writer:
        student_data.to_excel(writer, sheet_name="student_data", index=False)
        df.to_excel(writer, sheet_name="grade_statistics", index=False)
        grade_counts_sorted.to_excel(writer, sheet_name="grade_counts_sorted", index=False)

    with open("processed_data.xlsx", "rb") as file:
        st.download_button("Download Processed Excel", data=file, file_name="processed_data.xlsx")



#######################################################  PART 2 ######################################################


from io import BytesIO

def prepare_grades_data(total_students):
    grades_data = {
        "grade": ["AA", "AB", "BB", "BC", "CC", "CD", "DD", "F", "I", "PP", "NP"],
        "old_iapc_reco": [5, 15, 25, 30, 15, 5, 5, 0, 0, 0, 0],
    }
    grades_df = pd.DataFrame(grades_data)
    grades_df['Counts'] = (grades_df['old_iapc_reco'] / 100) * total_students
    grades_df['Round'] = grades_df['Counts'].round().astype(int)
    grades_df['Count verified'] = grades_df['Round']
    return grades_df

def calculate_total_scaled(row, max_marks, weightage):
    total_score = 0
    for column in max_marks.keys():
        if column in row:
            score = float(row[column])
            scaled_score = (score / max_marks[column]) * weightage[column]
            total_score += scaled_score
    return total_score

def assign_grades(student_data, grades_df):
    grades_assigned = []
    for _, row in grades_df.iterrows():
        grade = row['grade']
        count_verified = int(row['Count verified'])
        grades_assigned.extend([grade] * count_verified)
    student_data['Grade'] = grades_assigned[:len(student_data)]
    return student_data

def scale_marks(row, df):
    grade = row['Grade']
    if grade in df['Grade'].values:
        grade_row = df[df['Grade'] == grade]
        a, b = grade_row['a'].values[0], grade_row['b'].values[0]
        min_x, max_x = grade_row['min (x)'].values[0], grade_row['max (x)'].values[0]
        scaled_value = (((b - a) * (row['Total Scaled/100'] - min_x)) / (max_x - min_x)) + a
        return scaled_value
    else:
        return None

def process_excel(uploaded_file):
    input_data = pd.read_excel(uploaded_file, sheet_name='Sheet1')
    max_marks = input_data.iloc[0, 2:].to_dict()
    weightage = input_data.iloc[1, 2:].to_dict()
    student_data = input_data.iloc[2:].reset_index(drop=True)
    total_students = len(student_data)
    grades_df = prepare_grades_data(total_students)
    student_data['Total Scaled/100'] = student_data.apply(calculate_total_scaled, axis=1, args=(max_marks, weightage))
    student_data = student_data.sort_values(by='Total Scaled/100', ascending=False).reset_index(drop=True)
    student_data = assign_grades(student_data, grades_df)
    stats_data = {
        "Subject Code": [None] * 11,
        "Month Year": ["Nov-24"] * 11,
        "Grade": ["AA", "AB", "BB", "BC", "CC", "CD", "DD", "F", "I", "PP", "NP"],
        "a": [91, 81, 71, 61, 51, 41, 31, 0, None, None, None],
        "b": [100, 90, 80, 70, 60, 50, 40, 30, None, None, None],
        "min (x)": [None] * 11,
        "max (x)": [None] * 11,
    }
    stats_df = pd.DataFrame(stats_data)
    grade_stats = student_data.groupby('Grade')['Total Scaled/100'].agg(['min', 'max']).reset_index()
    for index, row in stats_df.iterrows():
        grade = row['Grade']
        if grade in grade_stats['Grade'].values:
            grade_row = grade_stats[grade_stats['Grade'] == grade]
            stats_df.at[index, 'min (x)'] = grade_row['min'].values[0]
            stats_df.at[index, 'max (x)'] = grade_row['max'].values[0]
    student_data['Scaled'] = student_data.apply(scale_marks, axis=1, df=stats_df)
    grade_counts = student_data['Grade'].value_counts().reset_index()
    grade_counts.columns = ['Grade', 'Count']
    iapc_values = dict(zip(grades_df['grade'], grades_df['old_iapc_reco']))
    grade_counts['IAPC'] = grade_counts['Grade'].map(iapc_values)
    grade_counts['IAPC_count'] = (grade_counts['IAPC'] * total_students / 100).round().astype(int)
    grade_counts['Difference'] = grade_counts['Count'] - grade_counts['IAPC_count']
    grade_counts_sorted = grade_counts.sort_values(by='Grade').reset_index(drop=True)
    return student_data, stats_df, grade_counts_sorted

st.title("Excel Processor for Grades and Scaled Scores")
uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])

if uploaded_file:
    st.success("File uploaded successfully!")
    student_data, stats_df, grade_counts_sorted = process_excel(uploaded_file)
    st.header("Processed Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Student Data")
        st.dataframe(student_data)
    with col2:
        st.subheader("Grade Statistics")
        st.dataframe(stats_df)
    with col3:
        st.subheader("Grade Counts Difference")
        st.dataframe(grade_counts_sorted)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        student_data.to_excel(writer, sheet_name="Student Data", index=False)
        stats_df.to_excel(writer, sheet_name="Grade Statistics", index=False)
        grade_counts_sorted.to_excel(writer, sheet_name="Grade Counts", index=False)
    output.seek(0)
    st.download_button(
        label="Download Processed Excel",
        data=output,
        file_name="processed_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
