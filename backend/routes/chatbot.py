from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from typing import List, Optional
import random

router = APIRouter(tags=["Chatbot"])

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[int] = None

RESPONSES = {
    "loan": [
        "Finex offers personal loans from ₹10,000 to ₹50 lakhs at competitive rates starting from 10.5% p.a. Your eligibility is based on credit score, income, and account history. Would you like me to check your pre-approved loan offers?",
        "Our loan products include: Personal Loans (up to ₹50L), Home Loans (up to ₹2Cr), and Business Loans (up to ₹1Cr). Interest rates start at 10.5% p.a. with flexible repayment of 1-20 years."
    ],
    "invest": [
        "Based on current market trends, consider diversifying across: Large Cap (40%) - HDFC, TCS, Reliance; Mid Cap (35%) - stable growth stocks; Debt (25%) - government bonds for safety. Always invest based on your risk appetite!",
        "Top investment opportunities right now: NIFTY 50 Index Funds (low risk), Tech sector ETFs (moderate risk), and blue-chip stocks like INFY, WIPRO for steady returns. Want a personalized recommendation?"
    ],
    "fraud": [
        "Finex uses AI-powered fraud detection that monitors: unusual login locations, suspicious transaction patterns, and large unexpected transfers. We block fraudulent transactions in real-time and alert you immediately via SMS and email.",
        "Your account is protected by: 256-bit SSL encryption, 2-factor authentication, biometric verification, and real-time transaction monitoring. Any suspicious activity triggers immediate account freeze and alerts."
    ],
    "stock": [
        "Top performing stocks today: NVDA (+3.4%), AAPL (+1.2%), MSFT (+0.6%). For Indian markets: RELIANCE, TCS, HDFC are showing strong momentum. Click on Markets to see live prices and trade!",
        "Stock recommendation: For long-term growth, consider AAPL, MSFT, GOOGL. For high risk/reward: TSLA, NVDA. For Indian market: TCS, INFY, RELIANCE. Always do your own research!"
    ],
    "portfolio": [
        "Your portfolio health tips: 1) Diversify across sectors, 2) Don't put more than 10% in one stock, 3) Keep 20-30% in safe assets like bonds/FDs, 4) Rebalance quarterly. Check your Portfolio page for detailed analysis!",
        "To improve portfolio performance: Set stop-loss orders, track P&L regularly, and consider rupee-cost averaging for volatile stocks. Your Portfolio section shows detailed analytics!"
    ],
    "market": [
        "Today's market snapshot: US markets showing mixed signals. NASDAQ leading gains. Indian markets: NIFTY holding above 21,500 resistance. Key sectors to watch: IT, Banking, Pharma. Check the Markets page for live data!",
        "Market outlook: Tech stocks remain strong globally. Indian rupee stable. FII inflows positive. Key events this week: Fed meeting, RBI policy review. Stay updated on the Markets page!"
    ],
    "greeting": [
        "Hello! I'm your Finex AI Financial Assistant. I can help you with:\n• Stock recommendations\n• Loan eligibility\n• Portfolio analysis\n• Fraud protection\n• Market insights\n\nWhat would you like to know?",
        "Hi there! Welcome to Finex AI Assistant. Ask me anything about investments, loans, market trends, or your account. I'm here to help!"
    ],
    "transaction": [
        "To make a transaction: Go to Markets → Select a stock → Enter quantity → Choose BUY or SELL → Confirm order. Your transaction history is available in the Transactions section.",
        "Transaction help: For deposits, go to Add Funds. For stock trades, use the Markets page. For transfers, use Cards section. All transactions are secured with bank-grade encryption."
    ],
    "default": [
        "I can help you with investment advice, loan queries, fraud detection, stock recommendations, and market analysis. What specific information are you looking for?",
        "Great question! As your AI financial advisor, I specialize in portfolio management, stock recommendations, loan advisory, and market insights. Could you be more specific about what you need?",
        "I'm here to assist with all your financial needs. Try asking about: stock picks, loan eligibility, portfolio review, or market trends!"
    ]
}

def get_intent(msg: str) -> str:
    msg = msg.lower()
    if any(w in msg for w in ["loan", "borrow", "credit", "emi", "lend"]):
        return "loan"
    if any(w in msg for w in ["invest", "recommend", "buy", "which stock", "suggest", "tip"]):
        return "invest"
    if any(w in msg for w in ["fraud", "safe", "secure", "hack", "protect", "scam"]):
        return "fraud"
    if any(w in msg for w in ["stock", "share", "nifty", "sensex", "market", "price", "nasdaq"]):
        return "stock" if "market" not in msg else "market"
    if any(w in msg for w in ["portfolio", "holding", "p&l", "profit", "loss", "performance"]):
        return "portfolio"
    if any(w in msg for w in ["market", "index", "trend", "today", "outlook"]):
        return "market"
    if any(w in msg for w in ["hi", "hello", "hey", "start", "help", "what can"]):
        return "greeting"
    if any(w in msg for w in ["transaction", "transfer", "send", "pay", "deposit"]):
        return "transaction"
    return "default"

@router.post("/ask")
async def ask_chatbot(msg: ChatMessage, db: Session = Depends(get_db)):
    intent = get_intent(msg.message)
    response = random.choice(RESPONSES[intent])
    return {"response": response, "intent": intent}

@router.get("/suggestions")
async def get_suggestions():
    return {"suggestions": [
        "What stocks should I buy today?",
        "Check my loan eligibility",
        "How is the market trending?",
        "Explain fraud protection",
        "Review my portfolio",
        "Best investment strategy"
    ]}
