from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invoice, Order, OrderStatus, OrderType
import uuid

@receiver(post_save, sender=Order)
def generate_invoice(sender, created, instance, **kwargs):
    if instance.status == OrderStatus.COMPLETED:
                # Generate a unique invoice number
        invoice_number = generate_unique_invoice_number()
        # Generate the invoice text
        invoice_text = f"Invoice for Order #{instance.pk}\n"
        invoice_text += f"Order type: {instance.type}\n"
        invoice_text += f"Invoice number: {invoice_number}\n"
        invoice_text += f"Total Amount: {instance.total_amount}\n"
        invoice_text += "Thank you for your purchase!"
        invoice = Invoice(order=instance, invoice_number=invoice_number, invoice=invoice_text)
        invoice.save()
        print(invoice_text)

def generate_unique_invoice_number():
    # Generate a unique UUID
    unique_id = str(uuid.uuid4().fields[-1])[:6]
    # Construct the invoice number with "inv" prefix
    invoice_number = f"inv{unique_id}"
    return invoice_number
