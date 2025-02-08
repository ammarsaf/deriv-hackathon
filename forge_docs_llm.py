import base64
import requests
import streamlit as st

# OpenAI API Key
api_key = st.secrets["OPENAI_API_KEY"]

LLM_FORGE_DOCS_PROMPT = "You are classifying whether the file is forge or not."  # TODO


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def llm_forge_docs(image_path):
    # image_path = "path_to_your_image.jpg"

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": LLM_FORGE_DOCS_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
            {"role": "system", "content": LLM_FORGE_DOCS_PROMPT},
        ],
        "max_tokens": 300,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    return response.json()
