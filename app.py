# import json
# import requests
# import streamlit as st
# from dotenv import load_dotenv
# from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
# from langchain_core.messages import SystemMessage, HumanMessage
# import os
# import pandas as pd

# load_dotenv()

# llm = HuggingFaceEndpoint(
#     repo_id="meta-llama/Llama-3.1-8B-Instruct:novita",
#     task="text-generation",
#     max_new_tokens=512,
#     temperature=0.2
# )

# model = ChatHuggingFace(llm=llm)

# system_prompt = SystemMessage(
#     content="""
# You are an AI Personal Expense Tracker.

# Your job is to extract transaction information from the user's sentence.

# Return ONLY valid JSON.

# Schema:

# {
#     "category": "",
#     "amount": null,
#     "currency": "INR",
#     "expense": "",
#     "account": "",
#     "transaction_type": "",
#     "title": "",
#     "note": ""
#  }

# Rules:

# 1. If the user spends money, set "category" to "debit".

# 2. If the user receives money, set "category" to "credit".

# 3. "expense" represents the expense category. Choose only one from:
# food
# fuel
# shopping
# travel
# medical
# recharge
# other

# 4. "transaction_type" represents the payment mode. Choose only one from:
# cash
# online

# 5. "account" should be one of:
# UCOBANK
# INDUSIND
# CASH

# 6. "amount" should contain only the numeric value.

# 7. "currency" should always be "INR" unless another currency is mentioned.

# 8. "title" should be very short (1-3 words).
# Examples:
# Coffee
# Pizza
# Petrol
# Recharge
# Medicine
# Shopping

# 9. "note" should be a complete English sentence describing the transaction.

# 10. If any value is not available, return null.

# 11. Return ONLY valid JSON.

# Example 1

# Input:
# I spent 500 on food by online through my UCO account.

# Output:

# {
#     "category":"debit",
#     "amount":500,
#     "currency":"INR",
#     "expense":"food",
#     "account":"UCO",
#     "transaction_type":"online",
#     "title":"Food",
#     "note":"I spent ₹500 on food using my UCO account through online payment."
#  }

# Example 2

# Input:
# I bought coffee worth 250 using my UCO account.

# Output:

# {
#     "category":"debit",
#     "amount":250,
#     "currency":"INR",
#     "expense":"food",
#     "account":"UCO",
#     "transaction_type":"online",
#     "title":"coffee",
#     "note":"I bought a coffee worth ₹250 using my UCO account." 
# }

# Example 3

# Input:
# I received 50000 salary in my INDUSIND account.

# Output:

# {
#     "category":"credit",
#     "amount":50000,
#     "currency":"INR",
#     "expense":null,
#     "account":"INDUSIND",
#     "transaction_type":null,
#     "title":"Salary",
#     "note":"I received a salary of ₹50,000 in my INDUSIND account." 
# }
# """
# )

# summary_prompt = SystemMessage(
#     content="""You are an AI Financial Analyst. 
# Your task is to analyze the provided JSON transaction history and generate a short, professional, and friendly executive summary.

# Provide:
# 1. A brief overview of the spending patterns.
# 2. Where the user is spending the most (e.g., Food, Shopping).
# 3. A small actionable tip or insight to improve financial health.

# Keep the response strictly under 4-5 sentences and directly address the user."""
# )

# st.set_page_config(page_title="AI Expense Tracker")

# st.title("AI Expense Tracker")

# # --- SECTION 1: SAVE TRANSACTION (POST API) ---
# st.header("Record Transaction")
# user_input = st.text_area(
#     "Enter your transaction",
#     placeholder="Example: I spent 500 on food by online through my UCO account."
# )

# if st.button("Save Transaction"):
#     messages = [
#         system_prompt,
#         HumanMessage(content=user_input)
#     ]

#     with st.spinner("Understanding your transaction..."):
#         response = model.invoke(messages)

#         try:
#             data = json.loads(response.content)

#             url = "https://dev294864.service-now.com/api/x_1879157_expens_0/expense_tracker_api/addTransaction"

#             r = requests.post(
#                 url,
#                 auth=(
#                     os.getenv("SN_USERNAME"),
#                     os.getenv("SN_PASSWORD")
#                 ),
#                 headers={
#                     "Content-Type": "application/json",
#                     "Accept": "application/json"
#                 },
#                 json=data,
#                 timeout=30
#             )

#             if r.status_code in [200, 201]:
#                 st.success("transaction recorded successfully")
#             else:
#                 st.error("not")

#         except Exception as e:
#             st.error("not")
#             st.text(response.content)
#             st.exception(e)

# st.markdown("---")

# # --- SECTION 2: FETCH DETAILS (GET API ON MAIN PAGE) ---
# st.header("Financial Dashboard")

# if st.button("Get Detail Transaction"):
#     get_url = "https://dev294864.service-now.com/api/x_1879157_expens_0/expense_tracker_api/getTransactions"
    
