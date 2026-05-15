"""
Seed script — run with:  python -m app.seed.seed_db
Generates realistic ecommerce data: 100 customers, 250 orders, refunds, FAQs, tickets.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine, Base
from app.models import (
    User, Customer, Order, Refund, Ticket, ChatHistory,
    FAQDocument, AgentLog, EscalationLog, UserRole,
    OrderStatus, RefundStatus, TicketStatus, TicketPriority
)
from app.core.security import hash_password
from app.database.vector_store import faq_vector_store
from langchain_core.documents import Document
import app.models  # noqa ensure all models loaded

fake = Faker()
random.seed(42)


def utcnow():
    return datetime.now(timezone.utc)


def past(days: int) -> datetime:
    return utcnow() - timedelta(days=random.randint(1, days))


def future(days: int) -> datetime:
    return utcnow() + timedelta(days=random.randint(1, days))


PRODUCTS = [
    {"name": "Wireless Noise-Cancelling Headphones", "sku": "WNC-H100", "price": 199.99},
    {"name": "4K Ultra HD Smart TV 55\"", "sku": "TV-4K55", "price": 699.99},
    {"name": "Ergonomic Office Chair", "sku": "CHR-ERG1", "price": 349.00},
    {"name": "Mechanical Keyboard RGB", "sku": "KB-MRG01", "price": 89.99},
    {"name": "USB-C Docking Station", "sku": "DCK-USB3", "price": 129.99},
    {"name": "Portable Bluetooth Speaker", "sku": "SPK-BT02", "price": 59.99},
    {"name": "Smartphone Stand Adjustable", "sku": "STD-PHN1", "price": 24.99},
    {"name": "Laptop Sleeve 15\"", "sku": "SLV-L15", "price": 19.99},
    {"name": "Webcam 1080p HD", "sku": "CAM-HD02", "price": 79.99},
    {"name": "LED Desk Lamp Smart", "sku": "LMP-LED3", "price": 44.99},
    {"name": "Gaming Mouse 12000 DPI", "sku": "MS-GM12", "price": 54.99},
    {"name": "External SSD 1TB", "sku": "SSD-EXT1", "price": 109.99},
    {"name": "Smart Home Hub", "sku": "HUB-SMT1", "price": 89.99},
    {"name": "Fitness Tracker Band", "sku": "FTB-PRO1", "price": 49.99},
    {"name": "Air Purifier HEPA", "sku": "APR-HPA1", "price": 159.99},
]

FAQ_DOCS = [
    {
        "category": "refund_policy",
        "title": "Refund Policy Overview",
        "content": (
            "Our refund policy allows returns within 30 days of purchase for most items. "
            "Items must be unused and in original packaging. Electronics have a 15-day return window. "
            "Refunds are processed within 5-7 business days to the original payment method. "
            "Custom or personalized items are non-refundable. Digital downloads cannot be refunded after access."
        ),
    },
    {
        "category": "refund_policy",
        "title": "How to Initiate a Refund",
        "content": (
            "To initiate a refund: 1) Log in to your account and go to Orders. "
            "2) Select the order and click 'Request Refund'. 3) Choose your reason. "
            "4) Submit the form. You will receive a confirmation email within 24 hours. "
            "For orders over $500, refunds require manual review and may take 3-5 additional business days."
        ),
    },
    {
        "category": "return_policy",
        "title": "Return Policy and Process",
        "content": (
            "Items can be returned within 30 days of delivery. "
            "To return: package the item securely with all original accessories. "
            "Print the prepaid return label from your account portal. "
            "Drop off at any authorized shipping location. "
            "Once received and inspected, your refund will be processed within 5 business days."
        ),
    },
    {
        "category": "cancellation_policy",
        "title": "Order Cancellation Policy",
        "content": (
            "Orders can be cancelled within 1 hour of placement at no charge. "
            "After 1 hour, if the order has not shipped, a 5% processing fee applies. "
            "Once shipped, cancellation is not possible — you must initiate a return. "
            "To cancel, go to Orders > Select Order > Cancel Order. "
            "Cancelled orders are refunded within 2-3 business days."
        ),
    },
    {
        "category": "shipping_policy",
        "title": "Shipping and Delivery Information",
        "content": (
            "Standard shipping takes 5-7 business days. Express shipping (2-3 days) is available at checkout. "
            "Free shipping on orders over $50. International shipping available to 40+ countries. "
            "You will receive a tracking number via email once your order ships. "
            "Deliveries are attempted twice; after that, the package is held at the local facility for 7 days."
        ),
    },
    {
        "category": "shipping_policy",
        "title": "Delayed and Lost Shipments",
        "content": (
            "If your order is delayed beyond the estimated delivery date, please wait 2 additional business days. "
            "If still not received, contact support with your order number and tracking number. "
            "Lost packages are investigated with the carrier — this can take 5-10 business days. "
            "Confirmed lost shipments are replaced or refunded at no cost to the customer."
        ),
    },
    {
        "category": "account",
        "title": "Managing Your Account",
        "content": (
            "You can manage your account from the Profile section. "
            "Update your email, password, phone number, and shipping addresses anytime. "
            "To delete your account, contact customer support — data is retained for 90 days before purging. "
            "Two-factor authentication is available for enhanced security."
        ),
    },
    {
        "category": "payments",
        "title": "Accepted Payment Methods",
        "content": (
            "We accept Visa, MasterCard, American Express, PayPal, Apple Pay, and Google Pay. "
            "Bank transfers are accepted for orders over $1,000. "
            "Buy Now Pay Later is available via Klarna for eligible customers. "
            "All transactions are secured with 256-bit SSL encryption."
        ),
    },
]

ORDER_STATUSES = [
    OrderStatus.delivered,
    OrderStatus.delivered,
    OrderStatus.delivered,
    OrderStatus.shipped,
    OrderStatus.shipped,
    OrderStatus.delayed,
    OrderStatus.cancelled,
    OrderStatus.pending,
]

TICKET_SUBJECTS = [
    "Where is my order?",
    "I want to return my item",
    "My package arrived damaged",
    "Refund not received after 7 days",
    "Wrong item was delivered",
    "Order shows delivered but not received",
    "How do I cancel my order?",
    "I need to change my shipping address",
    "My payment was charged twice",
    "Product stopped working after 2 days",
]


def random_product_details(n: int = None) -> list:
    n = n or random.randint(1, 3)
    items = random.sample(PRODUCTS, min(n, len(PRODUCTS)))
    return [{"name": p["name"], "sku": p["sku"], "qty": random.randint(1, 2), "price": p["price"]} for p in items]


def seed(db: Session):
    print("🌱 Starting seed...")

    # ── Create tables ──────────────────────────────────────────────────────────
    Base.metadata.create_all(bind=engine)

    # ── Admin user ─────────────────────────────────────────────────────────────
    admin_email = "admin@supportai.dev"
    if not db.query(User).filter(User.email == admin_email).first():
        admin = User(
            id=str(uuid.uuid4()),
            email=admin_email,
            hashed_password=hash_password("Admin@1234"),
            role=UserRole.admin,
            is_verified=True,
        )
        db.add(admin)
        print(f"  ✅ Admin created: {admin_email} / Admin@1234")

    # ── Test customer ──────────────────────────────────────────────────────────
    test_email = "customer@supportai.dev"
    if not db.query(User).filter(User.email == test_email).first():
        test_user = User(
            id=str(uuid.uuid4()),
            email=test_email,
            hashed_password=hash_password("Customer@1234"),
            role=UserRole.customer,
            is_verified=True,
        )
        db.add(test_user)
        db.flush()
        db.add(Customer(
            user_id=test_user.id,
            full_name="Alex Johnson",
            phone="+1-555-0100",
            address="123 Main St",
            city="San Francisco",
            country="USA",
        ))
        print(f"  ✅ Test customer created: {test_email} / Customer@1234")

    # ── 100 random customers ───────────────────────────────────────────────────
    customer_ids = []
    for i in range(100):
        email = fake.unique.email()
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hash_password("Test@1234"),
            role=UserRole.customer,
            is_verified=random.choice([True, True, True, False]),
        )
        db.add(user)
        db.flush()
        cust = Customer(
            id=str(uuid.uuid4()),
            user_id=user.id,
            full_name=fake.name(),
            phone=fake.phone_number()[:20],
            address=fake.street_address(),
            city=fake.city(),
            country=fake.country()[:100],
        )
        db.add(cust)
        customer_ids.append(cust.id)

    db.flush()
    print(f"  ✅ 100 customers created")

    # ── 250 orders ─────────────────────────────────────────────────────────────
    order_ids = []
    refund_eligible_orders = []
    for i in range(250):
        cust_id = random.choice(customer_ids)
        status = random.choice(ORDER_STATUSES)
        products = random_product_details()
        total = sum(p["price"] * p["qty"] for p in products)
        is_refund_eligible = status in (OrderStatus.delivered, OrderStatus.cancelled)

        order = Order(
            id=str(uuid.uuid4()),
            customer_id=cust_id,
            order_number=f"ORD-{fake.unique.numerify('########')}",
            status=status,
            total_amount=round(total, 2),
            currency="USD",
            product_details=products,
            shipping_address=fake.address(),
            tracking_number=fake.bothify("1Z###########") if status != OrderStatus.pending else None,
            estimated_delivery=future(10) if status in (OrderStatus.shipped, OrderStatus.delayed) else None,
            delivered_at=past(30) if status == OrderStatus.delivered else None,
            is_refund_eligible=is_refund_eligible,
        )
        db.add(order)
        order_ids.append(order.id)
        if is_refund_eligible:
            refund_eligible_orders.append((order.id, total))

    db.flush()
    print(f"  ✅ 250 orders created")

    # ── 60 refunds ─────────────────────────────────────────────────────────────
    refund_sample = random.sample(refund_eligible_orders, min(60, len(refund_eligible_orders)))
    statuses = [RefundStatus.approved] * 25 + [RefundStatus.rejected] * 15 + [RefundStatus.pending] * 20
    random.shuffle(statuses)
    for idx, (oid, total) in enumerate(refund_sample):
        ref_status = statuses[idx % len(statuses)]
        db.add(Refund(
            id=str(uuid.uuid4()),
            order_id=oid,
            status=ref_status,
            amount=round(total * random.uniform(0.5, 1.0), 2),
            reason=random.choice([
                "Item not as described",
                "Received wrong product",
                "Item arrived damaged",
                "Changed my mind",
                "Late delivery",
            ]),
            rejection_reason="Order outside refund window" if ref_status == RefundStatus.rejected else None,
        ))
    print(f"  ✅ 60 refunds created")

    # ── Tickets ────────────────────────────────────────────────────────────────
    for i in range(80):
        cust_id = random.choice(customer_ids)
        t_status = random.choice(list(TicketStatus))
        db.add(Ticket(
            id=str(uuid.uuid4()),
            customer_id=cust_id,
            ticket_number=f"TKT-{fake.unique.numerify('########')}",
            subject=random.choice(TICKET_SUBJECTS),
            description=fake.paragraph(nb_sentences=2),
            status=t_status,
            priority=random.choice(list(TicketPriority)),
        ))
    print(f"  ✅ 80 tickets created")

    # ── FAQ Documents ──────────────────────────────────────────────────────────
    faq_docs_for_faiss = []
    for doc in FAQ_DOCS:
        faq = FAQDocument(
            id=str(uuid.uuid4()),
            category=doc["category"],
            title=doc["title"],
            content=doc["content"],
        )
        db.add(faq)
        faq_docs_for_faiss.append(
            Document(
                page_content=f"{doc['title']}\n{doc['content']}",
                metadata={"category": doc["category"], "faq_id": str(faq.id), "title": doc["title"]}
            )
        )
        
    print(f"  ✅ {len(FAQ_DOCS)} FAQ documents created")
    
    print("  🧠 Indexing FAQ documents into FAISS vector store...")
    faq_vector_store.add_documents(faq_docs_for_faiss)
    print("  ✅ FAISS index created and saved locally")

    db.commit()
    print("\n🎉 Seed complete!")
    print("\n📋 Test Accounts:")
    print("  Admin:    admin@supportai.dev    / Admin@1234")
    print("  Customer: customer@supportai.dev / Customer@1234")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
