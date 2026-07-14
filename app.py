from langchain_groq import ChatGroq
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Customer360 AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Customer360 AI Assistant")
st.caption("AI-powered unified customer intelligence dashboard")
st.info(
    """
This AI assistant combines CRM, Support, Email, Slack and Product Usage
to generate a unified customer view with actionable insights.
"""
)

# Load data
crm = pd.read_csv("data/crm.csv")
support = pd.read_csv("data/support.csv")
emails = pd.read_csv("data/emails.csv")
slack = pd.read_csv("data/slack.csv")
usage = pd.read_csv("data/usage.csv")



# Sidebar
st.sidebar.header("Customers")
customer = st.sidebar.selectbox(
    "Select Customer",
    crm["customer"].unique()
)

# Customer Info
customer_info = crm[crm["customer"] == customer].iloc[0]

# Filter data for selected customer
support_data = support[support["customer"] == customer]
email_data = emails[emails["customer"] == customer]
slack_data = slack[slack["customer"] == customer]
usage_data = usage[usage["customer"] == customer]

st.subheader("📊 Customer Overview")


# Customer Info
customer_info = crm[crm["customer"] == customer].iloc[0]

# Filter data for selected customer
support_data = support[support["customer"] == customer]
email_data = emails[emails["customer"] == customer]
slack_data = slack[slack["customer"] == customer]
usage_data = usage[usage["customer"] == customer]

# ----------------------------------
# Customer Health Score
# ----------------------------------

health_score = 100

# Open support tickets reduce score
open_tickets = len(support_data[support_data["status"] == "Open"])
health_score -= open_tickets * 20

# Low product usage
if not usage_data.empty:
    active_users = usage_data.iloc[0]["active_users"]

    if active_users < 5:
        health_score -= 30

# Renewal approaching
renewal_date = pd.to_datetime(customer_info["renewal"])
days_left = (renewal_date - pd.Timestamp.today()).days

if days_left < 30:
    health_score -= 20

# Prevent negative values
health_score = max(0, health_score)

# Health label
if health_score >= 80:
    health = "Healthy"

elif health_score >= 60:
    health = "Attention"

else:
    health = "At Risk"

st.subheader("📊 Customer Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    label="🏢 Company",
    value=customer_info["company"]
)
col2.metric(
    label="💳 Plan",
    value=customer_info["plan"]
)

col3.metric(
    label="📅 Renewal",
    value=customer_info["renewal"]
)

col4.metric(
    label="👤 Owner",
    value=customer_info["owner"]
)

col5.metric(
    "💚 Health",
    f"{health_score}%",
    delta="+ Healthy"
)

# ----------------------------------
# Customer Health Score
# ----------------------------------

health_score = 100

# Reduce score if there are open support tickets
if len(support_data[support_data["status"] == "Open"]) > 0:
    health_score -= 20

# Reduce score if active users are low
if usage_data.iloc[0]["active_users"] < 5:
    health_score -= 30

# Reduce score if renewal is within 30 days
renewal_days = (
    pd.to_datetime(customer_info["renewal"]) - pd.Timestamp.today()
).days

if renewal_days < 30:
    health_score -= 20

# Decide health status
if health_score >= 80:
    health = "🟢 Healthy"
elif health_score >= 60:
    health = "🟡 Attention"
else:
    health = "🔴 At Risk"

# Display the health metric
st.metric(
    "Customer Health",
    f"{health_score}%",
    health
)

st.divider()

# ----------------------------------
# Build Customer Context
# ----------------------------------

context = f"""
Customer Name: {customer}

Company: {customer_info['company']}
Plan: {customer_info['plan']}
Renewal Date: {customer_info['renewal']}
Account Owner: {customer_info['owner']}

Support Tickets:
{support_data.to_string(index=False)}

Customer Emails:
{email_data.to_string(index=False)}

Slack Notes:
{slack_data.to_string(index=False)}

Product Usage:
{usage_data.to_string(index=False)}
"""
    

prompt = f"""
You are a Senior Customer Success Manager.

Analyze ONLY the customer information provided below.

Rules:
- Use ONLY the provided information.
- Do NOT assume or invent facts.
- If information is missing, say it is unavailable.
- Treat Slack notes as internal team notes.
- If product usage is healthy, do not describe it as low usage.

Customer Information:

{context}

Return Markdown with exactly these sections:

# 📋 Customer Summary

# ⚠ Risks

# 🚀 Opportunities

# 🎯 Next Best Action
"""



left, right = st.columns(2)

with left:

    with st.expander("🎫 Support Tickets", expanded=True):
        st.dataframe(
            support_data,
            use_container_width=True,
            hide_index=True
        )

    with st.expander("📧 Customer Emails"):
        st.dataframe(
            email_data,
            use_container_width=True,
            hide_index=True
        )

with right:

    with st.expander("💬 Slack Notes", expanded=True):
        st.dataframe(
            slack_data,
            use_container_width=True,
            hide_index=True
        )

    with st.expander("📈 Product Usage"):
        st.dataframe(
            usage_data,
            use_container_width=True,
            hide_index=True
        )

# ----------------------------------
# AI Chat Assistant
# ----------------------------------

st.divider()

st.subheader("💬 Ask AI About This Customer")

question = st.chat_input(
    "Ask anything about this customer..."
)

if question:

    chat_prompt = f"""
You are a Customer Success AI Assistant.

Use ONLY the customer information below.

Rules:
- Never invent facts.
- Never assume customer sentiment or churn.
- Do not infer inactivity unless explicitly stated.
- If information is unavailable, say "Not available in the provided customer data."
- Base every answer only on the supplied data.

Customer Information:

{context}

User Question:

{question}

Provide a concise and professional answer.
"""

    with st.spinner("Thinking..."):
        answer = llm.invoke(chat_prompt).content

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        st.write(answer)

st.divider()

st.caption(
    "Built for the Volopay Growth Squad Assessment • Streamlit • Ollama • LangChain"
)