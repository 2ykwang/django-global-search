import random
import sys
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

# Import all models
from apps.analytics.models import Conversion, Event, PageView, SessionData
from apps.content.models import Article, BlogPost, Comment, MediaFile
from apps.inventory.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Stock,
    StockMovement,
    Supplier,
    Warehouse,
)
from apps.orders.models import Invoice, Order, OrderItem, Refund, ShippingAddress
from apps.products.models import Category, Product, ProductImage, ProductVariant, Tag
from apps.support.models import FAQ, KnowledgeBaseArticle, Ticket, TicketCategory, TicketMessage
from apps.users.models import Address, PaymentMethod, UserProfile

fake = Faker()


class Command(BaseCommand):
    help = "Generate demo data for all models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=1000,
            help="Batch size for bulk_create operations (default: 1000)",
        )

    def handle(self, *args, **options):
        self.chunk_size = options["chunk_size"]
        self.stdout.write(self.style.SUCCESS("Starting data generation..."))

        try:
            # Create data in order of dependencies
            self.create_users()
            self.create_products()
            self.create_orders()
            self.create_inventory()
            self.create_content()
            self.create_support()
            self.create_analytics()

            self.stdout.write(self.style.SUCCESS("\n✓ All data generated successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error: {str(e)}"))
            sys.exit(1)

    def create_users(self):
        """Create 100K users with profiles, addresses, and payment methods."""
        self.stdout.write("\n[1/7] Creating users and related data...")

        # Create users
        users = []
        for i in range(100_000):
            users.append(
                User(
                    username=f"user_{i:06d}",
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_active=True,
                    date_joined=fake.date_time_between(
                        start_date="-2y", end_date="now", tzinfo=timezone.utc
                    ),
                )
            )
            if (i + 1) % self.chunk_size == 0:
                User.objects.bulk_create(users, ignore_conflicts=True)
                self.stdout.write(f"  Created {i + 1:,} users...")
                users = []
        if users:
            User.objects.bulk_create(users, ignore_conflicts=True)
            self.stdout.write("  Created 100,000 users")

        # Get all user IDs
        user_ids = list(User.objects.values_list("id", flat=True))

        # Create user profiles
        profiles = []
        for user_id in user_ids:
            profiles.append(
                UserProfile(
                    user_id=user_id,
                    bio=fake.paragraph(nb_sentences=3),
                    company=fake.company(),
                    job_title=fake.job(),
                    phone_number=fake.phone_number()[:20],
                    website=fake.url() if random.random() > 0.5 else "",
                    avatar_url=fake.image_url() if random.random() > 0.7 else "",
                )
            )
            if len(profiles) >= self.chunk_size:
                UserProfile.objects.bulk_create(profiles, ignore_conflicts=True)
                profiles = []
        if profiles:
            UserProfile.objects.bulk_create(profiles, ignore_conflicts=True)
        self.stdout.write("  Created 100,000 user profiles")

        # Create addresses (200K - 2 per user on average)
        addresses = []
        address_types = ["home", "work", "billing", "shipping"]
        for i, user_id in enumerate(user_ids * 2):
            addresses.append(
                Address(
                    user_id=user_id,
                    address_type=random.choice(address_types),
                    full_address=fake.address(),
                    street_address=fake.street_address(),
                    city=fake.city(),
                    state=fake.state(),
                    postal_code=fake.postcode(),
                    country=fake.country(),
                    is_default=(i % 2 == 0),
                )
            )
            if len(addresses) >= self.chunk_size:
                Address.objects.bulk_create(addresses)
                addresses = []
        if addresses:
            Address.objects.bulk_create(addresses)
        self.stdout.write("  Created 200,000 addresses")

        # Create payment methods (150K)
        payment_methods = []
        method_types = ["credit_card", "debit_card", "paypal", "bank_transfer"]
        card_brands = ["Visa", "Mastercard", "American Express", "Discover"]
        for i in range(150_000):
            payment_methods.append(
                PaymentMethod(
                    user_id=random.choice(user_ids),
                    method_type=random.choice(method_types),
                    card_holder_name=fake.name(),
                    card_last_four=str(random.randint(1000, 9999)),
                    card_brand=random.choice(card_brands),
                    expiry_month=random.randint(1, 12),
                    expiry_year=random.randint(2024, 2030),
                    is_default=random.random() > 0.7,
                    is_active=random.random() > 0.1,
                )
            )
            if len(payment_methods) >= self.chunk_size:
                PaymentMethod.objects.bulk_create(payment_methods)
                payment_methods = []
        if payment_methods:
            PaymentMethod.objects.bulk_create(payment_methods)
        self.stdout.write("  Created 150,000 payment methods")

    def create_products(self):
        """Create 500K products (outlier) with categories, tags, images, and variants."""
        self.stdout.write("\n[2/7] Creating products and related data...")

        # Create categories (500)
        categories = []
        for i in range(500):
            name = f"{fake.word().capitalize()} {fake.word().capitalize()}"
            categories.append(
                Category(
                    name=name,
                    slug=slugify(name) + f"-{i}",
                    description=fake.paragraph(),
                    is_active=random.random() > 0.1,
                )
            )
        Category.objects.bulk_create(categories)
        category_ids = list(Category.objects.values_list("id", flat=True))
        self.stdout.write("  Created 500 categories")

        # Create tags (5000)
        tags = []
        for i in range(5000):
            name = fake.word()
            tags.append(
                Tag(
                    name=f"{name}-{i}",
                    slug=slugify(f"{name}-{i}"),
                )
            )
        Tag.objects.bulk_create(tags)
        tag_ids = list(Tag.objects.values_list("id", flat=True))
        self.stdout.write("  Created 5,000 tags")

        # Create products (500K - outlier)
        products = []
        for i in range(500_000):
            name = f"{fake.word().capitalize()} {fake.word().capitalize()} {fake.word()}"
            products.append(
                Product(
                    name=name[:300],
                    slug=slugify(name)[:250] + f"-{i}",
                    sku=f"SKU-{i:07d}",
                    description=fake.paragraph(nb_sentences=5),
                    short_description=fake.sentence(),
                    category_id=random.choice(category_ids),
                    price=Decimal(str(random.uniform(10, 1000))),
                    cost=Decimal(str(random.uniform(5, 500))),
                    weight=Decimal(str(random.uniform(0.1, 50))),
                    is_active=random.random() > 0.1,
                    is_featured=random.random() > 0.9,
                    stock_quantity=random.randint(0, 1000),
                )
            )
            if (i + 1) % self.chunk_size == 0:
                Product.objects.bulk_create(products)
                self.stdout.write(f"  Created {i + 1:,} products...")
                products = []
        if products:
            Product.objects.bulk_create(products)
        self.stdout.write("  Created 500,000 products")

        product_ids = list(Product.objects.values_list("id", flat=True))

        # Create product-tag relationships (M2M)
        self.stdout.write("  Creating product-tag relationships...")
        products_with_tags = Product.objects.all()[:100_000]  # Limit for performance
        for i, product in enumerate(products_with_tags):
            tags_for_product = random.sample(tag_ids, k=random.randint(1, 5))
            product.tags.set(tags_for_product)
            if (i + 1) % 5000 == 0:
                self.stdout.write(f"    Linked {i + 1:,} products to tags...")

        # Create product images (1M)
        images = []
        for i, product_id in enumerate(random.choices(product_ids, k=1_000_000)):
            images.append(
                ProductImage(
                    product_id=product_id,
                    image_url=fake.image_url(),
                    alt_text=fake.sentence(nb_words=5),
                    caption=fake.sentence() if random.random() > 0.5 else "",
                    is_primary=(i % 3 == 0),
                    display_order=random.randint(0, 10),
                )
            )
            if len(images) >= self.chunk_size:
                ProductImage.objects.bulk_create(images)
                images = []
        if images:
            ProductImage.objects.bulk_create(images)
        self.stdout.write("  Created 1,000,000 product images")

        # Create product variants (1.5M)
        variants = []
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        colors = ["Red", "Blue", "Green", "Black", "White", "Yellow"]
        materials = ["Cotton", "Polyester", "Wool", "Silk", "Denim"]
        for i in range(1_500_000):
            size = random.choice(sizes)
            color = random.choice(colors)
            variants.append(
                ProductVariant(
                    product_id=random.choice(product_ids),
                    sku=f"VAR-{i:07d}",
                    variant_name=f"{size} / {color}",
                    size=size,
                    color=color,
                    material=random.choice(materials) if random.random() > 0.5 else "",
                    price_adjustment=Decimal(str(random.uniform(-50, 50))),
                    stock_quantity=random.randint(0, 500),
                    is_active=random.random() > 0.1,
                )
            )
            if (i + 1) % self.chunk_size == 0:
                ProductVariant.objects.bulk_create(variants)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} product variants...")
                variants = []
        if variants:
            ProductVariant.objects.bulk_create(variants)
        self.stdout.write("  Created 1,500,000 product variants")

    def create_orders(self):
        """Create 300K orders with items, shipping, invoices, and refunds."""
        self.stdout.write("\n[3/7] Creating orders and related data...")

        user_ids = list(User.objects.values_list("id", flat=True))
        product_ids = list(Product.objects.values_list("id", flat=True))
        address_ids = list(Address.objects.values_list("id", flat=True))
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled", "refunded"]

        # Create orders (300K)
        orders = []
        for i in range(300_000):
            orders.append(
                Order(
                    order_number=f"ORD-{i:07d}",
                    user_id=random.choice(user_ids),
                    status=random.choice(statuses),
                    subtotal=Decimal(str(random.uniform(10, 5000))),
                    tax=Decimal(str(random.uniform(1, 500))),
                    shipping_cost=Decimal(str(random.uniform(5, 50))),
                    total=Decimal(str(random.uniform(20, 5500))),
                    notes=fake.sentence() if random.random() > 0.7 else "",
                )
            )
            if (i + 1) % self.chunk_size == 0:
                Order.objects.bulk_create(orders)
                if (i + 1) % 50_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} orders...")
                orders = []
        if orders:
            Order.objects.bulk_create(orders)
        self.stdout.write("  Created 300,000 orders")

        order_ids = list(Order.objects.values_list("id", flat=True))

        # Create order items (800K)
        order_items = []
        for i in range(800_000):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 10)
            unit_price = Decimal(str(random.uniform(10, 500)))
            order_items.append(
                OrderItem(
                    order_id=random.choice(order_ids),
                    product_id=product_id,
                    product_name=f"Product {product_id}",
                    sku=f"SKU-{product_id:07d}",
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=unit_price * quantity,
                    item_notes=fake.sentence() if random.random() > 0.8 else "",
                )
            )
            if (i + 1) % self.chunk_size == 0:
                OrderItem.objects.bulk_create(order_items)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} order items...")
                order_items = []
        if order_items:
            OrderItem.objects.bulk_create(order_items)
        self.stdout.write("  Created 800,000 order items")

        # Create shipping addresses (300K - one per order)
        shipping_addresses = []
        for order_id in order_ids:
            shipping_addresses.append(
                ShippingAddress(
                    order_id=order_id,
                    address_id=random.choice(address_ids) if random.random() > 0.3 else None,
                    recipient_name=fake.name(),
                    recipient_phone=fake.phone_number()[:20],
                    full_address=fake.address(),
                    street_address=fake.street_address(),
                    city=fake.city(),
                    state=fake.state(),
                    postal_code=fake.postcode(),
                    country=fake.country(),
                    delivery_instructions=fake.sentence() if random.random() > 0.7 else "",
                )
            )
            if len(shipping_addresses) >= self.chunk_size:
                ShippingAddress.objects.bulk_create(shipping_addresses)
                shipping_addresses = []
        if shipping_addresses:
            ShippingAddress.objects.bulk_create(shipping_addresses)
        self.stdout.write("  Created 300,000 shipping addresses")

        # Create invoices (250K - not all orders have invoices)
        invoices = []
        selected_orders = random.sample(order_ids, k=250_000)
        for i, order_id in enumerate(selected_orders):
            invoices.append(
                Invoice(
                    order_id=order_id,
                    invoice_number=f"INV-{i:07d}",
                    amount=Decimal(str(random.uniform(20, 5500))),
                    is_paid=random.random() > 0.3,
                    notes=fake.sentence() if random.random() > 0.8 else "",
                )
            )
            if len(invoices) >= self.chunk_size:
                Invoice.objects.bulk_create(invoices)
                invoices = []
        if invoices:
            Invoice.objects.bulk_create(invoices)
        self.stdout.write("  Created 250,000 invoices")

        # Create refunds (50K)
        refunds = []
        refund_statuses = ["requested", "approved", "rejected", "processed"]
        for i in range(50_000):
            refunds.append(
                Refund(
                    order_id=random.choice(order_ids),
                    refund_number=f"REF-{i:07d}",
                    status=random.choice(refund_statuses),
                    amount=Decimal(str(random.uniform(10, 1000))),
                    reason=fake.paragraph(nb_sentences=2),
                    notes=fake.sentence() if random.random() > 0.7 else "",
                )
            )
            if len(refunds) >= self.chunk_size:
                Refund.objects.bulk_create(refunds)
                refunds = []
        if refunds:
            Refund.objects.bulk_create(refunds)
        self.stdout.write("  Created 50,000 refunds")

    def create_inventory(self):
        """Create 200K inventory stock with warehouses, suppliers, and movements."""
        self.stdout.write("\n[4/7] Creating inventory and related data...")

        # Create warehouses (100)
        warehouses = []
        for i in range(100):
            warehouses.append(
                Warehouse(
                    name=f"Warehouse {fake.city()}",
                    code=f"WH-{i:03d}",
                    location_address=fake.address(),
                    city=fake.city(),
                    country=fake.country(),
                    capacity=random.randint(10_000, 100_000),
                    manager_name=fake.name(),
                    phone_number=fake.phone_number()[:20],
                    is_active=random.random() > 0.1,
                )
            )
        Warehouse.objects.bulk_create(warehouses)
        warehouse_ids = list(Warehouse.objects.values_list("id", flat=True))
        self.stdout.write("  Created 100 warehouses")

        # Create suppliers (2000)
        suppliers = []
        for i in range(2000):
            suppliers.append(
                Supplier(
                    name=fake.name(),
                    company_name=fake.company(),
                    contact_person=fake.name(),
                    email=fake.company_email(),
                    phone_number=fake.phone_number()[:20],
                    address=fake.address() if random.random() > 0.3 else "",
                    city=fake.city() if random.random() > 0.3 else "",
                    country=fake.country() if random.random() > 0.3 else "",
                    website=fake.url() if random.random() > 0.5 else "",
                    notes=fake.paragraph() if random.random() > 0.7 else "",
                    is_active=random.random() > 0.1,
                )
            )
        Supplier.objects.bulk_create(suppliers)
        supplier_ids = list(Supplier.objects.values_list("id", flat=True))
        self.stdout.write("  Created 2,000 suppliers")

        product_ids = list(Product.objects.values_list("id", flat=True))

        # Create stock (200K)
        stocks = []
        for i in range(200_000):
            quantity = random.randint(0, 1000)
            reserved = random.randint(0, min(quantity, 100))
            stocks.append(
                Stock(
                    product_id=random.choice(product_ids),
                    warehouse_id=random.choice(warehouse_ids),
                    quantity=quantity,
                    reserved_quantity=reserved,
                    available_quantity=quantity - reserved,
                    reorder_level=random.randint(5, 50),
                    notes=fake.sentence() if random.random() > 0.8 else "",
                )
            )
            if (i + 1) % self.chunk_size == 0:
                Stock.objects.bulk_create(stocks, ignore_conflicts=True)
                if (i + 1) % 50_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} stock records...")
                stocks = []
        if stocks:
            Stock.objects.bulk_create(stocks, ignore_conflicts=True)
        self.stdout.write("  Created 200,000 stock records")

        stock_ids = list(Stock.objects.values_list("id", flat=True))
        user_ids = list(User.objects.values_list("id", flat=True))

        # Create stock movements (500K)
        movements = []
        movement_types = ["in", "out", "transfer", "adjustment", "return"]
        for i in range(500_000):
            movements.append(
                StockMovement(
                    stock_id=random.choice(stock_ids),
                    movement_type=random.choice(movement_types),
                    quantity=random.randint(-100, 100),
                    reference_number=f"REF-{i:07d}" if random.random() > 0.5 else "",
                    notes=fake.sentence() if random.random() > 0.7 else "",
                    performed_by_id=random.choice(user_ids) if random.random() > 0.3 else None,
                )
            )
            if (i + 1) % self.chunk_size == 0:
                StockMovement.objects.bulk_create(movements)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} stock movements...")
                movements = []
        if movements:
            StockMovement.objects.bulk_create(movements)
        self.stdout.write("  Created 500,000 stock movements")

        # Create purchase orders (100K)
        pos = []
        po_statuses = ["draft", "sent", "confirmed", "received", "cancelled"]
        for i in range(100_000):
            pos.append(
                PurchaseOrder(
                    po_number=f"PO-{i:07d}",
                    supplier_id=random.choice(supplier_ids),
                    warehouse_id=random.choice(warehouse_ids),
                    status=random.choice(po_statuses),
                    total_amount=Decimal(str(random.uniform(100, 50000))),
                    notes=fake.sentence() if random.random() > 0.7 else "",
                )
            )
            if (i + 1) % self.chunk_size == 0:
                PurchaseOrder.objects.bulk_create(pos)
                if (i + 1) % 50_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} purchase orders...")
                pos = []
        if pos:
            PurchaseOrder.objects.bulk_create(pos)
        self.stdout.write("  Created 100,000 purchase orders")

        po_ids = list(PurchaseOrder.objects.values_list("id", flat=True))

        # Create PO items (300K)
        po_items = []
        for i in range(300_000):
            quantity = random.randint(10, 1000)
            unit_price = Decimal(str(random.uniform(5, 500)))
            po_items.append(
                PurchaseOrderItem(
                    purchase_order_id=random.choice(po_ids),
                    product_id=random.choice(product_ids),
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=unit_price * quantity,
                    received_quantity=random.randint(0, quantity),
                    notes=fake.sentence() if random.random() > 0.8 else "",
                )
            )
            if (i + 1) % self.chunk_size == 0:
                PurchaseOrderItem.objects.bulk_create(po_items)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} PO items...")
                po_items = []
        if po_items:
            PurchaseOrderItem.objects.bulk_create(po_items)
        self.stdout.write("  Created 300,000 PO items")

    def create_content(self):
        """Create 100K content items (articles, blog posts, comments, media files)."""
        self.stdout.write("\n[5/7] Creating content and related data...")

        user_ids = list(User.objects.values_list("id", flat=True))
        statuses = ["draft", "published", "archived"]

        # Create articles (50K)
        articles = []
        for i in range(50_000):
            title = fake.sentence(nb_words=6)
            articles.append(
                Article(
                    title=title[:300],
                    slug=slugify(title)[:250] + f"-{i}",
                    summary=fake.sentence(nb_words=15),
                    content=fake.paragraph(nb_sentences=10),
                    author_id=random.choice(user_ids),
                    status=random.choice(statuses),
                    view_count=random.randint(0, 10000),
                    is_featured=random.random() > 0.9,
                )
            )
            if (i + 1) % self.chunk_size == 0:
                Article.objects.bulk_create(articles)
                if (i + 1) % 10_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} articles...")
                articles = []
        if articles:
            Article.objects.bulk_create(articles)
        self.stdout.write("  Created 50,000 articles")

        # Create blog posts (50K)
        blog_posts = []
        for i in range(50_000):
            title = fake.sentence(nb_words=6)
            blog_posts.append(
                BlogPost(
                    title=title[:300],
                    slug=slugify(title)[:250] + f"-blog-{i}",
                    excerpt=fake.sentence(nb_words=15),
                    content=fake.paragraph(nb_sentences=10),
                    author_id=random.choice(user_ids),
                    status=random.choice(statuses),
                    view_count=random.randint(0, 10000),
                    comment_count=random.randint(0, 500),
                )
            )
            if (i + 1) % self.chunk_size == 0:
                BlogPost.objects.bulk_create(blog_posts)
                if (i + 1) % 10_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} blog posts...")
                blog_posts = []
        if blog_posts:
            BlogPost.objects.bulk_create(blog_posts)
        self.stdout.write("  Created 50,000 blog posts")

        # Get content types for generic relations
        article_ct = ContentType.objects.get_for_model(Article)
        blogpost_ct = ContentType.objects.get_for_model(BlogPost)
        article_ids = list(Article.objects.values_list("id", flat=True))
        blogpost_ids = list(BlogPost.objects.values_list("id", flat=True))

        # Create comments (300K)
        comments = []
        for i in range(300_000):
            # Randomly assign to article or blog post
            if random.random() > 0.5:
                content_type = article_ct
                object_id = random.choice(article_ids)
            else:
                content_type = blogpost_ct
                object_id = random.choice(blogpost_ids)

            comments.append(
                Comment(
                    user_id=random.choice(user_ids),
                    author_name=fake.name(),
                    author_email=fake.email() if random.random() > 0.5 else "",
                    comment_text=fake.paragraph(nb_sentences=3),
                    is_approved=random.random() > 0.2,
                    is_spam=random.random() > 0.9,
                    content_type=content_type,
                    object_id=object_id,
                )
            )
            if (i + 1) % self.chunk_size == 0:
                Comment.objects.bulk_create(comments)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} comments...")
                comments = []
        if comments:
            Comment.objects.bulk_create(comments)
        self.stdout.write("  Created 300,000 comments")

        # Create media files (100K)
        media_files = []
        file_types = ["image", "video", "audio", "document"]
        for i in range(100_000):
            media_files.append(
                MediaFile(
                    title=fake.sentence(nb_words=4),
                    description=fake.paragraph() if random.random() > 0.5 else "",
                    filename=fake.file_name(),
                    file_url=fake.url(),
                    file_type=random.choice(file_types),
                    file_size=random.randint(1024, 10_485_760),  # 1KB to 10MB
                    mime_type=fake.mime_type(),
                    uploaded_by_id=random.choice(user_ids) if random.random() > 0.1 else None,
                )
            )
            if (i + 1) % self.chunk_size == 0:
                MediaFile.objects.bulk_create(media_files)
                if (i + 1) % 50_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} media files...")
                media_files = []
        if media_files:
            MediaFile.objects.bulk_create(media_files)
        self.stdout.write("  Created 100,000 media files")

    def create_support(self):
        """Create 50K support tickets with messages, FAQs, and KB articles."""
        self.stdout.write("\n[6/7] Creating support and related data...")

        # Create ticket categories (50)
        categories = []
        for i in range(50):
            name = f"{fake.word().capitalize()} Support"
            categories.append(
                TicketCategory(
                    name=name,
                    slug=slugify(name) + f"-{i}",
                    description=fake.paragraph(),
                    is_active=random.random() > 0.1,
                )
            )
        TicketCategory.objects.bulk_create(categories)
        category_ids = list(TicketCategory.objects.values_list("id", flat=True))
        self.stdout.write("  Created 50 ticket categories")

        user_ids = list(User.objects.values_list("id", flat=True))
        ticket_statuses = ["open", "in_progress", "waiting_customer", "resolved", "closed"]
        priorities = ["low", "medium", "high", "urgent"]

        # Create tickets (50K)
        tickets = []
        for i in range(50_000):
            tickets.append(
                Ticket(
                    ticket_number=f"TKT-{i:07d}",
                    user_id=random.choice(user_ids),
                    category_id=random.choice(category_ids) if random.random() > 0.2 else None,
                    assigned_to_id=random.choice(user_ids) if random.random() > 0.5 else None,
                    subject=fake.sentence(nb_words=8),
                    description=fake.paragraph(nb_sentences=5),
                    status=random.choice(ticket_statuses),
                    priority=random.choice(priorities),
                )
            )
            if (i + 1) % self.chunk_size == 0:
                Ticket.objects.bulk_create(tickets)
                if (i + 1) % 10_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} tickets...")
                tickets = []
        if tickets:
            Ticket.objects.bulk_create(tickets)
        self.stdout.write("  Created 50,000 tickets")

        ticket_ids = list(Ticket.objects.values_list("id", flat=True))

        # Create ticket messages (200K)
        messages = []
        for i in range(200_000):
            messages.append(
                TicketMessage(
                    ticket_id=random.choice(ticket_ids),
                    user_id=random.choice(user_ids),
                    message_text=fake.paragraph(nb_sentences=4),
                    is_staff_reply=random.random() > 0.5,
                    is_internal_note=random.random() > 0.8,
                )
            )
            if (i + 1) % self.chunk_size == 0:
                TicketMessage.objects.bulk_create(messages)
                if (i + 1) % 50_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} ticket messages...")
                messages = []
        if messages:
            TicketMessage.objects.bulk_create(messages)
        self.stdout.write("  Created 200,000 ticket messages")

        # Create FAQs (1000)
        faqs = []
        for i in range(1000):
            faqs.append(
                FAQ(
                    category_id=random.choice(category_ids) if random.random() > 0.3 else None,
                    question=fake.sentence(nb_words=8) + "?",
                    answer=fake.paragraph(nb_sentences=4),
                    display_order=i,
                    view_count=random.randint(0, 10000),
                    is_published=random.random() > 0.1,
                )
            )
        FAQ.objects.bulk_create(faqs)
        self.stdout.write("  Created 1,000 FAQs")

        # Create knowledge base articles (5000)
        kb_articles = []
        kb_statuses = ["draft", "published", "archived"]
        for i in range(5000):
            title = fake.sentence(nb_words=6)
            kb_articles.append(
                KnowledgeBaseArticle(
                    category_id=random.choice(category_ids) if random.random() > 0.2 else None,
                    title=title[:300],
                    slug=slugify(title)[:250] + f"-kb-{i}",
                    content=fake.paragraph(nb_sentences=15),
                    summary=fake.sentence(nb_words=15),
                    author_id=random.choice(user_ids) if random.random() > 0.1 else None,
                    status=random.choice(kb_statuses),
                    view_count=random.randint(0, 50000),
                    helpful_count=random.randint(0, 5000),
                )
            )
        KnowledgeBaseArticle.objects.bulk_create(kb_articles)
        self.stdout.write("  Created 5,000 knowledge base articles")

    def create_analytics(self):
        """Create 1M analytics events (outlier) with page views, conversions, and sessions."""
        self.stdout.write("\n[7/7] Creating analytics data (1M events - outlier)...")

        user_ids = list(User.objects.values_list("id", flat=True))
        event_types = [
            "page_view",
            "click",
            "form_submit",
            "purchase",
            "signup",
            "login",
            "logout",
            "search",
            "download",
            "share",
        ]
        device_types = ["mobile", "desktop", "tablet"]
        browsers = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
        oses = ["Windows", "macOS", "Linux", "iOS", "Android"]
        countries = [
            "USA",
            "UK",
            "Canada",
            "Australia",
            "Germany",
            "France",
            "Japan",
            "South Korea",
        ]

        # Create events (1M - outlier with searchable text)
        events = []
        for i in range(1_000_000):
            events.append(
                Event(
                    user_id=random.choice(user_ids) if random.random() > 0.3 else None,
                    session_id=str(uuid.uuid4()),
                    event_type=random.choice(event_types),
                    event_name=fake.sentence(nb_words=3),  # Searchable
                    event_description=fake.paragraph(nb_sentences=2)
                    if random.random() > 0.5
                    else "",  # Searchable
                    user_agent=fake.user_agent(),  # Searchable
                    referrer_url=fake.url() if random.random() > 0.5 else "",  # Searchable
                    ip_address=fake.ipv4(),
                    device_type=random.choice(device_types),
                    browser_name=random.choice(browsers),
                    os_name=random.choice(oses),
                    country=random.choice(countries),
                    city=fake.city(),
                )
            )
            if (i + 1) % self.chunk_size == 0:
                Event.objects.bulk_create(events)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} events...")
                events = []
        if events:
            Event.objects.bulk_create(events)
        self.stdout.write("  Created 1,000,000 events")

        event_ids = list(Event.objects.values_list("id", flat=True))

        # Create page views (subset of events - random 300K)
        page_views = []
        selected_event_ids = random.sample(event_ids, k=min(300_000, len(event_ids)))
        for i, event_id in enumerate(selected_event_ids):
            page_views.append(
                PageView(
                    event_id=event_id,
                    page_url=fake.url(),  # Searchable
                    page_title=fake.sentence(nb_words=5),  # Searchable
                    page_description=fake.paragraph()
                    if random.random() > 0.5
                    else "",  # Searchable
                    page_path=f"/{fake.uri_path()}",
                    query_string=f"?param={fake.word()}" if random.random() > 0.5 else "",
                    time_on_page=random.randint(0, 600),
                    scroll_depth=random.randint(0, 100),
                )
            )
            if (i + 1) % self.chunk_size == 0:
                PageView.objects.bulk_create(page_views)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} page views...")
                page_views = []
        if page_views:
            PageView.objects.bulk_create(page_views)
        self.stdout.write("  Created 300,000 page views")

        # Create conversions (500K)
        conversions = []
        conversion_types = [
            "signup",
            "purchase",
            "subscribe",
            "download",
            "contact",
            "trial",
            "upgrade",
        ]
        campaign_sources = ["google", "facebook", "twitter", "linkedin", "email", "direct"]
        campaign_mediums = ["cpc", "cpm", "email", "social", "organic"]
        for i in range(500_000):
            conversions.append(
                Conversion(
                    user_id=random.choice(user_ids) if random.random() > 0.2 else None,
                    event_id=random.choice(event_ids) if random.random() > 0.7 else None,
                    conversion_type=random.choice(conversion_types),
                    conversion_description=fake.paragraph()
                    if random.random() > 0.5
                    else "",  # Searchable
                    campaign_name=fake.catch_phrase()
                    if random.random() > 0.3
                    else "",  # Searchable
                    campaign_source=random.choice(campaign_sources)
                    if random.random() > 0.3
                    else "",
                    campaign_medium=random.choice(campaign_mediums)
                    if random.random() > 0.3
                    else "",
                    conversion_value=Decimal(str(random.uniform(10, 1000)))
                    if random.random() > 0.5
                    else None,
                )
            )
            if (i + 1) % self.chunk_size == 0:
                Conversion.objects.bulk_create(conversions)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} conversions...")
                conversions = []
        if conversions:
            Conversion.objects.bulk_create(conversions)
        self.stdout.write("  Created 500,000 conversions")

        # Create session data (1M)
        sessions = []
        for i in range(1_000_000):
            sessions.append(
                SessionData(
                    session_id=str(uuid.uuid4()),
                    user_id=random.choice(user_ids) if random.random() > 0.3 else None,
                    device_info=f"{random.choice(device_types)} - {fake.user_agent()}",  # Searchable
                    browser_info=f"{random.choice(browsers)} {random.randint(80, 120)}.0 on {random.choice(oses)}",  # Searchable
                    screen_resolution=f"{random.choice(['1920x1080', '1366x768', '2560x1440', '3840x2160'])}",
                    language=random.choice(["en-US", "ko-KR", "ja-JP", "de-DE", "fr-FR"]),
                    timezone=random.choice(
                        ["America/New_York", "Europe/London", "Asia/Seoul", "Asia/Tokyo"]
                    ),
                    landing_page=fake.url() if random.random() > 0.3 else "",
                    exit_page=fake.url() if random.random() > 0.3 else "",
                    total_page_views=random.randint(1, 50),
                    total_events=random.randint(0, 100),
                    session_duration=random.randint(0, 3600),
                    is_bounce=random.random() > 0.6,
                )
            )
            if (i + 1) % self.chunk_size == 0:
                SessionData.objects.bulk_create(sessions)
                if (i + 1) % 100_000 == 0:
                    self.stdout.write(f"  Created {i + 1:,} sessions...")
                sessions = []
        if sessions:
            SessionData.objects.bulk_create(sessions)
        self.stdout.write("  Created 1,000,000 session data records")
