import streamlit as st
from openai import OpenAI
from forge_docs_llm import llm_forge_docs

SELLER_PROMPT_BEHAVIOR = """
    You are a seller from Deriv who want to sell 1 BTC for $1000. 
    You try to deviate the conversation to Whatsapp, Telegram or other platform
    to continue the transaction process.
    Please follow this system prompt. 
"""


def upload_pdf_sidebar():
    with st.sidebar:
        pdf_uploaded = st.file_uploader("Upload Transaction File")
        if pdf_uploaded:
            user_output = llm_forge_docs(pdf_uploaded)  # legit pdf
            # scammer_output = llm_forge_docs("...")  # scammer pdf
            return user_output


def seller_conversation():
    # Set OpenAI API key from Streamlit secrets
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # output state
    if "aioutput" not in st.session_state:
        st.session_state.aioutput = []

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
            st.session_state.aioutput.append(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        deviate_warning()

    # st.write(st.session_state.messages)
    # st.write(st.session_state.aioutput)


def deviate_warning():
    response: list = st.session_state.aioutput
    if len(response) > 0:
        # st.write(response)
        for i in range(len(response)):
            if "Whatsapp" in response[i] or "Telegram" in response[i]:
                st.warning(
                    "Warning: Seller try to deviate transaction from this platform!"
                )
            else:
                return


if __name__ == "__main__":
    st.title("AI Dispute Resolver")
    tab_chat, tab_analysis = st.tabs(["Chat", "Analysis"])

    upload_pdf_sidebar()

    with tab_chat:
        seller_conversation()

    with tab_analysis:
        analyze_button = st.button("Analyze")

        st.title("Conversation Analysis")

        st.title("Document Forge Analysis")
