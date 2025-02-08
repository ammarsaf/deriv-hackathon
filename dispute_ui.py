import streamlit as st
from openai import OpenAI
from forge_docs import docs_forger_classifier
from io import StringIO
import json
import ast

SELLER_PROMPT_BEHAVIOR = """
    You are a seller from Deriv who want to sell 1 BTC for $1000. 
    You try to deviate the conversation to Whatsapp, Telegram or other platform
    to continue the transaction process.
    Please follow this system prompt. 
"""


def upload_pdf_sidebar():
    if "forger" not in st.session_state:
        st.session_state.forger = []

    with st.sidebar:
        pdf_uploaded = st.file_uploader("Upload Transaction File")

        if pdf_uploaded:
            # stringio = StringIO(pdf_uploaded.getvalue().decode("utf-8"))

            buyer_output = docs_forger_classifier(
                pdf_uploaded.read(), role="buyer"
            )  # legit pdf
            # seller_output = llm_forge_docs("...")  # scammer pdf
            # st.write(buyer_output)

            st.session_state.forger.append(buyer_output)


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

    if "conversation" not in st.session_state:
        st.session_state.conversation = []

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

        st.session_state.conversation.append({"user": prompt, "system": response})
        st.session_state.messages.append({"role": "assistant", "content": response})


def deviate_warning(response):
    # st.write(response)
    # for i in range(len(response)):
    if "whatsapp" in response.lower() or "telegram" in response.lower():

        st.error("Warning: Seller try to deviate transaction from this platform!")
    else:
        return


def analyse_conversation(): ...  # TODO


if __name__ == "__main__":
    st.title("AI Dispute Resolver")
    tab_chat, tab_analysis = st.tabs(["Chat", "Analysis"])

    upload_pdf_sidebar()

    with tab_chat:
        seller_conversation()
        for res in st.session_state.aioutput:
            deviate_warning(res)

    with tab_analysis:
        analyze_button = st.button("Analyze")

        st.title("Conversation Analysis")
        analyse_conversation()

        st.title("Document Forge Analysis")
        if st.session_state.forger:
            dict_out = st.session_state.forger[0]
            json_out = json.loads(dict_out.replace("`", "").replace("json", ""))

            st.header("Dispute verdict")
            st.write(" ".join(json_out["dispute_verdict"].split("_")).title())

            st.header("Analysis")
            # for out in json_out["analysis"]:
            # st.write(type(json_out["analysis"]))
            for i in json_out["analysis"]:
                st.write(i)

                # st.write(dict_out["dispute_verdict"])
                # st.write(dict_out["analysis"])
