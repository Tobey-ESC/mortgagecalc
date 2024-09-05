import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
import plotly.graph_objects as go

st.title("Mortgage REpayments Calculator")

st.write("### Input Data")
col1, col2 = st.columns(2)
home_value = col1.number_input("Home Value", min_value=0, value=500000)
deposit = col1.number_input("Deposit", min_value=0, value=100000)
interest_rate = col2.number_input(
    "Interest Rate (in %)", min_value=0.0, value=5.5)
loan_term = col2.number_input("Loan Term (in years)", min_value=1, value=30)

# calc loan amount

loan_amount = home_value - deposit

# Calculate number of payments
number_of_payments = loan_term * 12

# Calculate monthly interest rate
monthly_interest_rate = (interest_rate / 100) / 12


# different paymnet frequencies

# Payment frequency options
st.write("### Payment Frequency Options")
payment_frequency = st.selectbox("Select Payment Frequency", ["Monthly", "Bi-Weekly", "Weekly"])

if payment_frequency == "Bi-Weekly":
    number_of_payments = loan_term * 26
    monthly_interest_rate /= 2  # Adjust the interest rate for bi-weekly payments
elif payment_frequency == "Weekly":
    number_of_payments = loan_term * 52
    monthly_interest_rate /= 4  # Adjust the interest rate for weekly payments
else:
    number_of_payments = loan_term * 12  # Default to monthly


# calculate the repayments

def calculate_repayments(loan_amount, monthly_interest_rate, number_of_payments):
    if loan_amount == 0 or number_of_payments == 0: 
        return 0, 0, 0
    if monthly_interest_rate == 0:
        monthly_payment = loan_amount / number_of_payments
        total_payments = monthly_payment * number_of_payments
        total_interest = 0
    else:
        monthly_payment = (
            loan_amount
            * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
            / ((1 + monthly_interest_rate) ** number_of_payments - 1)
        )
        total_payments = monthly_payment * number_of_payments
        total_interest = total_payments - loan_amount
    return monthly_payment, total_payments, total_interest


# display repayments

monthly_payment, total_payments, total_interest = calculate_repayments(
    home_value - deposit, (interest_rate / 100) / 12, loan_term * 12
)

st.write("### Repayments")
col1, col2, col3 = st.columns(3)
col1.metric(label="Monthly Repayments", value=f"₱{monthly_payment:,.2f}")
col2.metric(label="Total Repayments", value=f"₱{total_payments:,.0f}")
col3.metric(label="Total Interest", value=f"₱{total_interest:,.0f}")


# create a data-frame with the paymen schedule

schedule = []
remaining_balance = loan_amount

for i in range(1, number_of_payments + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment
    year = math.ceil(i / 12) # calc the year into loan
    schedule.append(
        [
            i,
            monthly_payment,
            principal_payment,
            interest_payment,
            remaining_balance,
            year,
        ]
    )

df = pd.DataFrame(
    schedule,
    columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance", "Year"],
)

# Amortization schedule download
st.write("### Amortization Schedule")
if st.button("Download Amortization Schedule"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="amortization_schedule.csv",
        mime="text/csv"
    )


# Prepayment calculator
st.write("### Prepayment Calculator")
prepayment = st.number_input("Prepayment Amount (optional)", min_value=0, value=0)

def calculate_with_prepayment(loan_amount, monthly_interest_rate, number_of_payments, prepayment):
    if monthly_interest_rate == 0:
        return 0, 0, 0

    monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / ((1 + monthly_interest_rate) ** number_of_payments - 1)
    total_interest = 0
    for month in range(1, number_of_payments + 1):
        interest_payment = loan_amount * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment + prepayment
        loan_amount -= principal_payment
        total_interest += interest_payment
        if loan_amount <= 0:
            return month, total_interest, principal_payment

    return number_of_payments, total_interest, monthly_payment

months_to_repay, total_interest_with_prepayment, _ = calculate_with_prepayment(
    loan_amount, monthly_interest_rate, number_of_payments, prepayment
)

st.write(f"Loan will be repaid in {months_to_repay} months with total interest of ₱{total_interest_with_prepayment:,.0f}.")


# display the data-frame as a chart
st.write("### Payment Schedule")
payments_df = df [["Year", "Remaining Balance"]].groupby("Year").min()
st.line_chart(payments_df)

chart_data = pd.DataFrame(
    np.random.randn(20, 6), columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance", "Year"]
)


# Create an interactive chart for loan repayment breakdown
fig = go.Figure()

# Add principal and interest traces
fig.add_trace(go.Scatter(x=df['Month'], y=df['Principal'], mode='lines', name='Principal'))
fig.add_trace(go.Scatter(x=df['Month'], y=df['Interest'], mode='lines', name='Interest'))

# Customize layout
fig.update_layout(
    title="Loan Repayment Breakdown",
    xaxis_title="Months",
    yaxis_title="Amount",
    legend_title="Components"
)

st.plotly_chart(fig)

st.scatter_chart(
    chart_data,
    x="Month",
    y=["Payment", "Principal"],
    size="Interest",
    color=["#FF0000", "#0000FF"], #optional

)


# Mortgage FAQs section
st.write("### Mortgage FAQs")
st.write("""
- **What is a mortgage?** \n\n    A mortgage is a loan used to purchase property, typically repaid over a long period (e.g., 30 years).
- **What is the difference between fixed and variable interest rates?** \n\n     Fixed rates stay the same, while variable rates can change.
- **What is an amortization schedule?** \n\n     It’s a table showing how much of each loan payment goes toward principal and interest over time.
""")

# Tips and advice section
st.write("### Mortgage Tips and Advice")
st.write("""
- **Improve Your Credit Score:** Make sure to pay bills on time and keep balances low on credit cards to improve your credit score.
- **Shop Around for the Best Rates:** Compare rates from different lenders to get the best deal on your mortgage.
- **Consider Prepayments:** Making extra payments can reduce your total interest paid and shorten your loan term.
- **Understand the Fees:** Ensure you're aware of any additional fees or closing costs when taking out a mortgage.
""")
