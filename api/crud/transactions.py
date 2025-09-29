"""CRUD operations for Transaction model"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from ..models import Bet, Transaction, TransactionStatus, TransactionType, User
from ..schemas import TransactionCreateRequest, TransactionUpdateRequest
from .base import CRUDBase


class CRUDTransaction(CRUDBase[Transaction, TransactionCreateRequest, TransactionUpdateRequest]):

    def create_with_user(
        self, db: Session, *, obj_in: TransactionCreateRequest, user_id: int
    ) -> Transaction:
        """Create transaction with user association and calculate net amount"""
        # Get user for validation
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Calculate net amount
        net_amount = obj_in.amount - (obj_in.fee_amount or Decimal("0.00"))

        # Create transaction data
        transaction_data = obj_in.dict()
        transaction_data.update({"user_id": user_id, "net_amount": net_amount})

        db_obj = self.model(**transaction_data)

        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create transaction: {str(e)}")

    def get_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None,
    ) -> List[Transaction]:
        """Get transactions for a specific user"""
        filters = {"user_id": user_id}
        if transaction_type:
            filters["transaction_type"] = transaction_type
        if status:
            filters["status"] = status

        return self.get_multi(db=db, skip=skip, limit=limit, filters=filters, order_by="created_at")

    def get_by_bet(self, db: Session, *, bet_id: int) -> List[Transaction]:
        """Get all transactions for a specific bet"""
        return self.get_multi(db=db, filters={"bet_id": bet_id}, order_by="created_at")

    def get_by_sportsbook(
        self, db: Session, *, sportsbook_id: str, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """Get transactions for a specific sportsbook"""
        return self.get_multi(
            db=db, skip=skip, limit=limit, filters={"sportsbook_id": sportsbook_id}
        )

    def get_pending_transactions(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """Get all pending transactions"""
        return self.get_multi(
            db=db, skip=skip, limit=limit, filters={"status": TransactionStatus.PENDING}
        )

    def get_failed_transactions(
        self, db: Session, *, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """Get failed transactions, optionally filtered by user"""
        filters = {"status": TransactionStatus.FAILED}
        if user_id:
            filters["user_id"] = user_id

        return self.get_multi(db=db, skip=skip, limit=limit, filters=filters)

    def get_recent_transactions(
        self,
        db: Session,
        *,
        days: int = 30,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transaction]:
        """Get transactions from the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(self.model).filter(self.model.created_at >= cutoff_date)

        if user_id:
            query = query.filter(self.model.user_id == user_id)

        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()

    def complete_transaction(
        self,
        db: Session,
        *,
        transaction_id: int,
        external_transaction_id: Optional[str] = None,
        processing_details: Optional[Dict[str, Any]] = None,
    ) -> Optional[Transaction]:
        """Mark transaction as completed"""
        transaction = self.get(db=db, id=transaction_id)
        if not transaction:
            return None

        if transaction.status != TransactionStatus.PENDING:
            raise ValueError("Can only complete pending transactions")

        transaction.status = TransactionStatus.COMPLETED
        transaction.processed_at = datetime.utcnow()

        if external_transaction_id:
            transaction.external_transaction_id = external_transaction_id

        if processing_details:
            import json

            transaction.processing_details = json.dumps(processing_details)

        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    def fail_transaction(
        self, db: Session, *, transaction_id: int, failure_reason: str, retry: bool = False
    ) -> Optional[Transaction]:
        """Mark transaction as failed"""
        transaction = self.get(db=db, id=transaction_id)
        if not transaction:
            return None

        if retry and transaction.retry_count < 3:
            transaction.retry_count += 1
            # Could implement retry logic here
        else:
            transaction.status = TransactionStatus.FAILED
            transaction.processed_at = datetime.utcnow()
            transaction.failure_reason = failure_reason

        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    def get_user_balance(self, db: Session, *, user_id: int) -> Decimal:
        """Calculate user's current balance from transactions"""
        result = (
            db.query(func.sum(self.model.net_amount))
            .filter(
                and_(
                    self.model.user_id == user_id, self.model.status == TransactionStatus.COMPLETED
                )
            )
            .scalar()
        )

        return Decimal(str(result or 0))

    def get_user_transaction_summary(
        self, db: Session, *, user_id: int, days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get transaction summary for a user"""
        query = db.query(self.model).filter(
            and_(self.model.user_id == user_id, self.model.status == TransactionStatus.COMPLETED)
        )

        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(self.model.created_at >= cutoff_date)

        transactions = query.all()

        if not transactions:
            return {
                "total_transactions": 0,
                "total_deposited": 0.0,
                "total_withdrawn": 0.0,
                "total_bet_placed": 0.0,
                "total_bet_payout": 0.0,
                "net_amount": 0.0,
                "total_fees": 0.0,
            }

        # Calculate summaries by type
        deposits = sum(
            float(t.amount) for t in transactions if t.transaction_type == TransactionType.DEPOSIT
        )
        withdrawals = sum(
            abs(float(t.amount))
            for t in transactions
            if t.transaction_type == TransactionType.WITHDRAWAL
        )
        bet_placed = sum(
            abs(float(t.amount))
            for t in transactions
            if t.transaction_type == TransactionType.BET_PLACED
        )
        bet_payouts = sum(
            float(t.amount)
            for t in transactions
            if t.transaction_type == TransactionType.BET_PAYOUT
        )
        total_fees = sum(float(t.fee_amount) for t in transactions)
        net_amount = sum(float(t.net_amount) for t in transactions)

        return {
            "total_transactions": len(transactions),
            "total_deposited": round(deposits, 2),
            "total_withdrawn": round(withdrawals, 2),
            "total_bet_placed": round(bet_placed, 2),
            "total_bet_payout": round(bet_payouts, 2),
            "net_amount": round(net_amount, 2),
            "total_fees": round(total_fees, 2),
            "period_days": days or "all_time",
        }

    def create_bet_transaction(
        self,
        db: Session,
        *,
        bet_id: int,
        transaction_type: TransactionType,
        amount: Decimal,
        sportsbook_id: str,
        external_transaction_id: Optional[str] = None,
    ) -> Transaction:
        """Create a transaction associated with a bet"""
        # Get bet and user
        bet = db.query(Bet).filter(Bet.id == bet_id).first()
        if not bet:
            raise ValueError("Bet not found")

        transaction_data = {
            "user_id": bet.user_id,
            "bet_id": bet_id,
            "amount": amount,
            "transaction_type": transaction_type,
            "sportsbook_id": sportsbook_id,
            "sportsbook_name": bet.sportsbook_name,
            "external_transaction_id": external_transaction_id,
            "description": f"{transaction_type.value} for bet #{bet_id}",
            "category": "betting",
            "net_amount": amount,  # Will be adjusted for fees if needed
        }

        db_obj = self.model(**transaction_data)

        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create bet transaction: {str(e)}")


transaction_crud = CRUDTransaction(Transaction)
