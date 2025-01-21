
import streamlit as st
from stateless_rag import chain
import markdown
from weasyprint import HTML
import tempfile
import re

def generate_sat_questions(user_input: str) -> str:
    """
    Invoke the retrieval chain with the user input.
    Returns only the text found between <Answer> and </Answer>, if present.
    """
    response = chain.invoke({"input": user_input})
    full_text = response["answer"].content


    pattern = re.compile(r"<Answer>\s*(.*?)\s*</Answer>", re.DOTALL)
    match = pattern.search(full_text)
    if match:
        answer_text = match.group(1)
    else:
        answer_text = full_text

    answer_text = re.sub(r"```markdown", "```", answer_text)

    return answer_text

def convert_markdown_to_pdf(md_text: str) -> bytes:
    """
    Convert the given Markdown text to PDF in-memory and return the binary content.
    Includes the 'fenced_code' extension to render triple backticks properly.
    """
    html_content = markdown.markdown(
        md_text, 
        extensions=["fenced_code"]
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        HTML(string=html_content).write_pdf(tmpfile.name)
        tmpfile.seek(0)
        pdf_bytes = tmpfile.read()
    return pdf_bytes

def main():
    # --- Page Configuration ---
    st.set_page_config(page_title="RAG Based SAT Math Question Generator", layout="centered")

    # --- Title & Description ---
    st.title("SAT Math Practice Question Generator")
    st.write(
        "This app leverages OpenAI and Pinecone to generate challenging SAT math questions.\n"
        "Customize the prompt details below and click **Generate**."
    )

    # --- Additional Settings (Main Layout) ---
    st.subheader("Additional Settings")

    # Difficulty selection
    difficulty_level = st.selectbox(
        "Choose difficulty:",
        ["Easy", "Moderate", "Hard"],
        index=1
    )

    # Language selection
    language = st.selectbox(
        "Choose language:",
        ["English", "Spanish", "French", "German", "Other"]
    )

    # Toggle to create PDF
    create_pdf = st.checkbox("Generate PDF output", value=False)

    # --- User Input ---
    st.subheader("Prompt Details")
    user_topic = st.text_input("Topic (e.g., 'algebraic inequalities')", value="algebraic inequalities")
    user_extras = st.text_area("Any special requests or instructions?", value="Please include more word problems.")

    user_input = (
        f"Topic: {user_topic}\n"
        f"Difficulty Level: {difficulty_level}\n"
        f"Language: {language}\n"
        f"Additional Instructions: {user_extras}\n"
        "Please generate the questions."
    )

    # --- Generate Button ---
    if st.button("Generate"):
        with st.spinner("Generating questions..."):
            result_text = generate_sat_questions(user_input)
            if result_text:
                st.markdown("## Generated SAT Math Questions")
                st.markdown(result_text)

                if create_pdf:
                    # Convert the generated Markdown to PDF
                    pdf_content = convert_markdown_to_pdf(result_text)
                    st.download_button(
                        label="Download PDF",
                        data=pdf_content,
                        file_name="sat_math_questions.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("No response was generated. Please try again.")

if __name__ == "__main__":
    main()