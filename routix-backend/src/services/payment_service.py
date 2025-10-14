"""
Payment Service for handling credit purchases.

This is a mock implementation that simulates payment processing.
In production, integrate with real payment gateways like:
- Stripe
- PayPal
- Square
- etc.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User
from src.models.generation import CreditTransaction


class PaymentService:
    """Service for handling payment processing."""
    
    # Credit package definitions
    CREDIT_PACKAGES = {
        "starter": {
            "id": "starter",
            "name": "Starter Pack",
            "credits": 50,
            "price": 9.99,
            "bonus": 0,
        },
        "popular": {
            "id": "popular",
            "name": "Popular Pack",
            "credits": 150,
            "price": 24.99,
            "bonus": 25,
        },
        "pro": {
            "id": "pro",
            "name": "Pro Pack",
            "credits": 300,
            "price": 49.99,
            "bonus": 75,
        }
    }
    
    def __init__(self):
        """Initialize payment service."""
        pass
    
    async def create_payment_intent(
        self,
        user: User,
        package_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Create a payment intent for credit purchase.
        
        In production, this would create a payment intent with a real gateway.
        For now, it returns a mock payment intent.
        """
        
        # Validate package
        package = self.CREDIT_PACKAGES.get(package_id)
        if not package:
            raise ValueError(f"Invalid package ID: {package_id}")
        
        # Create payment intent ID
        payment_intent_id = f"pi_mock_{uuid.uuid4().hex[:16]}"
        
        # In production, create actual payment intent with gateway
        # Example with Stripe:
        # import stripe
        # intent = stripe.PaymentIntent.create(
        #     amount=int(package["price"] * 100),  # Amount in cents
        #     currency="usd",
        #     customer=user.stripe_customer_id,
        #     metadata={
        #         "user_id": user.id,
        #         "package_id": package_id,
        #         "credits": package["credits"] + package["bonus"]
        #     }
        # )
        # return {
        #     "payment_intent_id": intent.id,
        #     "client_secret": intent.client_secret,
        #     ...
        # }
        
        return {
            "payment_intent_id": payment_intent_id,
            "client_secret": f"secret_mock_{uuid.uuid4().hex[:16]}",
            "amount": package["price"],
            "currency": "usd",
            "package": package,
            "status": "requires_payment_method",
            # Mock payment URL (in production this would be from payment gateway)
            "payment_url": f"/payment/checkout/{payment_intent_id}"
        }
    
    async def process_payment(
        self,
        user: User,
        package_id: str,
        payment_method_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process a payment for credit purchase.
        
        This is a mock implementation. In production, this would:
        1. Charge the customer via payment gateway
        2. Verify payment success
        3. Add credits to user account
        4. Create transaction record
        """
        
        # Validate package
        package = self.CREDIT_PACKAGES.get(package_id)
        if not package:
            raise ValueError(f"Invalid package ID: {package_id}")
        
        # Simulate payment processing delay
        await asyncio.sleep(1)
        
        # Mock payment processing (always succeeds in development)
        # In production, this would call the real payment gateway
        payment_successful = True  # Mock success
        
        if not payment_successful:
            return {
                "success": False,
                "error": "Payment failed",
                "transaction_id": None
            }
        
        # Calculate total credits (base + bonus)
        total_credits = package["credits"] + package["bonus"]
        
        # Add credits to user
        user.add_credits(total_credits)
        
        # Create transaction record
        transaction_id = str(uuid.uuid4())
        transaction = CreditTransaction(
            id=transaction_id,
            user_id=user.id,
            type="purchase",
            amount=total_credits,
            description=f"Purchased {package['name']} ({total_credits} credits)",
            reference_id=f"payment_mock_{uuid.uuid4().hex[:8]}"
        )
        
        db.add(transaction)
        await db.commit()
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "credits_added": total_credits,
            "new_balance": user.credits,
            "package": package
        }
    
    async def handle_webhook(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Handle webhook events from payment gateway.
        
        Common events:
        - payment_intent.succeeded
        - payment_intent.failed
        - charge.refunded
        - etc.
        """
        
        # In production, verify webhook signature
        # Example with Stripe:
        # try:
        #     event = stripe.Webhook.construct_event(
        #         payload, signature, webhook_secret
        #     )
        # except ValueError:
        #     return {"success": False, "error": "Invalid payload"}
        # except stripe.error.SignatureVerificationError:
        #     return {"success": False, "error": "Invalid signature"}
        
        if event_type == "payment_intent.succeeded":
            return await self._handle_payment_success(event_data, db)
        
        elif event_type == "payment_intent.failed":
            return await self._handle_payment_failure(event_data, db)
        
        elif event_type == "charge.refunded":
            return await self._handle_refund(event_data, db)
        
        else:
            return {"success": True, "message": f"Unhandled event type: {event_type}"}
    
    async def _handle_payment_success(
        self,
        event_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle successful payment."""
        
        # Extract data from event
        user_id = event_data.get("metadata", {}).get("user_id")
        package_id = event_data.get("metadata", {}).get("package_id")
        credits = event_data.get("metadata", {}).get("credits")
        
        if not all([user_id, package_id, credits]):
            return {"success": False, "error": "Missing required data"}
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Add credits
        user.add_credits(int(credits))
        
        # Create transaction
        transaction = CreditTransaction(
            user_id=user_id,
            type="purchase",
            amount=int(credits),
            description=f"Credit purchase via payment gateway",
            reference_id=event_data.get("payment_intent_id")
        )
        
        db.add(transaction)
        await db.commit()
        
        return {"success": True, "user_id": user_id, "credits_added": credits}
    
    async def _handle_payment_failure(
        self,
        event_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle failed payment."""
        
        # Log the failure
        print(f"Payment failed: {event_data}")
        
        # In production, you might:
        # - Send notification to user
        # - Log for analytics
        # - Trigger retry logic
        
        return {"success": True, "message": "Payment failure logged"}
    
    async def _handle_refund(
        self,
        event_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Handle payment refund."""
        
        # Extract refund data
        user_id = event_data.get("metadata", {}).get("user_id")
        credits_to_deduct = event_data.get("metadata", {}).get("credits")
        
        if not all([user_id, credits_to_deduct]):
            return {"success": False, "error": "Missing refund data"}
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Deduct credits
        user.deduct_credits(int(credits_to_deduct))
        
        # Create refund transaction
        transaction = CreditTransaction(
            user_id=user_id,
            type="refund",
            amount=-int(credits_to_deduct),
            description="Refund processed",
            reference_id=event_data.get("charge_id")
        )
        
        db.add(transaction)
        await db.commit()
        
        return {"success": True, "user_id": user_id, "credits_refunded": credits_to_deduct}
    
    def get_packages(self) -> Dict[str, Dict[str, Any]]:
        """Get available credit packages."""
        return self.CREDIT_PACKAGES
    
    def get_package(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific credit package."""
        return self.CREDIT_PACKAGES.get(package_id)
