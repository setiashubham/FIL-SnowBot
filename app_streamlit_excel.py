from gpt_index import SimpleDirectoryReader, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain.chat_models import ChatOpenAI
import streamlit as st
import pandas as pd
import os
import openai
import tempfile
import openpyxl
import PyPDF2
import lightning


openai_api_key = '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'

def construct_index(directory_path):
    max_input_size = 4096
    num_outputs = 512
    chunk_overlap_ratio = 0.2
    chunk_size_limit = 600

    prompt_helper = PromptHelper(max_input_size, num_outputs, chunk_overlap_ratio, chunk_size_limit=chunk_size_limit)

    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", max_tokens=num_outputs))

    documents = SimpleDirectoryReader(directory_path).load_data()

    index = GPTSimpleVectorIndex(documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper)

    index.save_to_disk('index.json')

    return index

def chatbot(input_text):
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    response = index.query(input_text, response_mode="compact")
    return response.response

def main():
    st.title("Custom-trained AI Chatbot")

    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "txt", "xlsx", "xls"])
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_data = "\n".join([page.extract_text() for page in pdf_reader.pages])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or uploaded_file.type == "application/vnd.ms-excel":
            df = pd.read_excel(uploaded_file)
            text_data = "\n".join(df.iloc[:, 0].astype(str).tolist())
        else:
            text_data = uploaded_file.getvalue().decode()

        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, "uploaded_file.txt"), "w") as f:
                f.write(text_data)

            openai.api_key = openai_api_key

            index = construct_index(tmp_dir)
            st.text("File has been uploaded. You can now start chatting with the AI Bot!")

            user_input = st.text_area("Enter your text:")
            if user_input:
                response = chatbot(user_input)
                st.text_input("AI Response:")
                st.write(response)


if __name__ == "__main__":
    main()
