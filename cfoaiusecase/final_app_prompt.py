import openai
import re
import streamlit as st
from prompts import get_system_prompt
from prompts_excel import get_system_prompt_excel
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
import time

st.title("\U0001F451"+" FIL SnowBot")

nav = st.sidebar.radio("Navigation",["Snowflake","Document"])
if nav == "Snowflake":

    # Initialize the chat messages history
    openai.api_key = st.secrets.OPENAI_API_KEY
    if "messages" not in st.session_state:
        # system prompt includes table information, rules, and prompts the LLM to produce
        # a welcome message to the user.
        st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

    # Prompt for user input and save
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        
    # display the existing chat messages
    for message in st.session_state.messages:
        #st.text(message)
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "results" in message:
                st.dataframe(message["results"])

    # If last message is not from assistant, we need to generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = ""
            resp_container = st.empty()
            for delta in openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            ):
                response += delta.choices[0].delta.get("content", "")
                resp_container.markdown(response)

            message = {"role": "assistant", "content": response}
            # Parse the response for a SQL query and execute if available
            sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
            time.sleep(10)
            if sql_match:
                sql = sql_match.group(1)
                conn = st.experimental_connection("snowpark")
                message["results"] = conn.query(sql)
                st.dataframe(message["results"])
            st.session_state.messages.append(message)

if nav=="Document":
    openai_api_key = st.secrets.OPENAI_API_KEY

    def construct_index(directory_path):
        max_input_size = 4096
        num_outputs = 512
        chunk_overlap_ratio = 0.2
        chunk_size_limit = 600

        prompt_helper = PromptHelper(max_input_size, num_outputs, chunk_overlap_ratio, chunk_size_limit=chunk_size_limit)

        llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo-16k", max_tokens=num_outputs))

        documents = SimpleDirectoryReader(directory_path).load_data()

        index = GPTSimpleVectorIndex(documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper)

        index.save_to_disk('index.json')

        return index

    def chatbot(messages):
        index = GPTSimpleVectorIndex.load_from_disk('index.json')
        response = ""

        for delta in openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,  # Pass the entire conversation history as messages
            stream=True,
        ):
            response += delta.choices[0].delta.get("content", "")

        return response

    system_prompt=get_system_prompt_excel()

    def main():
        st.write("Please Upload your document")

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
                with open(os.path.join(tmp_dir, "uploaded_file.txt"), "w", encoding='utf-8') as f:
                    f.write(text_data)

                openai.api_key = openai_api_key

                index = construct_index(tmp_dir)
                st.text("File has been uploaded. You can now start chatting with the AI Bot!")

                user_input = st.text_area("Enter your text:")
                if user_input:
                    # Initialize messages with the system prompt
                    messages = [{"role": "system", "content": system_prompt}]
                    
                    response = chatbot(messages)

                    # Store the current user input and AI response in session_state
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    st.text_input("AI Response:")
                    st.write(response)

                    # Add user input to the messages
                    # messages.append({"role": "user", "content": user_input})

                    # # Generate a response from the model using the messages
                    # response = chatbot(messages)

                    # st.text_input("AI Response:")
                    # st.write(response)



    if __name__ == "__main__":
        main()