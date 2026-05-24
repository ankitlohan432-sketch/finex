"""
AI Chatbot Service
Handles all chatbot logic - separate service file
"""

import random
from datetime import datetime

class AIService:
    """AI-powered chatbot for stock recommendations and guidance"""
    
    def __init__(self):
        self.conversation_history = []
        
    async def chat(self, message: str, user_name: str = "Investor"):
        """
        Main chat handler - routes messages to appropriate handlers
        """
        user_msg = message.lower().strip()
        self.conversation_history.append({"role": "user", "message": message})
        
        # Route to handlers
        if self.is_greeting(user_msg):
            response = self.greet_user(user_name)
        elif self.is_toppers_request(user_msg):
            response = self.get_top_stocks_response(user_msg)
        elif self.is_recommendation_request(user_msg):
            response = self.get_recommendations()
        elif self.is_loan_request(user_msg):
            response = self.get_loan_info()
        elif self.is_portfolio_request(user_msg):
            response = self.get_portfolio_guide()
        elif self.is_fraud_request(user_msg):
            response = self.get_fraud_protection_info()
        elif self.is_navigation_request(user_msg):
            response = self.get_site_navigation(user_msg)
        else:
            response = self.get_default_response(user_msg)
            
        self.conversation_history.append({"role": "bot", "message": response})
        return response
    
    def is_greeting(self, msg: str) -> bool:
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon']
        return any(g in msg for g in greetings)
    
    def greet_user(self, name: str) -> str:
        hour = datetime.now().hour
        time_greet = "Good afternoon"
        if hour < 12:
            time_greet = "Good morning"
        elif hour > 17:
            time_greet = "Good evening"
        
        return f"""{time_greet} {name.split()[0]}! 👋

**What can I help you with?**
📈 "Show gainers" - Top performing stocks
📉 "Show losers" - Worst performing stocks  
💡 "Recommend stocks" - Get recommendations
💰 "Loan info" - Personal loans & credit
💳 "Card security" - Fraud protection
📊 "Portfolio" - Your holdings
🧭 "Tour" - Site navigation
💬 Just chat - Ask anything!"""

    def is_toppers_request(self, msg: str) -> bool:
        keywords = ['gainers', 'losers', 'top movers', 'rising', 'falling', 'movers', 'trending']
        return any(k in msg for k in keywords)
    
    def get_top_stocks_response(self, msg: str) -> str:
        is_gainers = 'gain' in msg or 'up' in msg or 'rising' in msg
        
        if is_gainers:
            return """📈 **TOP 5 GAINERS TODAY** 🚀

1. **TSLA** (Tesla) - $245.80 | ↑ +5.2%
2. **NVDA** (NVIDIA) - $875.45 | ↑ +4.1%
3. **AMZN** (Amazon) - $178.90 | ↑ +3.8%
4. **MSFT** (Microsoft) - $380.25 | ↑ +2.5%
5. **GOOGL** (Alphabet) - $140.50 | ↑ +1.9%

💡 These stocks show strong momentum!
🎯 Type "Buy TSLA" to purchase
💬 Ask for more analysis"""
        else:
            return """📉 **TOP 5 LOSERS TODAY** 💔

1. **META** (Meta) - $502.30 | ↓ -6.2%
2. **ORCL** (Oracle) - $132.80 | ↓ -4.1%
3. **IBM** (IBM) - $175.20 | ↓ -3.5%
4. **INTC** (Intel) - $29.45 | ↓ -2.8%
5. **AMD** (Advanced Micro) - $168.90 | ↓ -2.3%

⚠️ These show downward pressure
💡 Sometimes dips are buying opportunities
🎯 Be careful if you're a beginner"""

    def is_recommendation_request(self, msg: str) -> bool:
        keywords = ['recommend', 'suggest', 'which stock', 'what to buy', 'investment']
        return any(k in msg for k in keywords)
    
    def get_recommendations(self) -> str:
        return """🎯 **PERSONALIZED STOCK RECOMMENDATIONS**

**🟢 STRONG BUY** (High Confidence)
• TSLA - Strong uptrend, +5.2%
• NVDA - Tech momentum, +4.1%
• AMZN - Stable growth, +3.8%

**🟡 MODERATE BUY** (Medium Confidence)
• MSFT - Blue-chip, stable, +2.5%
• GOOGL - Recovery signals, +1.9%

**🔴 AVOID NOW** (Negative)
• META, ORCL, IBM - Negative momentum

**⚠️ Remember:**
✓ Diversify your investments
✓ Start with blue-chip stocks
✓ Don't panic-sell on dips
✓ Think long-term (5+ years)

🆘 Want to know about a specific stock?
Type: "Tell me about TSLA"
💼 Ready to invest? Type "Buy [STOCK]" """

    def is_loan_request(self, msg: str) -> bool:
        keywords = ['loan', 'credit', 'borrow', 'financing', 'apy', 'apr']
        return any(k in msg for k in keywords)
    
    def get_loan_info(self) -> str:
        return """💰 **PERSONAL LOANS & CREDIT OFFERS**

**Loan Options Available:**

**1. Personal Loan**
💵 Amount: $1,000 - $50,000
📅 Term: 6-60 months  
💳 APR: Starting at 5.0%
✓ Use for: Any purpose

**2. Investment Loan**
💵 Amount: $5,000 - $100,000
📅 Term: 12-84 months
💳 APR: Starting at 4.5%
✓ Use for: Stock investing

**3. Credit Line**
💵 Amount: $2,000 - $25,000
📅 Revolving (pay as needed)
💳 APR: 6-8%
✓ Use for: Flexibility

**Application:**
1. Click "Loans" in sidebar
2. Fill application form  
3. Get instant decision
4. Receive funds in 24 hours

**Requirements:**
✓ Age: 18+
✓ Steady income
✓ Credit score: 600+
✓ Valid ID & proof of income

💬 Ready to apply? Type "Apply for loan"
📞 Questions? Click "Contact Support" """

    def is_fraud_request(self, msg: str) -> bool:
        keywords = ['fraud', 'security', 'safe', 'card', 'protect', 'suspicious']
        return any(k in msg for k in keywords)
    
    def get_fraud_protection_info(self) -> str:
        return """🛡️ **FRAUD PROTECTION & SECURITY**

**What We Protect You From:**
✓ Unauthorized transactions
✓ Card fraud & cloning
✓ Account takeover
✓ Suspicious login attempts
✓ Unusual trading patterns

**Our Security Measures:**
🔐 Bank-level encryption
📱 2FA (Two-Factor Authentication)
🚨 Real-time fraud monitoring
🔍 AI-powered fraud detection
🛡️ $100,000 fraud guarantee

**If You Spot Fraud:**
1. Click "Report Suspicious Activity"
2. Select transaction/card
3. Describe the issue
4. Our team investigates within 24 hours

**Your Rights:**
💯 Zero liability for fraudulent transactions
📊 Instant notifications of all activities
🔒 Control over your data
📞 24/7 support available

**Stay Safe:**
✓ Never share OTP/passwords
✓ Don't click suspicious links
✓ Review statements regularly
✓ Enable all security features

🚨 See suspicious activity? Report now!
💬 Questions about security? Ask me!"""

    def is_portfolio_request(self, msg: str) -> bool:
        keywords = ['portfolio', 'holdings', 'my stocks', 'investments', 'where is']
        return any(k in msg for k in keywords)
    
    def get_portfolio_guide(self) -> str:
        return """📊 **YOUR PORTFOLIO SECTION**

**What You'll Find:**
📈 Portfolio Value - Total worth of holdings
📊 Gain/Loss - Your profit or loss
💹 Asset Allocation - How diversified you are
📋 Holdings List - Each stock you own
📉 Performance Chart - Visual trends

**How to Use:**
→ Click "Portfolio" in sidebar
→ View all your stocks
→ See current prices & gains
→ Track performance over time

**Manage Your Portfolio:**
➕ **Add Stocks** → Click "Buy" button
➖ **Sell Stocks** → Click "Sell" on holding
📊 **View Analytics** → See detailed analysis
🔄 **Rebalance** → Adjust allocation

**Portfolio Tips:**
💡 Diversify: Mix different sectors
🎯 Rebalance: Check quarterly
📈 Review: Monitor monthly
⚖️ Balance: Mix safe & growth stocks

**Next Steps:**
→ Go to Portfolio section
→ Click "Buy" to add stocks
→ Type "Recommend stocks" for ideas"""

    def is_navigation_request(self, msg: str) -> bool:
        keywords = ['where', 'how to', 'tour', 'navigate', 'menu', 'find']
        return any(k in msg for k in keywords)
    
    def get_site_navigation(self, msg: str) -> str:
        return """🧭 **SITE NAVIGATION GUIDE**

**Left Sidebar Menu:**
📊 Dashboard - Overview & quick view
📈 Markets - Search & view stocks
💼 Portfolio - Your investments
📋 Transactions - Buy/sell history
💳 Cards - Payment methods
📊 Analytics - Detailed analysis
💬 Chat - Talk to me (I'm here!)
💰 Loans - Personal loans & credit

**Top Menu:**
🔔 Notifications - Updates
👤 Profile - Account settings
⚙️ Settings - Preferences
🚪 Logout - Sign out

**Dashboard Features:**
• Real-time portfolio value
• Top gainers & losers
• Recent transactions
• Market overview
• Investment recommendations

**Markets Page:**
🔍 Search any stock
📊 View live prices
📈 See charts & trends
💡 Get recommendations
🎯 Buy/sell stocks

**How to Buy Stocks:**
1. Go to Markets
2. Search stock symbol
3. Click the stock
4. Click "Buy"
5. Enter quantity
6. Confirm order

**How to View Portfolio:**
1. Click "Portfolio"
2. See all holdings
3. Check gains/losses
4. Analyze performance

**Need Help?**
💬 Ask me anything!
→ "How to buy stocks"
→ "Show gainers"
→ "Get recommendations" """

    def get_default_response(self, msg: str) -> str:
        responses = [
            """I didn't quite understand that. Here's what I can help with:

📈 Stock Information
💡 Investment Recommendations
💰 Loan & Credit Offers
📊 Portfolio Management
🛡️ Security & Fraud Protection
🧭 Site Navigation
💬 Financial Education

What interests you? Type a keyword and I'll help!""",

            """Great question! I can assist with:
📊 Real-time stock data
💼 Portfolio analysis
💡 Buy/sell recommendations
💰 Loan applications
🔒 Account security
📚 Investment tips

What would you like to know?""",

            """I'm here to help! Ask me about:
📈 Stocks & markets
💡 Stock recommendations
💳 Cards & payments
💰 Loans & credits
🛡️ Fraud protection
📚 How to trade

Type "Tour" for a full site guide!"""
        ]
        return random.choice(responses)

# Export the service
ai_service = AIService()
