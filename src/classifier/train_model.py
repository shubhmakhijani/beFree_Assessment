import os
import re
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


def clean_banking_narration(text: str) -> str:
    """
    Cleans banking narration strings by stripping noise:
    - Removes transaction reference numbers (e.g., UPI/402910283/ -> upi)
    - Removes hex strings, dates, and non-alphanumeric clutter
    - Keeps core semantic words and brand names
    """
    if not text:
        return ""
    text = text.lower()
    # Normalize common banking prefixes
    text = re.sub(r"\b(upi|neft|rtgs|imps|pos|ach|cms|inf|inb|mb|atm)\b", " ", text)
    # Strip long numeric or alphanumeric reference strings (like 12-digit UTRs)
    text = re.sub(r"\b[a-z0-9]{8,}\b", " ", text)
    text = re.sub(r"\b\d+\b", " ", text)
    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_training_dataset():
    """
    Constructs a rich, realistic training dataset representing standard
    Indian and international bank statement transaction narratives.
    """
    data = [
        # Salary & Income
        ("SALARY CREDITED FOR THE MONTH OF OCTOBER", "Salary & Income"),
        ("MONTHLY PAYROLL DIRECT DEPOSIT ACME CORP", "Salary & Income"),
        ("STIPEND PAYMENT INTERNSHIP BEFREE", "Salary & Income"),
        ("ACH CREDIT SALARY INFOSYS TECHNOLOGIES", "Salary & Income"),
        ("WAGES PAYMENT TRANSFER OCT 2024", "Salary & Income"),
        ("DIVIDEND RECEIVED TCS LTD", "Salary & Income"),
        ("ANNUAL BONUS DISBURSEMENT", "Salary & Income"),
        ("INTEREST CREDIT SAVINGS ACCOUNT", "Salary & Income"),
        ("INTEREST PAID CAPITAL GAINS", "Salary & Income"),
        ("REFUND FOR CANCELLED ORDER", "Salary & Income"),
        ("CASHBACK REWARD DEPOSIT", "Salary & Income"),

        # Food & Dining
        ("UPI 4281920 SWIGGY BANGALORE IN", "Food & Dining"),
        ("UPI 3910283 ZOMATO GURGAON ORDER", "Food & Dining"),
        ("DOMINOS PIZZA ONLINE PAYMENT", "Food & Dining"),
        ("STARBUCKS COFFEE KORAMANGALA", "Food & Dining"),
        ("MCDONALDS FAMILY RESTAURANT", "Food & Dining"),
        ("BURGER KING AIRPORT OUTLET", "Food & Dining"),
        ("KFC CHICKEN MEAL PURCHASE", "Food & Dining"),
        ("BARBEQUE NATION DINNER BUFFET", "Food & Dining"),
        ("SUBWAY SANDWICHES MALL", "Food & Dining"),
        ("CHAAYOS CHAI SNACKS", "Food & Dining"),
        ("CHAI POINT TEA REFRESHMENTS", "Food & Dining"),
        ("THE OBEROI RESTAURANT LUNCH", "Food & Dining"),
        ("LOCAL BAKERY CAKE ORDER", "Food & Dining"),
        ("PUNJABI DHABA HIGHWAY MEAL", "Food & Dining"),

        # Groceries & Supermarket
        ("BLINKIT 10 MINUTE DELIVERY GROCERIES", "Groceries & Supermarket"),
        ("ZEPTO QUICK COMMERCE ESSENTIALS", "Groceries & Supermarket"),
        ("BIGBASKET SUPERMARKET ORDER", "Groceries & Supermarket"),
        ("DMART RETAIL GROCERIES PURCHASE", "Groceries & Supermarket"),
        ("RELIANCE FRESH VEGETABLES AND FRUITS", "Groceries & Supermarket"),
        ("SPENCERS RETAIL SUPERMARKET", "Groceries & Supermarket"),
        ("NATURES BASKET ORGANIC FOOD", "Groceries & Supermarket"),
        ("LOCAL KIRANA STORE MILK BREAD", "Groceries & Supermarket"),
        ("COUNTRY DELIGHT DAILY MILK DELIVERY", "Groceries & Supermarket"),
        ("BB DAILY MORNING SUPPLIES", "Groceries & Supermarket"),
        ("MORE RETAIL PROVISION STORE", "Groceries & Supermarket"),

        # Shopping & E-Commerce
        ("AMAZON INDIA PAYMENTS RETAIL", "Shopping & E-Commerce"),
        ("FLIPKART INTERNET PVT LTD PURCHASE", "Shopping & E-Commerce"),
        ("MYNTRA DESIGNS CLOTHING ORDER", "Shopping & E-Commerce"),
        ("MEESHO ONLINE SHOPPING STORE", "Shopping & E-Commerce"),
        ("AJIO APPAREL TRENDS ONLINE", "Shopping & E-Commerce"),
        ("NYKAA E-RETAIL COSMETICS", "Shopping & E-Commerce"),
        ("TATA CLIQ ELECTRONICS PURCHASE", "Shopping & E-Commerce"),
        ("ZARA FASHION STORE PURCHASE", "Shopping & E-Commerce"),
        ("H&M CLOTHING RETAIL OUTLET", "Shopping & E-Commerce"),
        ("DECATHLON SPORTS GOODS INDIA", "Shopping & E-Commerce"),
        ("UNIQLO CLOTHING STORE", "Shopping & E-Commerce"),
        ("SHOPPERS STOP DEPARTMENTAL STORE", "Shopping & E-Commerce"),
        ("LIFESTYLE INTERNATIONAL RETAIL", "Shopping & E-Commerce"),

        # Utilities & Bills
        ("BESCOM ELECTRICITY BILL PAYMENT", "Utilities & Bills"),
        ("TNEB POWER BILL ONLINE CHENNAI", "Utilities & Bills"),
        ("UPPCL ELECTRICITY CONSUMPTION CHARGES", "Utilities & Bills"),
        ("MUNICIPAL WATER SUPPLY BILL", "Utilities & Bills"),
        ("INDANE LPG GAS CYLINDER REFILL", "Utilities & Bills"),
        ("BHARAT GAS REFILL BOOKING", "Utilities & Bills"),
        ("HP GAS CYLINDER ONLINE BOOKING", "Utilities & Bills"),
        ("AIRTEL PREPAID RECHARGE MOBILE", "Utilities & Bills"),
        ("JIO POSTPAID MOBILE BILL PAYMENT", "Utilities & Bills"),
        ("VODAFONE IDEA RECHARGE BILLPAY", "Utilities & Bills"),
        ("ACT FIBERNET BROADBAND MONTHLY BILL", "Utilities & Bills"),
        ("TATA PLAY DTH RECHARGE", "Utilities & Bills"),
        ("APARTMENT MAINTENANCE SOCIETY FEES", "Utilities & Bills"),

        # Travel & Commute
        ("UBER INDIA RIDES TRIP CHARGES", "Travel & Commute"),
        ("OLA CABS RIDE FARE PAYMENT", "Travel & Commute"),
        ("RAPIDO BIKE TAXI COMMUTE", "Travel & Commute"),
        ("IRCTC TRAIN TICKET BOOKING NEW DELHI", "Travel & Commute"),
        ("REDBUS INTERCITY BUS TICKET", "Travel & Commute"),
        ("MAKEMYTRIP FLIGHT BOOKING MUMBAI", "Travel & Commute"),
        ("GOIBIBO HOTEL AND TRAVEL BOOKING", "Travel & Commute"),
        ("INDIGO AIRLINES FLIGHT TICKETS", "Travel & Commute"),
        ("AIR INDIA DOMESTIC FLIGHT", "Travel & Commute"),
        ("HPCL PETROL PUMP FUEL REFILL", "Travel & Commute"),
        ("BPCL DIESEL FUEL STATION", "Travel & Commute"),
        ("INDIAN OIL PETROL FUEL FILL", "Travel & Commute"),
        ("SHELL FUEL OUTLET HIGHWAY", "Travel & Commute"),
        ("FASTAG RECHARGE HIGHWAY TOLL", "Travel & Commute"),
        ("METRO SMART CARD RECHARGE COMMUTE", "Travel & Commute"),

        # Investments & Wealth
        ("ZERODHA BROKING LTD FUNDS TRANSFER", "Investments & Wealth"),
        ("GROWW MUTUAL FUNDS SIP INVESTMENT", "Investments & Wealth"),
        ("UPSTOX SECURITIES TRADING ACCOUNT", "Investments & Wealth"),
        ("ANGEL ONE SHARE TRADING MARGIN", "Investments & Wealth"),
        ("SBI MUTUAL FUND MONTHLY SIP", "Investments & Wealth"),
        ("HDFC PRUDENTIAL ASSET MANAGEMENT", "Investments & Wealth"),
        ("CAMSONLINE MUTUAL FUND DIRECT", "Investments & Wealth"),
        ("KFINTECH INVESTMENT SERVICES", "Investments & Wealth"),
        ("NATIONAL PENSION SYSTEM NPS CONTRIBUTION", "Investments & Wealth"),
        ("PUBLIC PROVIDENT FUND PPF DEPOSIT", "Investments & Wealth"),
        ("DIGITAL GOLD SOVEREIGN BOND PURCHASE", "Investments & Wealth"),

        # Loans & EMI
        ("BAJAJ FINANCE LIMITED EMI DEDUCTION", "Loans & EMI"),
        ("HDFC BANK HOME LOAN MONTHLY EMI", "Loans & EMI"),
        ("SBI CAR LOAN INSTALMENT DEBIT", "Loans & EMI"),
        ("PERSONAL LOAN AUTO DEBIT ACH", "Loans & EMI"),
        ("CRED CREDIT CARD BILL PAYMENT", "Loans & EMI"),
        ("HDFC CREDIT CARD STATEMENT PAYMENT", "Loans & EMI"),
        ("ICICI CREDIT CARD OUTSTANDING DUES", "Loans & EMI"),
        ("CONSUMER DURABLE LOAN EMI", "Loans & EMI"),

        # Bank Charges & Taxes
        ("QUARTERLY SMS ALERT CHARGES", "Bank Charges & Taxes"),
        ("CONSOLIDATED CHARGES FOR MINIMUM BALANCE", "Bank Charges & Taxes"),
        ("ANNUAL DEBIT CARD MAINTENANCE FEE", "Bank Charges & Taxes"),
        ("GOODS AND SERVICES TAX GST LEVIED", "Bank Charges & Taxes"),
        ("CHEQUE RETURN CHARGES PENALTY", "Bank Charges & Taxes"),
        ("ATM INTERCHANGE USAGE FEES", "Bank Charges & Taxes"),
        ("ACCOUNT SERVICE CHARGES DEDUCTION", "Bank Charges & Taxes"),

        # Entertainment & Subscriptions
        ("NETFLIX MONTHLY SUBSCRIPTION PLAN", "Entertainment & Subscriptions"),
        ("SPOTIFY PREMIUM MUSIC STREAMING", "Entertainment & Subscriptions"),
        ("AMAZON PRIME ANNUAL MEMBERSHIP", "Entertainment & Subscriptions"),
        ("DISNEY HOTSTAR ANNUAL SUBSCRIPTION", "Entertainment & Subscriptions"),
        ("YOUTUBE PREMIUM FAMILY MEMBERSHIP", "Entertainment & Subscriptions"),
        ("BOOKMYSHOW MOVIE TICKETS CINEMA", "Entertainment & Subscriptions"),
        ("PVR CINEMAS MULTIPLEX TICKETS", "Entertainment & Subscriptions"),
        ("INOX LEISURE MOVIE SEATS", "Entertainment & Subscriptions"),
        ("APPLE COM BILL ICLOUD STORAGE", "Entertainment & Subscriptions"),
        ("GOOGLE PLAY SUBSCRIPTION SERVICES", "Entertainment & Subscriptions"),

        # Healthcare & Medical
        ("APOLLO PHARMACY MEDICINES PURCHASE", "Healthcare & Medical"),
        ("MEDPLUS HEALTHCARE DRUGS RETAIL", "Healthcare & Medical"),
        ("TATA 1MG HEALTHCARE WELLNESS", "Healthcare & Medical"),
        ("NETMEDS ONLINE PHARMACY ORDER", "Healthcare & Medical"),
        ("MAX HEALTHCARE HOSPITAL CONSULTATION", "Healthcare & Medical"),
        ("FORTIS HOSPITAL OPD DOCTOR FEES", "Healthcare & Medical"),
        ("DR LAL PATHLABS BLOOD DIAGNOSTIC TEST", "Healthcare & Medical"),
        ("CLINIC DOCTOR CONSULTATION APPOINTMENT", "Healthcare & Medical"),

        # Education & Fees
        ("DELHI PUBLIC SCHOOL QUARTERLY FEES", "Education & Fees"),
        ("COLLEGE SEMESTER TUITION FEES", "Education & Fees"),
        ("UDEMY ONLINE COURSE CERTIFICATION", "Education & Fees"),
        ("COURSERA ANNUAL LEARNING SUBSCRIPTION", "Education & Fees"),
        ("ALLEN CAREER INSTITUTE COACHING FEES", "Education & Fees"),
        ("UNIVERSITY EXAM REGISTRATION CHARGES", "Education & Fees"),

        # Transfers & Personal
        ("UPI PAYMENT SENT TO FRIEND RAMESH", "Transfers & Personal"),
        ("IMPS TRANSFER TO SISTER ACCOUNT", "Transfers & Personal"),
        ("NEFT TRANSFER RAHUL SHARMA", "Transfers & Personal"),
        ("RTGS INTERBANK FUNDS TRANSFER", "Transfers & Personal"),
        ("FUNDS TRANSFER TO SELF SAVINGS ACCOUNT", "Transfers & Personal"),
        ("UPI PAYMENT TO LOCAL VENDOR", "Transfers & Personal"),
        ("RECEIVED FUNDS FROM ANITA VERMA", "Transfers & Personal")
    ]

    # Data augmentation: multiply with synthetic banking variations (prefixes, suffixes, noise)
    augmented_data = []
    prefixes = [
        "UPI/", "NEFT-", "IMPS/P2P/", "POS 402910 ", "ACH DR-", "CMS/2024/", 
        "INF-", "MB/", "EFT/", "DEBIT CARD PURCHASE AT "
    ]
    suffixes = [
        " REF 9028102918", " UTR 00192837192", " BANGALORE", " MUMBAI", 
        " DELHI", " TXN ID 9928172", " ON 15-OCT-2024", ""
    ]

    for desc, cat in data:
        augmented_data.append((desc, cat))
        for p in prefixes[:3]:
            augmented_data.append((f"{p}{desc}", cat))
        for s in suffixes[:2]:
            augmented_data.append((f"{desc}{s}", cat))

    df = pd.DataFrame(augmented_data, columns=["description", "category"])
    return df


def train_and_save_model(output_path="models/transaction_classifier.joblib"):
    """
    Trains the TF-IDF + Logistic Regression pipeline and persists the artifact.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = build_training_dataset()

    X = df["description"].apply(clean_banking_narration)
    y = df["category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3500, sublinear_tf=True)),
        ("classifier", LogisticRegression(C=2.0, max_iter=1000, class_weight="balanced"))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Training Complete! Test Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, y_pred))

    joblib.dump(pipeline, output_path)
    print(f"Model successfully saved to {output_path}")


if __name__ == "__main__":
    train_and_save_model()
