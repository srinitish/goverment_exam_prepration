import streamlit as st
import sqlite3
import os

# --- DB Setup ---
conn = sqlite3.connect("govtprep.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS resources
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT, pdf_url TEXT, subject TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS quizzes
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              question TEXT, options TEXT, answer INTEGER, subject TEXT)""")
conn.commit()

# --- Helper Functions ---
def add_resource(title, url, subject):
    c.execute("INSERT INTO resources (title, pdf_url, subject) VALUES (?, ?, ?)", (title, url, subject))
    conn.commit()

def get_resources(subject=None):
    if subject:
        return c.execute("SELECT * FROM resources WHERE subject=?", (subject,)).fetchall()
    return c.execute("SELECT * FROM resources").fetchall()

def delete_resource(rid):
    c.execute("DELETE FROM resources WHERE id=?", (rid,))
    conn.commit()

def add_quiz(question, options, answer, subject):
    c.execute("INSERT INTO quizzes (question, options, answer, subject) VALUES (?, ?, ?, ?)",
              (question, ",".join(options), answer, subject))
    conn.commit()

def get_quizzes(subject=None):
    if subject:
        return c.execute("SELECT * FROM quizzes WHERE subject=?", (subject,)).fetchall()
    return c.execute("SELECT * FROM quizzes").fetchall()

def delete_quiz(qid):
    c.execute("DELETE FROM quizzes WHERE id=?", (qid,))
    conn.commit()

# --- Streamlit UI ---
st.title("📘 Govt Exam Preparation Portal")

menu = st.sidebar.radio("Navigate", ["Home", "Resources", "Quizzes", "Admin"])

groups = ["Group 1", "Group 2", "Group 3"]



if menu == "Home":
    st.markdown("<h1 style='text-align: center;'>🚀 Govt Exam Preparation Portal</h1>", unsafe_allow_html=True)
    st.write("Welcome to your one-stop destination for Group 1, Group 2, and Group 3 exam preparation.")

    # Motivational Quote of the Day
    quotes = [
        "“Success is the sum of small efforts, repeated day in and day out.” – Robert Collier",
        "“The future depends on what you do today.” – Mahatma Gandhi",
        "“Push yourself, because no one else is going to do it for you.”",
        "“Dreams don’t work unless you do.” – John C. Maxwell",
        "“Believe you can and you're halfway there.” – Theodore Roosevelt"
    ]
    import random
    st.info(random.choice(quotes))

    # Features Section
    st.subheader("✨ What You’ll Find Here")
    st.markdown("""
    - 📚 **Study Resources**: Download PDFs categorized by Group 1, Group 2, and Group 3.
    - 📝 **Practice Quizzes**: Attempt MCQs with instant feedback and track your progress.
    - 🏆 **Motivation Hub**: Daily quotes and tips to keep you inspired.
    - 📢 **Announcements**: Stay updated with exam notifications and syllabus changes.
    """)

    # Call to Action
    st.success("💡 Tip: Start with your group’s resources, then test yourself with quizzes to measure progress!")
elif menu == "Resources":
    st.header("Study Resources")
    group_choice = st.selectbox("Select Group", groups, key="res_group_filter")
    for r in get_resources(group_choice):
        st.subheader(r[1])
        st.markdown(f"[Download PDF]({r[2]})")
        st.caption(f"Group: {r[3]}")

elif menu == "Quizzes":
    st.header("Practice Quizzes")
    group_choice = st.selectbox("Select Group", groups, key="quiz_group_filter")
    quizzes = get_quizzes(group_choice)
    score = 0
    for q in quizzes:
        st.write(f"**{q[1]}**")
        opts = q[2].split(",")
        choice = st.radio("Select answer:", opts, key=f"quiz_{q[0]}")
        if choice == opts[q[3]]:
            score += 1
    st.success(f"Your Score: {score}/{len(quizzes)}")

elif menu == "Admin":
    st.header("🔒 Admin Panel")

    # --- Password Protection ---
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        password = st.text_input("Enter Admin Password", type="password", key="admin_pass")
        if st.button("Login", key="admin_login_btn"):
            if password == "mysecret123":   # <-- set your own strong password here
                st.session_state.admin_authenticated = True
                st.success("Access granted ✅")
            else:
                st.error("Incorrect password ❌")
    else:
        st.success("Welcome, Admin! You have full access.")

        # --- Admin Features ---
        st.subheader("Add Resource")
        title = st.text_input("Title", key="res_title")
        subject = st.selectbox("Select Group", groups, key="res_subject")
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="res_pdf")
        if st.button("Add Resource", key="add_res_btn"):
            if pdf_file is not None:
                save_path = os.path.join("pdfs", pdf_file.name)
                os.makedirs("pdfs", exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                pdf_url = save_path
                add_resource(title, pdf_url, subject)
                st.success("Resource added!")
            else:
                st.error("Please upload a PDF file.")

        st.subheader("Manage Resources")
        for r in get_resources():
            st.write(f"{r[1]} ({r[3]})")
            if st.button(f"Delete {r[1]}", key=f"del_res_{r[0]}"):
                delete_resource(r[0])
                st.warning("Deleted!")

        st.subheader("Add Quiz")
        q_text = st.text_input("Question", key="quiz_question")
        q_opts = st.text_area("Options (comma separated)", key="quiz_options")
        q_ans = st.number_input("Correct Answer Index", min_value=0, key="quiz_answer")
        q_subject = st.selectbox("Select Group", groups, key="quiz_subject")
        if st.button("Add Quiz", key="add_quiz_btn"):
            add_quiz(q_text, q_opts.split(","), q_ans, q_subject)
            st.success("Quiz added!")

        st.subheader("Manage Quizzes")
        for q in get_quizzes():
            st.write(f"{q[1]} ({q[4]})")
            if st.button(f"Delete Quiz {q[0]}", key=f"del_quiz_{q[0]}"):
                delete_quiz(q[0])
                st.warning("Deleted!")