#     with st.spinner("Fetching historical data from ServiceNow..."):
#         try:
#             r_get = requests.get(
#                 get_url,
#                 auth=(os.getenv("SN_USERNAME"), os.getenv("SN_PASSWORD")),
#                 headers={"Accept": "application/json"},
#                 timeout=30
#             )
            
#             if r_get.status_code == 200:
#                 json_response = r_get.json()
#                 transactions = json_response.get("result", {}).get("transactions", [])
                
#                 total_debit = 0.0
#                 total_credit = 0.0
                
#                 # Dictionaries to aggregate expenses by specific key names
#                 debit_breakdown = {}
#                 credit_breakdown = {}
                
#                 for transaction in transactions:
#                     try:
#                         amt = float(transaction.get("amount", 0) or 0)
#                         cat = str(transaction.get("category", "")).lower().strip()
#                         exp_type = str(transaction.get("expense", "") or "unspecified").strip().title()
                        
#                         if cat == "debit":
#                             total_debit += amt
#                             debit_breakdown[exp_type] = debit_breakdown.get(exp_type, 0.0) + amt
#                         elif cat == "credit":
#                             total_credit += amt
#                             credit_breakdown[exp_type] = credit_breakdown.get(exp_type, 0.0) + amt
#                     except (ValueError, TypeError):
#                         pass
                
#                 # Metric updates
#                 st.metric(label="Total Money Spent (Debit)", value=f"INR {total_debit:,.2f}")
#                 st.metric(label="Total Money Received (Credit)", value=f"INR {total_credit:,.2f}")
                
#                 # --- NEW SECTION: AGGREGATED SORTED TABLES ---
#                 st.subheader("Category Breakdown Analysis")
                
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.write("Debit (Expenses) Details")
#                     if debit_breakdown:
#                         # Convert to DataFrame, format numbers and sort highest to lowest
#                         df_debit = pd.DataFrame(list(debit_breakdown.items()), columns=["Expense Category", "Total Amount"])
#                         df_debit = df_debit.sort_values(by="Total Amount", ascending=False).reset_index(drop=True)
#                         st.dataframe(df_debit, use_container_width=True)
#                     else:
#                         st.text("No debit transactions registered.")
                        
#                 with col2:
#                     st.write("Credit (Income) Details")
#                     if credit_breakdown:
#                         df_credit = pd.DataFrame(list(credit_breakdown.items()), columns=["Income Category", "Total Amount"])
#                         df_credit = df_credit.sort_values(by="Total Amount", ascending=False).reset_index(drop=True)
#                         st.dataframe(df_credit, use_container_width=True)
#                     else:
#                         st.text("No credit transactions registered.")
#                 # ----------------------------------------------
                
#                 # AI Insights Summary
#                 st.subheader("AI Insights Summary")
#                 summary_input = HumanMessage(content=f"Here is my transaction data: {json.dumps(transactions)}")
#                 ai_summary = model.invoke([summary_prompt, summary_input])
#                 st.write(ai_summary.content)
                
#                 # Unmodified original GET response payload display
#                 st.subheader("Response")
#                 st.json(json_response)
#             else:
#                 st.error(f"Failed to reach ServiceNow: {r_get.status_code}")
#         except Exception as e:
#             st.error(f"Network error occurred: {e}")

 








import json
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import SystemMessage, HumanMessage
import os
import pandas as pd

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct:novita",
    task="text-generation",
    max_new_tokens=512,
    temperature=0.2
)

model = ChatHuggingFace(llm=llm)

system_prompt = SystemMessage(
    content="""
You are an AI Personal Expense Tracker.

Your job is to extract transaction information from the user's sentence.

Return ONLY valid JSON.

Schema:

{
    "category": "",
    "amount": null,
    "currency": "INR",
    "expense": "",
    "account": "",
    "transaction_type": "",
    "title": "",
    "note": ""
 }

Rules:

1. If the user spends money, set "category" to "debit".

2. If the user receives money, set "category" to "credit".

3. "expense" represents the expense category. Choose only one from:
food
fuel
shopping
travel
medical
recharge
other

4. "transaction_type" represents the payment mode. Choose only one from:
cash
online

5. "account" should be one of:
UCOBANK
INDUSIND
CASH

6. "amount" should contain only the numeric value.

7. "currency" should always be "INR" unless another currency is mentioned.

8. "title" should be very short (1-3 words).
Examples:
Coffee
Pizza
Petrol
Recharge
Medicine
Shopping

9. "note" should be a complete English sentence describing the transaction.

10. If any value is not available, return null.

11. Return ONLY valid JSON.

Example 1

Input:
I spent 500 on food by online through my UCO account.

Output:

{
    "category":"debit",
    "amount":500,
    "currency":"INR",
    "expense":"food",
    "account":"UCO",
    "transaction_type":"online",
    "title":"Food",
    "note":"I spent ₹500 on food using my UCO account through online payment."
 }

Example 2

Input:
I bought coffee worth 250 using my UCO account.

Output:

{
    "category":"debit",
    "amount":250,
    "currency":"INR",
    "expense":"food",
    "account":"UCO",
    "transaction_type":"online",
    "title":"coffee",
    "note":"I bought a coffee worth ₹250 using my UCO account." 
}

Example 3

Input:
I received 50000 salary in my INDUSIND account.

Output:

{
    "category":"credit",
    "amount":50000,
    "currency":"INR",
    "expense":null,
    "account":"INDUSIND",
    "transaction_type":null,
    "title":"Salary",
    "note":"I received a salary of ₹50,000 in my INDUSIND account." 
}
"""
)

