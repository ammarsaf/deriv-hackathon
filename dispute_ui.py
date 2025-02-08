import streamlit as st
from openai import OpenAI

SELLER_PROMPT_BEHAVIOR = """
    You are a seller from Deriv who want to sell 1 BTC for RM1000. 
    You try to deviate the conversation to Whatsapp, Telegram or other platform
    to continue the transaction process.
"""


def upload_pdf_sidebar():
    with st.sidebar:
        pdf_uploaded = st.file_uploader("Upload Transaction File")


def seller_conversation():
    # Set OpenAI API key from Streamlit secrets
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "system", "content": SELLER_PROMPT_BEHAVIOR},
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    st.title("AI Dispute Resolver")

    upload_pdf_sidebar()
    seller_conversation()
