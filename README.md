# RAG-Based SAT Math Question Generator

This repository contains a project that demonstrates how to build and deploy a Retrieval-Augmented Generation (RAG) system tailored for generating SAT-style math questions. The system indexes PDF documents into [Pinecone](https://www.pinecone.io/) as a vector database, then uses [OpenAI’s GPT models](https://openai.com/) via [LangChain](https://github.com/hwchase17/langchain) to retrieve context and create original math questions.

Below is a detailed overview of how this project works, how to set it up, and how to use its different components.

---
## Overview

The main objective of this project is to create a set of SAT-level math questions given:

1. **Contextual Material** – A set of PDF documents (e.g., practice exams, lesson materials) that are indexed in a vector store (Pinecone).
2. **User Instructions** – A user prompt specifying a topic, difficulty, language, and any additional instructions.

The system retrieves the most relevant pieces of text from the indexed PDFs and uses them to guide the generation of new SAT math questions. The output is rendered in Markdown and optionally downloadable as a PDF.

---

## Project Structure

The repository includes the following key files and directories:

```
.
├── env/                      # (Optional) Python virtual environment directory
├── .env                      # Environment variables (not committed to source)
├── requirements.txt          # Python dependencies
├── main_indexer.py           # Script to index PDF files into Pinecone
├── sat_question_generator.py  # Streamlit application for generating questions
├── stateless_rag.py          # Retrieval chain setup using LangChain
├── README.md                 # This README
```

Below is a high-level overview of each file:

1. **`main_indexer.py`**  
   - Recursively walks a directory containing PDF files.  
   - Splits them into text chunks.  
   - Generates embeddings and indexes these chunks into Pinecone.

2. **`sat_question_generator.py`**  
   - A [Streamlit](https://streamlit.io/) application providing a GUI for users to input prompt details (e.g., topic, difficulty, language).  
   - Calls the retrieval-augmented generation chain to produce SAT math questions.  
   - Allows downloading generated questions as a PDF.

3. **`stateless_rag.py`**  
   - Sets up the retrieval chain in a stateless manner (no conversation history).  
   - Defines a prompt that fetches context from Pinecone using a [LangChain Retriever](https://github.com/hwchase17/langchain) and then uses an OpenAI chat model to generate new questions.

4. **`.env`**  
   - Contains essential environment variables like `OPENAI_API_KEY`, `ROOT_DIRECTORY`, and `INDEX_NAME`.  
   - **Note**: This file is not committed to version control for security reasons.

---

## Features

- **PDF-to-Vector Indexing**: Converts PDF documents into embeddings and stores them in Pinecone.  
- **Context-Aware Generation**: Pulls the most relevant chunks from Pinecone to guide GPT-based generation.  
- **Streamlit Frontend**: Simple interface to customize prompt parameters, generate questions, and optionally download as PDF.  
- **Markdown & PDF Output**: Renders the final output in Markdown and provides a PDF download for easy distribution.

---

## Installation & Setup

### Prerequisites

1. **Python 3.8+**  
2. **Pinecone account**  
   - You will need to create a Pinecone index and have your API key ready.  
   - [Sign up for Pinecone here.](https://www.pinecone.io/)  
3. **OpenAI API key**  
   - [Sign up for OpenAI here.](https://openai.com/api/)  

### Environment Variables

Create a file named `.env` in the root directory of your project with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
INDEX_NAME=your_pinecone_index_name
ROOT_DIRECTORY=/absolute/or/relative/path/to/your/pdf/folder
```

- `OPENAI_API_KEY`: Your OpenAI API key.
- `PINECONE_API_KEY`: Your Pinecone API key.
- `INDEX_NAME`: The name of the Pinecone index you created.
- `ROOT_DIRECTORY`: Path to the folder that contains PDF files to be indexed.

**Note**: Depending on how you provision your Pinecone client, you may also need `PINECONE_API_KEY` and `PINECONE_ENV` stored in environment variables. Make sure to update any references in the code if needed.

### Installing Dependencies

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Create a Virtual Environment (optional but recommended)**  
   ```bash
   python -m venv env
   source env/bin/activate  # On macOS/Linux
   env\Scripts\activate     # On Windows
   ```

3. **Install Python Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

Ensure that your `.env` file is properly configured before proceeding to the next steps.

---

## Indexing Your PDFs

Once your environment is set up, you’ll need to index the PDF documents:

1. Place all PDF files in the folder specified by `ROOT_DIRECTORY` in your `.env`.
2. Run the indexer script:
   ```bash
   python main_indexer.py
   ```
3. This script will:
   - Recursively scan the `ROOT_DIRECTORY` for PDFs.
   - Split their content into chunks using a text splitter.
   - Generate embeddings for each chunk.
   - Store these embeddings in the Pinecone index named in `INDEX_NAME`.

**Note**: If you have many PDFs or large PDFs, indexing might take some time. You can monitor the progress via `tqdm` progress bars.

---

## Running the Streamlit App

1. **Start Streamlit**:
   ```bash
   streamlit run sat_question_generator.py
   ```
2. **Open the Browser**:  
   Streamlit will either open automatically or prompt a URL (usually [http://localhost:8501](http://localhost:8501)).

3. **Use the App**:  
   - Fill in the prompt details: topic, difficulty level, language, and any special instructions.  
   - Click **Generate**.  
   - The application will display three new SAT-level questions, formatted in Markdown.  
   - If you checked **Generate PDF output**, you can download the questions as a PDF.

---

## How the Retrieval Chain Works

1. **Document Retrieval**:  
   The user’s prompt is taken by `stateless_rag.py`, which uses a [Retriever](https://python.langchain.com/en/latest/modules/indexes/retrievers.html) from Pinecone.  
   - The PineconeVectorStore fetches the most semantically similar chunks to the user query from the Pinecone index.

2. **Prompt Construction**:  
   - A ChatPromptTemplate is used to inject the retrieved context (`{context}`) alongside the user input (`{input}`) into a single prompt.  
   - The prompt instructs the LLM to generate 3 SAT questions without providing solutions or explanations.

3. **LLM Generation**:  
   - [OpenAI GPT](https://beta.openai.com/docs/) processes the constructed prompt and returns the final Markdown content.  
   - The system ensures the new questions are original by drawing upon the retrieved context as just “inspiration” or guidelines.

---

## Customization & Extension

- **Changing the Model**:  
  In `stateless_rag.py`, you can set `model` to a different GPT model (e.g., `"gpt-3.5-turbo"`) in the `ChatOpenAI` constructor.
  
- **Modifying the Prompt**:  
  Adjust the `ChatPromptTemplate` in `stateless_rag.py` to alter how the final questions are generated (e.g., requiring multiple choice format, adding steps, etc.).

- **Scaling to Other Subjects**:  
  Although this project focuses on SAT math, you can reuse the architecture for other subjects (e.g., reading comprehension, science). Simply replace the content in Pinecone or alter the instructions.

- **Alternative Frontends**:  
  If Streamlit does not suit your needs, you could wrap the same chain in a Flask or FastAPI backend or integrate it into another application.
