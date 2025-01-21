import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
import markdown
from weasyprint import HTML

# Load environment variables first
load_dotenv()

# Initialize components
embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
vectorstore = PineconeVectorStore(
    index_name=os.environ["INDEX_NAME"],
    embedding=embeddings
)

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    openai_api_key=os.environ["OPENAI_API_KEY"]
)

prompt = ChatPromptTemplate.from_template("""
You are an expert SAT math tutor tasked with creating practice questions based on user input and provided context. Your goal is to generate challenging, original SAT-level math questions that are relevant to the topic requested.

First, review the following context, which contains similar questions to guide your creation process:

{context}

Now, consider the user's input requesting specific types of questions:

{input}

Based on the context and user input, follow these instructions:

1. Generate 3 challenging SAT-level math questions related to the topic specified in the user's input.
2. Ensure that each question is original and not a direct copy of any question in the provided context.
3. Make sure the questions are relevant to the SAT math section and appropriate for SAT-level difficulty.
4. Format your entire response in Markdown, including mathematical notation and equations.
5. Do not include any additional commentary, explanations, or unrelated information.
6. Present only the questions themselves, without answers or solutions.

Your response should contain exactly 3 questions, each formatted in Markdown and numbered consecutively.

Fill in the answer in answer tags like this: 
                                          
<Answer>
answer
</Answer>
""")


# Create retrieval chain
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

chain = create_retrieval_chain(retriever, prompt | llm)

question = "Give me challenging practice questions about algebraic inequalities with explanations"
result = chain.invoke({"input": question})