from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from textwrap import dedent
from crewai_tools import PDFSearchTool

my_llm = ChatGroq(
    api_key="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",
    model="llama3-8b-8192",
)

# project = input("Enter a project: ")

pdf_tool = PDFSearchTool(
    pdf=r"C:/Users/HP/Downloads/APJ.pdf",
    config=dict(
        llm=dict(
            provider="groq",
            config=dict(
                model="llama3-8b-8192",
                api_key="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",
            ),
        ),
        embedder=dict(
            provider="ollama",
            config=dict(
                model="all-minilm:latest",
            ),
        ),
    ),
)

pdf_expert = Agent(
    role="PDF Expert",
    goal="Answer questions based on the content of the uploaded PDF",
    backstory="You are an AI assistant specialized in analyzing and answering questions about PDF documents.",
    llm=my_llm,
    verbose=True,
)


def create_question_task(question):
    return Task(
        description=f"""
        Your task is to analyze the content of the uploaded PDF document and provide an accurate answer to the following question:
        "{question}"
        
        Follow these steps:
        1. Carefully read and understand the content of the PDF.
        2. Interpret the user's question and identify the relevant information from the PDF.
        3. Formulate a clear, concise, and accurate answer based on the PDF content.
        4. If the question cannot be answered directly from the PDF, provide the most relevant information available and explain any limitations.
        5. Use quotes from the PDF where appropriate to support your answer.
        6. If clarification is needed, state that in your response.
        """,
        expected_output="""
        A comprehensive and accurate answer to the user's question, including:
        - Direct responses to the specific query
        - Relevant quotes or paraphrases from the PDF to support the answer
        - Clear explanations of any concepts from the PDF that are necessary to understand the answer
        - Identification of any areas where the PDF doesn't provide sufficient information to fully answer the question
        - Follow-up questions or clarifications if needed to provide a more complete answer
        
        The response should be well-structured, easy to understand, and directly address the user's query while showcasing a thorough understanding of the PDF content.
        """,
        tools=[pdf_tool],
        agent=pdf_expert,
    )


crew = Crew(
    agents=[pdf_expert],
    tasks=[],
    verbose=True,
)

# print(f"Project: {project}")
print("You can now ask questions about the PDF. Type 'exit' to end the session.")

while True:
    user_question = input("\nEnter your question: ")
    if user_question.lower() == "exit":
        break

    question_task = create_question_task(user_question)
    crew.tasks = [question_task]
    result = crew.kickoff()
    print("\nAnswer:", result)

print("Session ended. Thank you for using the PDF Q&A system!")


# import os
# from typing import List
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from pydantic import BaseModel
# from pypdf import PdfReader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain.llms import HuggingFacePipeline
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# app = FastAPI()

# # Initialize HuggingFace embeddings
# embeddings = HuggingFaceEmbeddings()

# # Initialize language model
# model_name = "google/flan-t5-base"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)
# pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_length=512)
# local_llm = HuggingFacePipeline(pipeline=pipe)

# # Vector store
# vector_store = None

# def process_pdf(pdf_file: UploadFile) -> List[str]:
#     pdf_reader = PdfReader(pdf_file.file)
#     text = ""
#     for page in pdf_reader.pages:
#         text += page.extract_text()
    
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len
#     )
#     chunks = text_splitter.split_text(text=text)
#     return chunks

# def create_vector_store(chunks: List[str]):
#     global vector_store
#     vector_store = FAISS.from_texts(chunks, embedding=embeddings)

# class Question(BaseModel):
#     text: str

# @app.post("/upload-pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     if file.filename.endswith(".pdf"):
#         chunks = process_pdf(file)
#         create_vector_store(chunks)
#         return {"message": "PDF processed and vector store created successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF.")

# @app.post("/ask-question/")
# async def ask_question(question: Question):
#     if vector_store is None:
#         raise HTTPException(status_code=400, detail="Please upload a PDF first")
    
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=local_llm,
#         chain_type="stuff",
#         retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
#         return_source_documents=True
#     )
    
#     response = qa_chain({"query": question.text})
#     return {
#         "answer": response['result'],
#         "sources": [doc.page_content for doc in response['source_documents']]
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)