summary_prompt = SystemMessage(
    content="""You are an AI Financial Analyst. 
Your task is to analyze the provided JSON transaction history and generate a short, professional, and friendly executive summary.

Provide:
1. A brief overview of the spending patterns.
2. Where the user is spending the most (e.g., Food, Shopping).
3. A small actionable tip or insight to improve financial health.

Keep the response strictly under 4-5 sentences and directly address the user."""
)

st.set_page_config(page_title="AI Expense Tracker")

st.title("AI Expense Tracker")

# --- SECTION 1: SAVE TRANSACTION (POST API) ---
st.header("Record Transaction")
user_input = st.text_area(
    "Enter your transaction",
    placeholder="Example: I spent 500 on food by online through my UCO account."
)

if st.button("Save Transaction"):
    messages = [
        system_prompt,
        HumanMessage(content=user_input)
    ]

    with st.spinner("Understanding your transaction..."):
        response = model.invoke(messages)

        try:
            data = json.loads(response.content)

            url = "https://dev294864.service-now.com/api/x_1879157_expens_0/expense_tracker_api/addTransaction"

            r = requests.post(
                url,
                auth=(
                    os.getenv("SN_USERNAME"),
                    os.getenv("SN_PASSWORD")
                ),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json=data,
                timeout=30
            )

            if r.status_code in [200, 201]:
                st.success("transaction recorded successfully")
            else:
                st.error("not")

        except Exception as e:
            st.error("not")
            st.text(response.content)
            st.exception(e)

st.markdown("---")

# --- SECTION 2: FETCH DETAILS (GET API ON MAIN PAGE) ---
st.header("Financial Dashboard")

if st.button("Get Detail Transaction"):
    get_url = "https://dev294864.service-now.com/api/x_1879157_expens_0/expense_tracker_api/getTransactions"
    
    with st.spinner("Fetching historical data from ServiceNow..."):
        try:
            r_get = requests.get(
                get_url,
                auth=(os.getenv("SN_USERNAME"), os.getenv("SN_PASSWORD")),
                headers={"Accept": "application/json"},
                timeout=30
            )
            
            if r_get.status_code == 200:
                json_response = r_get.json()
                transactions = json_response.get("result", {}).get("transactions", [])
                
                total_debit = 0.0
                total_credit = 0.0
                
                debit_breakdown = {}
                credit_breakdown = {}
                
                for transaction in transactions:
                    try:
                        amt = float(transaction.get("amount", 0) or 0)
                        cat = str(transaction.get("category", "")).lower().strip()
                        exp_type = str(transaction.get("expense", "") or "unspecified").strip().title()
                        
                        if cat == "debit":
                            total_debit += amt
                            debit_breakdown[exp_type] = debit_breakdown.get(exp_type, 0.0) + amt
                        elif cat == "credit":
                            total_credit += amt
                            credit_breakdown[exp_type] = credit_breakdown.get(exp_type, 0.0) + amt
                    except (ValueError, TypeError):
                        pass
                
                # Metric updates
                st.metric(label="Total Money Spent (Debit)", value=f"INR {total_debit:,.2f}")
                st.metric(label="Total Money Received (Credit)", value=f"INR {total_credit:,.2f}")
                
                # Category Breakdown Analysis Tables
                st.subheader("Category Breakdown Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("Debit (Expenses) Details")
                    if debit_breakdown:
                        df_debit = pd.DataFrame(list(debit_breakdown.items()), columns=["Expense Category", "Total Amount"])
                        df_debit = df_debit.sort_values(by="Total Amount", ascending=False).reset_index(drop=True)
                        st.dataframe(df_debit, use_container_width=True)
                    else:
                        st.text("No debit transactions registered.")
                        
                with col2:
                    st.write("Credit (Income) Details")
                    if credit_breakdown:
                        df_credit = pd.DataFrame(list(credit_breakdown.items()), columns=["Income Category", "Total Amount"])
                        df_credit = df_credit.sort_values(by="Total Amount", ascending=False).reset_index(drop=True)
                        st.dataframe(df_credit, use_container_width=True)
                    else:
                        st.text("No credit transactions registered.")
                
                # AI Insights Summary
                st.subheader("AI Insights Summary")
                summary_input = HumanMessage(content=f"Here is my transaction data: {json.dumps(transactions)}")
                ai_summary = model.invoke([summary_prompt, summary_input])
                st.write(ai_summary.content)
                
            else:
                st.error(f"Failed to reach ServiceNow: {r_get.status_code}")
        except Exception as e:
            st.error(f"Network error occurred: {e}")