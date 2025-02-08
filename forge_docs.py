import openai
import pdf2image
import os
import base64
import streamlit as st

api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key)

# pdf_path = "../deriv_fake_transactions/fake_bank_1182032140.pdf"
output_folder = "images"


def docs_forger_classifier(pdf_path, role):
    if role == "buyer":
        images = pdf2image.convert_from_bytes(pdf_path)
    elif role == "seller":
        images = pdf2image.convert_from_path(pdf_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    img_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"page_{i+1}.png")
        img.save(img_path, "PNG")
        img_paths.append(img_path)

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    base64_image = encode_image(img_paths[0])

    requested_amount = "$1000"

    first_prompt = """
    You are an expert for Deriv peer-2-peer in document forgery detection.     
    Analyze the provided document images for any signs of tampering, inconsistencies, or anomalies.
    Provide a concise and detailed report based on your findings.

    This is list of what to check:
    2. Wrong Dates
    3. Wrong Deposits
    4. Different font
    5. Repeated transaction no.
    6. wrong ending balance.
    7. wrong withdraws.
    8. Spelling errors.
    9. Sign of alteration if can.

    Requested amount: {}

    ###########################################################

    Output in json:
    analysis: summarize and explain your findings
    document_info: key,value extraction for useful info
    forged_document_bool: if this document is forged

    """.format(
        requested_amount
    )
    # print(first_prompt)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": first_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=1024,
    )
    out = response.choices[0].message.content
    # print(out)

    requested_amount = 934

    second_prompt = """
    You are an expert for Deriv peer-2-peer in dispute resolution.
    You will receive document forgery results that act as proof of transfer and you will conduct a final review to resolve 
    such dispute between a buyer and a seller.

    ### Context
    Seller amount requested: {}
    Document forgery results and buyer transaction details:
    {}

    ###
    Output in json:
    dispute_verdict: choose the most likely outcome only - [buyer_not_paid, seller_not_released, buyer_underpaid, buyer_overpaid]
    analysis: step by step give your reasoning

    """.format(
        requested_amount, out
    )
    # print(second_prompt)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": second_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=1024,
    )
    out = response.choices[0].message.content

    # print(out)
    return out
