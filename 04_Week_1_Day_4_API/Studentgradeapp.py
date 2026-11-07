
import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student Grade Book",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM UI STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #F5F7FB;
    }

    [data-testid="stSidebar"] {
        background-color: #14243A;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF;
    }

    .main-title {
        font-size: 30px;
        font-weight: 750;
        color: #14243A;
        margin-bottom: 4px;
    }

    .sub-title {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E5EAF1;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(20,36,58,0.04);
    }

    div[data-testid="stForm"] {
        background: white;
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #E5EAF1;
    }

    .section-heading {
        color: #14243A;
        font-size: 20px;
        font-weight: 650;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "students" not in st.session_state:
    st.session_state.students = []


# --------------------------------------------------
# ORIGINAL GRADE CALCULATION LOGIC
# --------------------------------------------------

def get_grade(mark):
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "E"


def add_student(name, mark):

    st.session_state.students.append({
        "name": name,
        "mark": mark,
        "grade": get_grade(mark)
    })


# --------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------

def get_student_dataframe():

    return pd.DataFrame(
        st.session_state.students,
        columns=["name", "mark", "grade"]
    ).rename(columns={
        "name": "Student Name",
        "mark": "Marks",
        "grade": "Grade"
    })


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:

    st.markdown("# 🎓 STUDENT HUB")
    st.caption("Academic Performance System")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Add Student",
            "Student Records",
            "Performance Analytics"
        ]
    )

    st.divider()

    st.caption("STUDENT GRADE MANAGER")
    st.caption("Academic Management | 2026")


# --------------------------------------------------
# COMMON HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">Student Performance Manager</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Monitor student performance, manage academic records '
    'and analyse grade distribution.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    students = st.session_state.students

    st.markdown("### Academic Overview")

    if students:

        marks = [s["mark"] for s in students]

        total_students = len(students)
        average = sum(marks) / total_students
        highest = max(marks)
        lowest = min(marks)

    else:

        total_students = 0
        average = 0
        highest = 0
        lowest = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", total_students)
    col2.metric("Class Average", f"{average:.1f}%")
    col3.metric("Highest Mark", f"{highest:.1f}")
    col4.metric("Lowest Mark", f"{lowest:.1f}")

    st.divider()

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown("### Recent Student Records")

        if students:

            df = get_student_dataframe()

            st.dataframe(
                df.tail(10),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No student records available. Add your first student.")

    with right:

        st.markdown("### Grade Distribution")

        if students:

            grade_order = ["A", "B", "C", "D", "E"]

            grade_counts = {
                grade: sum(
                    1 for s in students if s["grade"] == grade
                )
                for grade in grade_order
            }

            grade_df = pd.DataFrame({
                "Grade": grade_order,
                "Students": [grade_counts[g] for g in grade_order]
            })

            st.bar_chart(
                grade_df,
                x="Grade",
                y="Students"
            )

        else:

            st.info("Grade analytics will appear after adding students.")


# --------------------------------------------------
# ADD STUDENT
# --------------------------------------------------

elif page == "Add Student":

    st.markdown("### Add New Student")

    st.write("Enter the student details below.")

    with st.form("student_form", clear_on_submit=True):

        name = st.text_input(
            "Student Name",
            placeholder="Enter full name"
        )

        mark = st.number_input(
            "Student Marks",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.5
        )

        submitted = st.form_submit_button(
            "Add Student",
            use_container_width=True
        )

        if submitted:

            if not name.strip():

                st.error("Please enter the student name.")

            else:

                add_student(name.strip(), mark)

                st.success(
                    f"{name.strip()} added successfully! "
                    f"Grade: {get_grade(mark)}"
                )


# --------------------------------------------------
# STUDENT RECORDS
# --------------------------------------------------

elif page == "Student Records":

    st.markdown("### Student Records")

    students = st.session_state.students

    if students:

        df = get_student_dataframe()

        search = st.text_input(
            "Search Student",
            placeholder="Enter student name..."
        )

        if search:

            df = df[
                df["Student Name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.write(f"Records displayed: {len(df)}")

        # CSV DOWNLOAD

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Student Records (CSV)",
            data=csv_data,
            file_name="student_records.csv",
            mime="text/csv"
        )

    else:

        st.info("No student records available yet.")


# --------------------------------------------------
# PERFORMANCE ANALYTICS
# --------------------------------------------------

elif page == "Performance Analytics":

    st.markdown("### Academic Performance Analytics")

    students = st.session_state.students

    if students:

        df = get_student_dataframe()

        # Grade distribution

        st.markdown("#### Grade Distribution")

        grade_order = ["A", "B", "C", "D", "E"]

        grade_counts = {
            grade: sum(
                1 for s in students if s["grade"] == grade
            )
            for grade in grade_order
        }

        grade_df = pd.DataFrame({
            "Grade": grade_order,
            "Students": [grade_counts[g] for g in grade_order]
        })

        st.bar_chart(
            grade_df,
            x="Grade",
            y="Students"
        )

        st.divider()

        # Student-wise performance

        st.markdown("#### Student-wise Marks")

        st.bar_chart(
            df,
            x="Student Name",
            y="Marks"
        )

        # Grade summary

        st.markdown("#### Grade Summary")

        summary = pd.DataFrame({
            "Grade": grade_order,
            "Number of Students": [
                grade_counts[g] for g in grade_order
            ]
        })

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Add student records to view performance analytics.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Student Performance Manager | Built with Python and Streamlit"
)
