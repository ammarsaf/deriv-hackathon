import openai
import pdf2image
import os
import base64
import streamlit as st

api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key)

# pdf_path = "../deriv_fake_transactions/fake_bank_1182032140.pdf"
output_folder = "images"

def docs_forger_classifier(pdf_path, role, requested_amount: int = 1000):
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
        <OBJECTIVE>
        You are an expert in document forgery detection for the Deriv Peer-to-Peer platform.  
        Your task is to analyze provided document images for any signs of tampering, inconsistencies, or anomalies.  
        Provide a concise and detailed report based on your findings.  

        </OBJECTIVE>  

        <CHECKLIST>  
        Examine the document for the following forgery indicators:  
        1. **Wrong Dates** – Bank statements should follow a reverse chronological order.  
        2. **Wrong Deposits** – Inconsistencies in deposit amounts.  
        3. **Different Fonts** – Variations in text style that suggest manual edits.  
        4. **Repeated Transaction Numbers** – Duplicated transaction IDs, which are suspicious.  
        5. **Wrong Ending/Beginning Balance** – Mismatches in balance calculations.  
        6. **Wrong Withdrawals** – Unusual or inconsistent withdrawal amounts.  
        7. **Spelling Errors** – Typos or grammatical errors in financial documents.  
        8. **Signs of Alteration** – Inconsistencies in fonts, formatting, logos, paper quality, or alignment, indicating cut-and-paste editing.  
        9. **Too Many Round Numbers** – An unusually high number of round figures, which may indicate fabricated transactions.  

        </CHECKLIST>

        <RESPONSE_SCHEMA>  
        Your response should be in JSON format with the following fields:  

        ```json
            "analysis": "Summarize and explain your findings.",  
            "document_info": { "key": "value" },  
            "forged_document_bool": true/false (if any of the documents are forged or not)
        ```
    """

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

    second_prompt = """
        <OBJECTIVE>  
        You are an expert in dispute resolution for Deriv Peer-to-Peer transactions.  
        Your role is to analyze document forgery results that act as proof of transfer and conduct a final review to resolve disputes between a buyer and a seller.  

        </OBJECTIVE>

        <CONTEXT>  
        **Seller Requested Amount:** {requested_amount}  
        **Document Forgery Results & Buyer Transaction Details:**  
        {out}  
        </CONTEXT>  

        <EVALUATION_CRITERIA>  
        Determine the dispute verdict based on the following conditions:  
        - If the documents are forged → **"dispute_verdict": "buyer_not_paid"**  
        - If the buyer underpaid the seller (amount transacted < requested amount) → **"dispute_verdict": "buyer_underpaid"**  
        - If the buyer overpaid the seller (amount transacted > requested amount) → **"dispute_verdict": "buyer_overpaid"**  
        - If the seller did not specify a requested amount → **"dispute_verdict": "seller_not_released"**  

        </EVALUATION_CRITERIA>  

        <OUTPUT_FORMAT>  
        Your response should be in JSON format:  

        ```json
            "dispute_verdict": "buyer_not_paid",  
            "analysis": "Step-by-step explanation of how the verdict was reached."
        ```
    """.format(
        requested_amount, out
    )

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

    return out
