"""
Loan Service
Handles all loan applications, approvals, and payments
"""

from datetime import datetime, timedelta
from enum import Enum

class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    REJECTED = "rejected"

class LoanService:
    """Service for managing loans and credit"""
    
    def __init__(self):
        self.loans = []
        self.payments = []
        
    async def apply_for_loan(self, user_id: int, amount: float, 
                            duration_months: int):
        """
        Create a new loan application
        """
        
        # Validate amount
        if amount < 1000:
            return {"error": "Minimum loan amount is $1,000"}
        if amount > 100000:
            return {"error": "Maximum loan amount is $100,000"}
        
        # Validate duration
        if duration_months < 6:
            return {"error": "Minimum duration is 6 months"}
        if duration_months > 84:
            return {"error": "Maximum duration is 84 months"}
        
        # Calculate terms
        terms = self.calculate_loan_terms(amount, duration_months)
        
        loan = {
            "id": len(self.loans) + 1,
            "user_id": user_id,
            "amount": amount,
            "interest_rate": terms["interest_rate"],
            "duration_months": duration_months,
            "monthly_payment": terms["monthly_payment"],
            "total_interest": terms["total_interest"],
            "total_repay": terms["total_repay"],
            "status": LoanStatus.PENDING.value,
            "paid_amount": 0.0,
            "remaining_amount": terms["total_repay"],
            "payments_completed": 0,
            "start_date": None,
            "end_date": None,
            "next_payment_date": None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.loans.append(loan)
        return loan
    
    def calculate_loan_terms(self, amount: float, duration_months: int) -> dict:
        """
        Calculate loan terms and monthly payment
        Uses standard amortization formula
        """
        
        # Determine APR based on amount
        if amount <= 5000:
            apr = 0.08  # 8%
        elif amount <= 25000:
            apr = 0.06  # 6%
        else:
            apr = 0.045  # 4.5%
        
        # Monthly interest rate
        monthly_rate = apr / 12
        
        # Calculate monthly payment using amortization formula
        # M = P * [r(1+r)^n] / [(1+r)^n - 1]
        numerator = amount * monthly_rate * ((1 + monthly_rate) ** duration_months)
        denominator = ((1 + monthly_rate) ** duration_months) - 1
        monthly_payment = numerator / denominator if denominator != 0 else amount / duration_months
        
        total_repay = monthly_payment * duration_months
        total_interest = total_repay - amount
        
        return {
            "interest_rate": apr * 100,  # In percentage
            "monthly_payment": round(monthly_payment, 2),
            "total_interest": round(total_interest, 2),
            "total_repay": round(total_repay, 2)
        }
    
    async def approve_loan(self, loan_id: int):
        """Approve a pending loan application"""
        for loan in self.loans:
            if loan["id"] == loan_id and loan["status"] == LoanStatus.PENDING.value:
                loan["status"] = LoanStatus.APPROVED.value
                loan["start_date"] = (datetime.utcnow() + timedelta(days=1)).isoformat()
                
                # Calculate end date
                start = datetime.fromisoformat(loan["start_date"])
                end = start + timedelta(days=30 * loan["duration_months"])
                loan["end_date"] = end.isoformat()
                loan["next_payment_date"] = (start + timedelta(days=30)).isoformat()
                
                return loan
        return None
    
    async def reject_loan(self, loan_id: int, reason: str = ""):
        """Reject a pending loan application"""
        for loan in self.loans:
            if loan["id"] == loan_id and loan["status"] == LoanStatus.PENDING.value:
                loan["status"] = LoanStatus.REJECTED.value
                loan["rejection_reason"] = reason
                return loan
        return None
    
    async def activate_loan(self, loan_id: int):
        """Activate an approved loan (funds disbursed)"""
        for loan in self.loans:
            if loan["id"] == loan_id and loan["status"] == LoanStatus.APPROVED.value:
                loan["status"] = LoanStatus.ACTIVE.value
                loan["activated_at"] = datetime.utcnow().isoformat()
                return loan
        return None
    
    async def make_payment(self, loan_id: int, amount: float):
        """Record a loan payment"""
        for loan in self.loans:
            if loan["id"] == loan_id and loan["status"] in [LoanStatus.ACTIVE.value, LoanStatus.ACTIVE.value]:
                
                if amount < loan["monthly_payment"] * 0.5:
                    return {"error": "Payment too small. Minimum is 50% of monthly payment"}
                
                # Calculate principal and interest split
                remaining_principal = loan["remaining_amount"] - (loan["monthly_payment"] * loan["payments_completed"])
                interest_portion = (remaining_principal * (loan["interest_rate"] / 100)) / 12
                principal_portion = amount - interest_portion
                
                payment = {
                    "id": len(self.payments) + 1,
                    "loan_id": loan_id,
                    "amount": amount,
                    "principal": principal_portion,
                    "interest": interest_portion,
                    "status": "completed",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                self.payments.append(payment)
                
                # Update loan
                loan["paid_amount"] += amount
                loan["remaining_amount"] -= principal_portion
                loan["payments_completed"] += 1
                
                # Update next payment date
                current_next = datetime.fromisoformat(loan["next_payment_date"])
                loan["next_payment_date"] = (current_next + timedelta(days=30)).isoformat()
                
                # Check if loan completed
                if loan["remaining_amount"] <= 0:
                    loan["status"] = LoanStatus.COMPLETED.value
                    loan["completed_at"] = datetime.utcnow().isoformat()
                
                return payment
        
        return {"error": "Loan not found or cannot accept payments"}
    
    async def get_user_loans(self, user_id: int):
        """Get all loans for a user"""
        return [loan for loan in self.loans if loan["user_id"] == user_id]
    
    async def get_loan_details(self, loan_id: int):
        """Get detailed loan information"""
        for loan in self.loans:
            if loan["id"] == loan_id:
                # Add payment history
                payments = [p for p in self.payments if p["loan_id"] == loan_id]
                loan["payments"] = payments
                loan["payment_count"] = len(payments)
                return loan
        return None
    
    async def get_loan_summary(self, user_id: int):
        """Get loan summary for a user"""
        user_loans = [loan for loan in self.loans if loan["user_id"] == user_id]
        
        active_loans = [l for l in user_loans if l["status"] == LoanStatus.ACTIVE.value]
        completed_loans = [l for l in user_loans if l["status"] == LoanStatus.COMPLETED.value]
        pending_loans = [l for l in user_loans if l["status"] == LoanStatus.PENDING.value]
        
        total_borrowed = sum(l["amount"] for l in completed_loans + active_loans)
        total_paid = sum(l["paid_amount"] for l in completed_loans + active_loans)
        total_remaining = sum(l["remaining_amount"] for l in active_loans)
        
        return {
            "total_loans": len(user_loans),
            "active_loans": len(active_loans),
            "completed_loans": len(completed_loans),
            "pending_loans": len(pending_loans),
            "total_borrowed": total_borrowed,
            "total_paid": total_paid,
            "total_remaining": total_remaining,
            "monthly_obligations": sum(l["monthly_payment"] for l in active_loans),
            "loans": {
                "active": active_loans,
                "completed": completed_loans,
                "pending": pending_loans
            }
        }

# Export service
loan_service = LoanService()
