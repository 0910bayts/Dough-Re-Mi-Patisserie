import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dough_re_mi.settings')
django.setup()

from bakery.models import Order, Receipt, UserProfile
from django.utils import timezone
from datetime import timedelta

def backfill_receipts():
    """Create receipts for orders that don't have them"""
    
    # Get all orders that don't have receipts
    orders_without_receipts = []
    
    for order in Order.objects.all():
        receipt_exists = Receipt.objects.filter(session_id=order.session_id).exists()
        if not receipt_exists:
            orders_without_receipts.append(order)
    
    print(f"Found {len(orders_without_receipts)} orders without receipts")
    
    # Create receipts for these orders
    created_count = 0
    for order in orders_without_receipts:
        try:
            # Get user profile for contact number
            contact_number = None
            if hasattr(order.user, 'userprofile'):
                contact_number = order.user.userprofile.contactnumber
            
            # Get full name from user
            full_name = order.user.get_full_name()
            
            # Get payment option from order if available
            payment_option = order.payment_option
            
            # Calculate pickup date (3 days after order date)
            pickup_date = None
            if order.ordered_at:
                pickup_date = order.ordered_at + timedelta(days=3)
            
            # Create receipt
            receipt = Receipt.objects.create(
                user=order.user,
                session_id=order.session_id,
                total_price=order.item_price,
                full_name=full_name,
                contact_number=contact_number,
                reference_number=order.reference_number,
                payment_option=payment_option,
                total_amount=order.total_amount,
                amount_paid=order.amount_paid,
                remaining_balance=order.remaining_balance,
                pickup_availability_date=pickup_date
            )
            
            created_count += 1
            print(f"Created receipt for order {order.id} (session: {order.session_id})")
            print(f"  - Full name: {full_name}")
            print(f"  - Contact: {contact_number}")
            print(f"  - Payment option: {payment_option}")
            
        except Exception as e:
            print(f"Error creating receipt for order {order.id}: {str(e)}")
    
    print(f"\nSuccessfully created {created_count} receipts")

if __name__ == '__main__':
    backfill_receipts()
