"""
Stock Market Service
Handles all market data, real-time prices, and portfolio management
"""

from datetime import datetime
import random

class StockMarketService:
    """Service for managing stock market data and portfolios"""
    
    def __init__(self):
        self.holdings = {}  # user_id: [holdings]
        self.market_data = {}  # symbol: market_data
        self.initialize_mock_data()
    
    def initialize_mock_data(self):
        """Initialize with mock stock data"""
        popular_stocks = {
            "AAPL": {"name": "Apple Inc", "price": 180.50, "change": 1.25},
            "GOOGL": {"name": "Alphabet Inc", "price": 140.75, "change": 0.85},
            "MSFT": {"name": "Microsoft Corp", "price": 380.25, "change": 2.15},
            "TSLA": {"name": "Tesla Inc", "price": 245.80, "change": 5.20},
            "AMZN": {"name": "Amazon.com Inc", "price": 178.90, "change": 3.80},
            "NVDA": {"name": "NVIDIA Corp", "price": 875.45, "change": 4.10},
            "META": {"name": "Meta Inc", "price": 502.30, "change": -6.20},
            "ORCL": {"name": "Oracle Corp", "price": 132.80, "change": -4.10}
        }
        
        for symbol, data in popular_stocks.items():
            self.market_data[symbol] = {
                "symbol": symbol,
                "name": data["name"],
                "price": data["price"],
                "open": data["price"] - (data["change"] * data["price"] / 100),
                "high": data["price"] + random.uniform(0, 5),
                "low": data["price"] - random.uniform(0, 5),
                "change": data["change"],
                "change_percent": (data["change"] / data["price"]) * 100,
                "volume": random.randint(1000000, 100000000),
                "market_cap": data["price"] * random.randint(1000000000, 5000000000),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def get_stock_price(self, symbol: str):
        """Get current price for a stock"""
        symbol = symbol.upper()
        if symbol in self.market_data:
            return self.market_data[symbol]
        
        # Return default if not in mock data
        return {
            "error": f"Stock {symbol} not found",
            "symbol": symbol,
            "price": 0
        }
    
    async def get_market_overview(self):
        """Get overview of entire market"""
        gainers = sorted(
            self.market_data.values(), 
            key=lambda x: x["change"],
            reverse=True
        )[:5]
        
        losers = sorted(
            self.market_data.values(),
            key=lambda x: x["change"]
        )[:5]
        
        return {
            "total_stocks": len(self.market_data),
            "gainers": gainers,
            "losers": losers,
            "market_status": "OPEN" if self.is_market_open() else "CLOSED"
        }
    
    def is_market_open(self) -> bool:
        """Check if US stock market is open"""
        now = datetime.utcnow()
        day = now.weekday()  # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
        hour = now.hour
        
        # Mon-Fri, 14:30-21:00 UTC (9:30-16:00 EST)
        return (0 <= day <= 4) and (14 <= hour <= 21)
    
    async def add_holding(self, user_id: int, symbol: str, quantity: float, 
                         price: float):
        """Add a stock holding for a user"""
        
        if user_id not in self.holdings:
            self.holdings[user_id] = []
        
        # Check if user already holds this stock
        for holding in self.holdings[user_id]:
            if holding["symbol"] == symbol:
                # Update existing holding
                old_cost = holding["quantity"] * holding["average_price"]
                new_cost = quantity * price
                total_cost = old_cost + new_cost
                total_quantity = holding["quantity"] + quantity
                
                holding["quantity"] = total_quantity
                holding["average_price"] = total_cost / total_quantity
                holding["total_cost"] = total_cost
                holding["updated_at"] = datetime.utcnow().isoformat()
                
                return holding
        
        # New holding
        holding = {
            "symbol": symbol,
            "name": self.market_data.get(symbol, {}).get("name", symbol),
            "quantity": quantity,
            "average_price": price,
            "total_cost": quantity * price,
            "current_price": price,
            "current_value": quantity * price,
            "gain_loss": 0,
            "gain_loss_percent": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.holdings[user_id].append(holding)
        return holding
    
    async def sell_holding(self, user_id: int, symbol: str, quantity: float):
        """Sell a stock holding"""
        
        if user_id not in self.holdings:
            return {"error": "No holdings found"}
        
        for i, holding in enumerate(self.holdings[user_id]):
            if holding["symbol"] == symbol:
                if holding["quantity"] < quantity:
                    return {"error": f"Not enough shares to sell. You have {holding['quantity']}"}
                
                if holding["quantity"] == quantity:
                    # Remove entire holding
                    removed = self.holdings[user_id].pop(i)
                    return {"message": "Holding sold and removed", "holding": removed}
                else:
                    # Reduce quantity
                    holding["quantity"] -= quantity
                    holding["total_cost"] = holding["quantity"] * holding["average_price"]
                    holding["updated_at"] = datetime.utcnow().isoformat()
                    return holding
        
        return {"error": f"You don't hold {symbol}"}
    
    async def get_user_portfolio(self, user_id: int):
        """Get full portfolio for a user"""
        
        if user_id not in self.holdings:
            return {
                "user_id": user_id,
                "holdings": [],
                "total_invested": 0,
                "total_value": 0,
                "total_gain_loss": 0,
                "total_gain_loss_percent": 0
            }
        
        holdings = self.holdings[user_id]
        
        # Update prices from market data
        for holding in holdings:
            if holding["symbol"] in self.market_data:
                market = self.market_data[holding["symbol"]]
                holding["current_price"] = market["price"]
                holding["current_value"] = holding["quantity"] * market["price"]
                holding["gain_loss"] = holding["current_value"] - holding["total_cost"]
                holding["gain_loss_percent"] = (holding["gain_loss"] / holding["total_cost"] * 100) if holding["total_cost"] > 0 else 0
                holding["updated_at"] = datetime.utcnow().isoformat()
        
        # Calculate totals
        total_invested = sum(h["total_cost"] for h in holdings)
        total_value = sum(h["current_value"] for h in holdings)
        total_gain_loss = total_value - total_invested
        total_gain_loss_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "user_id": user_id,
            "holdings": holdings,
            "total_invested": round(total_invested, 2),
            "total_value": round(total_value, 2),
            "total_gain_loss": round(total_gain_loss, 2),
            "total_gain_loss_percent": round(total_gain_loss_percent, 2),
            "holding_count": len(holdings),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_portfolio_analytics(self, user_id: int):
        """Get detailed portfolio analytics"""
        
        portfolio = await self.get_user_portfolio(user_id)
        
        if not portfolio["holdings"]:
            return {
                "error": "No holdings",
                "holdings_count": 0
            }
        
        # Asset allocation
        allocation = {}
        for holding in portfolio["holdings"]:
            allocation[holding["symbol"]] = {
                "value": holding["current_value"],
                "percent": (holding["current_value"] / portfolio["total_value"] * 100) if portfolio["total_value"] > 0 else 0
            }
        
        # Performance
        gainers = [h for h in portfolio["holdings"] if h["gain_loss"] > 0]
        losers = [h for h in portfolio["holdings"] if h["gain_loss"] < 0]
        
        return {
            "total_invested": portfolio["total_invested"],
            "total_value": portfolio["total_value"],
            "total_return": portfolio["total_gain_loss"],
            "total_return_percent": portfolio["total_gain_loss_percent"],
            "holdings_count": portfolio["holding_count"],
            "gainers": len(gainers),
            "losers": len(losers),
            "allocation": allocation,
            "best_performer": max(portfolio["holdings"], key=lambda x: x["gain_loss_percent"]) if portfolio["holdings"] else None,
            "worst_performer": min(portfolio["holdings"], key=lambda x: x["gain_loss_percent"]) if portfolio["holdings"] else None
        }

# Export service
stock_service = StockMarketService()
