from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invoice, Order, OrderStatus, OrderType
import uuid
from datetime import date

@receiver(post_save, sender=Order)
def generate_invoice(sender, created, instance, **kwargs):
    if instance.status == OrderStatus.COMPLETED:
                # Generate a unique invoice number
        invoice_number = generate_unique_invoice_number()
        invoice = Invoice(order=instance, invoice_number=invoice_number)
        invoice.save()

def generate_unique_invoice_number():
    # Generate a unique UUID
    unique_id = str(uuid.uuid4().fields[-1])[:6]
    # Construct the invoice number with "inv" prefix
    invoice_number = f"inv{unique_id}"
    return invoice_number
