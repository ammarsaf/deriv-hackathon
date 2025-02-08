# Regenerating the PDF with specified inconsistencies
from fpdf import FPDF
from pathlib import Path
import random
from datetime import datetime, timedelta
import os
from tqdm import tqdm

# Sender
# Recipient
# Transaction amount
# Transaction ID
# Date and time

pdf_amount = 5
transaction_type = "Debit"
for _ in tqdm(range(pdf_amount), desc="generate pdf ..."):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)


    # Incorrect logo (simulated by just text, since we can't use actual logos)
    bank_random = random.choice([
        "Maybnk Berhad", "Publik Bank", "CIMD Bank", "Hong Leong Bnk", "RHB Banck",
        "AmBank Berhed", "UOB Malasia", "Allince Bank", "Standrd Chartered", "BSN Berhad"
    ])
    address_random = random.choice([
        "123, Jalan Ampnag, Kuala Lumpur",
        "456, Lebuh Queen, George Town, Penang",
        "789, Jalan Wong Ah Fook, Johor Bahru",
        "321, Persiaran Gurney, Penang",
        "654, Jalan Tun Razak, KL",
        "987, Jalan Merdeka, Melaka",
        "741, Jalan Bukit Bintang, KL",
        "852, Lorong Haji Taib, KL",
        "963, Jalan Sultan Ismail, KL",
        "159, Jalan Tebrau, Johor"
    ])
    acc_num_random = random.choice([random.randint(10**9, 10**10 - 1) for _ in range(10)])
    name_random =  random.choice([
        "Muhamad Fikr", "Norliah Binti Hsan", "Ahmd Hafiz", "Siti Norhaya", "Roslina Binte Yusof",
        "Faizal Rahma", "Nur Afiqqah", "Hassanul Bakar", "Azlina Bt Mhd", "Syahril Zainal"
    ])
    date_random = random.choice([(datetime(2025, 1, 1) + timedelta(days=random.randint(0, 364))).strftime("%Y-%m-%d") for _ in range(10)])
    times_random = random.choice([f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}" for _ in range(10)])

    pdf.cell(200, 10, f"{bank_random}", ln=True, align="C")
    pdf.set_text_color(255, 0, 0)  # Simulate a colorful logo (which is incorrect)
    # pdf.cell(200, 10, "Colorful Logo - Incorrect", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"{address_random}", ln=True, align="C")
    pdf.cell(200, 10, f"Customer Service: (000) 05-{acc_num_random}", ln=True, align="C")
    pdf.ln(10)

    # Account Info
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Account Statement", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Account Holder: {name_random}", ln=True)
    pdf.cell(200, 10, f"Account Number: {acc_num_random}", ln=True)
    pdf.cell(200, 10, f"Statement Date: {date_random}", ln=True)
    pdf.cell(200, 10, f"Statement Time: {times_random}", ln=True)
    pdf.cell(200, 10, f"Transaction ID: 00000{acc_num_random}", ln=True)

    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Date", 1)
    pdf.cell(60, 10, "Name", 1)
    pdf.cell(30, 10, "Type", 1)
    pdf.cell(30, 10, "Amount", 1)
    pdf.cell(30, 10, "Balance", 1)
    pdf.ln()

    # Generate faulty transactions
    start_balance = 5000.00  # Start balance
    transactions = []
    start_date = datetime.today() - timedelta(days=30)

    for i in range(1):
        # Incorrect reverse chronological order
        date = start_date + timedelta(days=30 - i)
        
        # description = random.choice(["ATM Withdrawl", "POS Purchaze", "Salary Creditt", "Onlne Transfer", "Bil Payment"])  # Typos included
        reciever = random.choice([
        "Muhamad Fikr", "Norliah Binti Hsan", "Ahmd Hafiz", "Siti Norhaya", "Roslina Binte Yusof",
        "Faizal Rahma", "Nur Afiqqah", "Hassanul Bakar", "Azlina Bt Mhd", "Syahril Zainal"
    ])
        amount = round(random.uniform(100, 1000), 0)  # Too many round numbers
        # transaction_type = random.choice(["Buy", "Sell"])
        
        # Incorrect balance calculation
        if transaction_type == "Buy":
            start_balance += amount  # Should subtract, but we add to make it wrong
        else:
            start_balance -= amount  # Should add, but we subtract to make it wrong

        transactions.append((date.strftime("%Y-%m-%d"), 
                            reciever, 
                            transaction_type, 
                            f"${amount:.2f}", 
                            f"${start_balance:.2f}"))

    # Repeated transaction IDs (incorrect)
    for transaction in transactions:
        for col in transaction:
            pdf.cell(40 if col == transaction[0] else (60 if col == transaction[1] else 30), 10, col, 1)
        pdf.ln()

    # Wrong Ending Balance
    pdf.cell(200, 10, f"Ending Balance: ${amount}", ln=True, align="L")

    # Save PDF
    current_pwd = Path(os.getcwd())
    pdf_path = current_pwd / "fake_pdfs"
    pdf_name = f"fake_bank_{acc_num_random}.pdf"
    pdf.output(pdf_path / pdf_name)
