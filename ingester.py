import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from tqdm import tqdm

def get_pdf_paths(root_dir):
    # Get all PDF paths recursively
    pdf_paths = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                pdf_paths.append(os.path.join(dirpath, filename))
    return pdf_paths

def main():
    load_dotenv()
    
    root_dir = os.environ["ROOT_DIRECTORY"]
    pdf_paths = get_pdf_paths(root_dir)
    
    if not pdf_paths:
        raise ValueError("No PDFs found")
    
    # Initialization of components required for vector store
    text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    index_name = os.environ["INDEX_NAME"]
    vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    
    # Process files
    for pdf_path in tqdm(pdf_paths,  desc="Processing PDFs", unit="file"):

        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            chunks = text_splitter.split_documents(docs)
            
            # Add to existing vector store
            vector_store.add_documents(chunks)
            
        except Exception as e:
            print(f"Failed to process {pdf_path}: {str(e)}")

if __name__ == "__main__":
    main()