from typing import Dict, List

import openai
import streamlit as st

client = openai.OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

def fraud_detector(conversation_history: List[Dict[str, str]]) -> Dict[str, str]:

    prompt = """
    <OBJECTIVE>  
    You are an AI tool designed to detect fraud between buyers and sellers and automate
    dispute resolution on the Deriv Peer-2-Peer platform. Your role involves two phases:

    1. **Before a Dispute is Raised**:  
    - Clients communicate through the P2P chatbox to discuss transaction details.  
    - Your goal is to analyze chat conversations for suspicious keywords indicating potential fraud.  
    - If fraud is suspected, you must take appropriate action to prevent fund loss.  

    </OBJECTIVE>  

    <DETECTION_CRITERIA>  
    AI should flag and act upon the following suspicious behavior:  

    1. **Example Suspicious Phrases**:  
    - "Let's continue on WhatsApp"  
    - "We can talk on Telegram"  
    - "Let's move to Messenger"  
    - "Switch to Signal"  
    - "Continue on WeChat"  
    - "Talk on Viber"  

    2. **Unauthorized Money Transfers**:  
    - Cases where thieves transfer money from a user's P2P account without permission.  
    - This often occurs via stolen login credentials obtained through phishing.  
    - Fraudsters may change account settings to prevent victims from stopping transfers.  

    </DETECTION_CRITERIA>  

    <INPUT>  
    conversation_history: {}  
    </INPUT>  

    <RESPONSE_SCHEMA>  
    Your response must be formatted as JSON with the following fields:  

    - **suspicious_keywords**: `List[str]` (Keywords detected in the conversation)  
    - **actions**: `List[str]` (One from: `block_fund_access`, `alert_cashier`, `alert_user`, `no_action`)  
    - **analysis**: `str` (Explanation of why the conversation is flagged or not)  

    Example Output:
    ```json
        - "suspicious_keywords": ["Let's continue on WhatsApp"],  
        - "actions": ["alert_user"],  
        - "analysis": "User is attempting to move the conversation outside the platform, which is a common fraud tactic."
    ```
    """.format(conversation_history)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt},
                ],
            }
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    conversation_history = """[
        {
        "buyer": "Hi, I want to buy $200 worth of USDT. Can we continue on WhatsApp? It'll be faster there. My number is +123456789.",
        "seller": "Sure! Let's move to WhatsApp. It'll be easier to share payment details there."
        }
    ]
    """

    x = fraud_detector(conversation_history)
    print(x)
