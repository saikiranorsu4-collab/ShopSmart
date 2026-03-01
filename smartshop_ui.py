import streamlit as st
import json
import os
from datetime import datetime
import plotly.express as px
import pandas as pd

DATA_FILE = "purchases.json"

# ---------- Helper Functions ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- Streamlit UI Config ----------
st.set_page_config(page_title="ShopSmart - Purchase Manager", page_icon="🛍️", layout="wide")
st.markdown(
    """
    <style>
    .main {
        background-color:"#F0F0F0";
    }
    div.block-container{
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stMetric {
        background-color: #fff;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🛒 ShopSmart - Smart Purchase Optimizer")

menu = [
    "View Purchases",
    "Add Purchase",
    "Update Purchase",
    "Delete Purchase",
    "Total Summary"
]
choice = st.sidebar.selectbox("📂 Menu", menu)

data = load_data()

# Convert data to DataFrame for analysis
df = pd.DataFrame(data)

# ---------- View Purchases ----------
if choice == "View Purchases":
    st.subheader("📋 All Purchases")

    if not df.empty:
        # Category Filter
        categories = ["All"] + sorted(df["category"].unique())
        selected_category = st.selectbox("🔎 Filter by Category", categories)

        if selected_category != "All":
            df = df[df["category"] == selected_category]

        # Search by name
        search_term = st.text_input("🔍 Search by Name or Keyword")
        if search_term:
            df = df[df["name"].str.contains(search_term, case=False, na=False)]

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No purchases found yet!")

# ---------- Add Purchase ----------
elif choice == "Add Purchase":
    st.subheader("➕ Add a New Purchase")

    name = st.text_input("Purchase Name")
    amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01)
    category = st.text_input("Category")
    date = st.date_input("Date", datetime.now())

    if st.button("💾 Save Purchase"):
        new_purchase = {
            "id": len(data) + 1,
            "name": name,
            "amount": amount,
            "category": category,
            "date": str(date)
        }
        data.append(new_purchase)
        save_data(data)
        st.success(f"✅ '{name}' added successfully!")

# ---------- Update Purchase ----------
elif choice == "Update Purchase":
    st.subheader("✏️ Update a Purchase")

    if data:
        ids = [p["id"] for p in data]
        pid = st.selectbox("Select Purchase ID", ids)

        purchase = next((p for p in data if p["id"] == pid), None)
        if purchase:
            name = st.text_input("Purchase Name", purchase["name"])
            amount = st.number_input("Amount", value=purchase["amount"], step=0.01)
            category = st.text_input("Category", purchase["category"])
            date = st.date_input("Date", datetime.strptime(purchase["date"], "%Y-%m-%d"))

            if st.button("💾 Update Purchase"):
                purchase.update({
                    "name": name,
                    "amount": amount,
                    "category": category,
                    "date": str(date)
                })
                save_data(data)
                st.success("✅ Purchase updated successfully!")
    else:
        st.warning("No purchases available to update.")

# ---------- Delete Purchase ----------
elif choice == "Delete Purchase":
    st.subheader("❌ Delete a Purchase")

    if data:
        ids = [p["id"] for p in data]
        pid = st.selectbox("Select Purchase ID to delete", ids)

        if st.button("🗑️ Delete"):
            # Remove the selected purchase
            data = [p for p in data if p["id"] != pid]

            # Reorder remaining IDs sequentially (1, 2, 3, ...)
            for i, p in enumerate(data, start=1):
                p["id"] = i

            # Save updated data
            save_data(data)

            st.success(f"🗑️ Purchase ID {pid} deleted successfully!")
            st.info("✅ IDs have been reordered sequentially.")
    else:
        st.warning("No purchases available to delete.")


# ---------- Total Summary ----------
elif choice == "Total Summary":
    st.subheader("📊 Spending Summary Dashboard")

    if not df.empty:
        # Handle both formats (CLI + Streamlit)
        df["amount"] = df.apply(
            lambda p: p.get("amount") if "amount" in p else p.get("price", 0) * p.get("quantity", 1),
            axis=1
        )

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["month"] = df["date"].dt.strftime("%B %Y")

        total_spent = df["amount"].sum()
        category_summary = df.groupby("category")["amount"].sum().reset_index()
        monthly_summary = df.groupby("month")["amount"].sum().reset_index()

        # Top summary metrics
        col1, col2 = st.columns(2)
        col1.metric("💵 Total Spent", f"₹{total_spent:.2f}")
        col2.metric("📦 Total Purchases", len(df))

        # Category Breakdown
        st.markdown("### 💠 Category-wise Breakdown")
        st.table(category_summary)

        pie_fig = px.pie(
            category_summary,
            names="category",
            values="amount",
            title="Category Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        st.plotly_chart(pie_fig, use_container_width=True)

        # Monthly Trend
        st.markdown("### 📅 Monthly Spending Trend")
        bar_fig = px.bar(
            monthly_summary,
            x="month",
            y="amount",
            text="amount",
            title="Monthly Spending Overview",
            color="amount",
            color_continuous_scale="Blues"
        )
        bar_fig.update_traces(texttemplate='₹%{text:.2f}', textposition='outside')
        st.plotly_chart(bar_fig, use_container_width=True)

    else:
        st.info("No data available for summary yet!")
