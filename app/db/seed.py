from app.db.models.user import User
from app.db.models.product import Product
from app.core.security import hash_password
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def create_default_admin():
    """
    Create a default admin user if it doesn't exist.
    Credentials are read from environment variables:
    - DEFAULT_ADMIN_EMAIL (default: admin@example.com)
    - DEFAULT_ADMIN_PASSWORD (default: admin123)
    - CREATE_DEFAULT_ADMIN (default: true)
    
    ⚠️  SECURITY: Change these defaults in production!
    """
    # Check if admin creation is disabled
    if not settings.create_default_admin:
        logger.info("Default admin creation disabled via CREATE_DEFAULT_ADMIN=false")
        return None
    
    try:
        # Get admin credentials from environment
        admin_email = settings.default_admin_email
        admin_password = settings.default_admin_password
        
        # Check if admin user already exists
        existing_admin = await User.find_one(User.email == admin_email)
        
        if existing_admin:
            logger.info(f"Admin user '{admin_email}' already exists. Skipping creation.")
            return existing_admin
        
        # Create new admin user
        admin_user = User(
            email=admin_email,
            hashed_password=hash_password(admin_password),
            role="admin"
        )
        await admin_user.insert()
        logger.info(f"✅ Default admin user created successfully: {admin_email}")
        
        # Security warning for default credentials
        if admin_email == "admin@example.com" or admin_password == "admin123":
            logger.warning("⚠️  SECURITY WARNING: Using default admin credentials!")
            logger.warning("⚠️  Please change the admin password immediately or set custom credentials via environment variables:")
            logger.warning("⚠️  - DEFAULT_ADMIN_EMAIL")
            logger.warning("⚠️  - DEFAULT_ADMIN_PASSWORD")
        
        return admin_user
        
    except Exception as e:
        logger.error(f"Failed to create default admin user: {e}")
        raise


async def seed_products():
    """
    Seed the database with 20 sample products.
    Only creates products if none exist.
    """
    try:
        # Check if products already exist
        existing_count = await Product.count()
        if existing_count > 0:
            logger.info(f"Products already exist ({existing_count} found). Skipping product seeding.")
            return
        
        logger.info("Creating 20 sample products...")
        
        sample_products = [
            # Electronics
            {
                "product_id": 1,
                "name": "Gaming Laptop Pro",
                "slug": "gaming-laptop-pro",
                "description": "High-performance gaming laptop with RTX 4080, 32GB RAM, and 1TB NVMe SSD",
                "price": 2499.99,
                "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500",
                "inventory": 15,
                "category": "Electronics",
                "is_active": True
            },
            {
                "product_id": 2,
                "name": "Wireless Noise-Cancelling Headphones",
                "slug": "wireless-noise-cancelling-headphones",
                "description": "Premium over-ear headphones with active noise cancellation and 30-hour battery",
                "price": 349.99,
                "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
                "inventory": 50,
                "category": "Electronics",
                "is_active": True
            },
            {
                "product_id": 3,
                "name": "4K Ultra HD Smart TV 55\"",
                "slug": "4k-ultra-hd-smart-tv-55",
                "description": "55-inch 4K Smart TV with HDR10+, Dolby Vision, and built-in streaming apps",
                "price": 899.99,
                "image": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500",
                "inventory": 25,
                "category": "Electronics",
                "is_active": True
            },
            {
                "product_id": 4,
                "name": "Mechanical Gaming Keyboard RGB",
                "slug": "mechanical-gaming-keyboard-rgb",
                "description": "Mechanical keyboard with Cherry MX switches and customizable RGB lighting",
                "price": 159.99,
                "image": "https://images.unsplash.com/photo-1595225476474-87563907a212?w=500",
                "inventory": 40,
                "category": "Electronics",
                "is_active": True
            },
            {
                "product_id": 5,
                "name": "Smartphone Pro Max 256GB",
                "slug": "smartphone-pro-max-256gb",
                "description": "Latest flagship smartphone with 256GB storage, 5G, and triple camera system",
                "price": 1199.99,
                "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
                "inventory": 30,
                "category": "Electronics",
                "is_active": True
            },
            
            # Fashion
            {
                "product_id": 6,
                "name": "Premium Leather Jacket",
                "slug": "premium-leather-jacket",
                "description": "Genuine leather jacket with quilted lining, perfect for all seasons",
                "price": 299.99,
                "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500",
                "inventory": 20,
                "category": "Fashion",
                "is_active": True
            },
            {
                "product_id": 7,
                "name": "Designer Sunglasses",
                "slug": "designer-sunglasses",
                "description": "Polarized designer sunglasses with UV400 protection and titanium frame",
                "price": 199.99,
                "image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500",
                "inventory": 60,
                "category": "Fashion",
                "is_active": True
            },
            {
                "product_id": 8,
                "name": "Running Shoes Ultra Boost",
                "slug": "running-shoes-ultra-boost",
                "description": "Premium running shoes with responsive cushioning and breathable mesh upper",
                "price": 179.99,
                "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
                "inventory": 45,
                "category": "Fashion",
                "is_active": True
            },
            {
                "product_id": 9,
                "name": "Casual Backpack 30L",
                "slug": "casual-backpack-30l",
                "description": "Durable water-resistant backpack with laptop compartment and USB charging port",
                "price": 79.99,
                "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500",
                "inventory": 55,
                "category": "Fashion",
                "is_active": True
            },
            {
                "product_id": 10,
                "name": "Luxury Watch Automatic",
                "slug": "luxury-watch-automatic",
                "description": "Swiss-made automatic watch with sapphire crystal and leather strap",
                "price": 1499.99,
                "image": "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=500",
                "inventory": 10,
                "category": "Fashion",
                "is_active": True
            },
            
            # Home & Living
            {
                "product_id": 11,
                "name": "Smart Coffee Maker",
                "slug": "smart-coffee-maker",
                "description": "WiFi-enabled coffee maker with app control and programmable brewing",
                "price": 149.99,
                "image": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500",
                "inventory": 35,
                "category": "Home & Living",
                "is_active": True
            },
            {
                "product_id": 12,
                "name": "Memory Foam Mattress Queen",
                "slug": "memory-foam-mattress-queen",
                "description": "Premium memory foam mattress with cooling gel and pressure relief",
                "price": 699.99,
                "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500",
                "inventory": 12,
                "category": "Home & Living",
                "is_active": True
            },
            {
                "product_id": 13,
                "name": "Robot Vacuum Cleaner",
                "slug": "robot-vacuum-cleaner",
                "description": "Smart robot vacuum with mapping, auto-charging, and app control",
                "price": 399.99,
                "image": "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500",
                "inventory": 28,
                "category": "Home & Living",
                "is_active": True
            },
            {
                "product_id": 14,
                "name": "Air Purifier HEPA",
                "slug": "air-purifier-hepa",
                "description": "HEPA air purifier with smart sensors and 3-stage filtration system",
                "price": 249.99,
                "image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500",
                "inventory": 22,
                "category": "Home & Living",
                "is_active": True
            },
            {
                "product_id": 15,
                "name": "Ergonomic Office Chair",
                "slug": "ergonomic-office-chair",
                "description": "Premium ergonomic chair with lumbar support and adjustable armrests",
                "price": 449.99,
                "image": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=500",
                "inventory": 18,
                "category": "Home & Living",
                "is_active": True
            },
            
            # Sports & Fitness
            {
                "product_id": 16,
                "name": "Yoga Mat Premium",
                "slug": "yoga-mat-premium",
                "description": "Extra-thick non-slip yoga mat with carrying strap and alignment lines",
                "price": 49.99,
                "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500",
                "inventory": 70,
                "category": "Sports & Fitness",
                "is_active": True
            },
            {
                "product_id": 17,
                "name": "Adjustable Dumbbell Set",
                "slug": "adjustable-dumbbell-set",
                "description": "Space-saving adjustable dumbbells from 5-52.5 lbs with quick-change dial",
                "price": 299.99,
                "image": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=500",
                "inventory": 15,
                "category": "Sports & Fitness",
                "is_active": True
            },
            {
                "product_id": 18,
                "name": "Fitness Tracker Smartband",
                "slug": "fitness-tracker-smartband",
                "description": "Water-resistant fitness tracker with heart rate monitor and sleep tracking",
                "price": 89.99,
                "image": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500",
                "inventory": 50,
                "category": "Sports & Fitness",
                "is_active": True
            },
            {
                "product_id": 19,
                "name": "Protein Powder Whey 5lbs",
                "slug": "protein-powder-whey-5lbs",
                "description": "Premium whey protein isolate with 25g protein per serving, chocolate flavor",
                "price": 59.99,
                "image": "https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?w=500",
                "inventory": 80,
                "category": "Sports & Fitness",
                "is_active": True
            },
            {
                "product_id": 20,
                "name": "Resistance Bands Set",
                "slug": "resistance-bands-set",
                "description": "Complete set of 5 resistance bands with handles, door anchor, and carry bag",
                "price": 34.99,
                "image": "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=500",
                "inventory": 65,
                "category": "Sports & Fitness",
                "is_active": True
            }
        ]
        
        # Insert all products
        products = [Product(**product_data) for product_data in sample_products]
        await Product.insert_many(products)
        
        logger.info(f"✅ Successfully created {len(products)} sample products")
        
        # Log categories summary
        categories = {}
        for product in sample_products:
            category = product["category"]
            categories[category] = categories.get(category, 0) + 1
        
        logger.info(f"Product categories: {categories}")
        
    except Exception as e:
        logger.error(f"Failed to seed products: {e}")
        # Don't raise - allow app to continue even if seeding fails
        

async def seed_database():
    """
    Seed the database with initial data.
    Creates default admin user and sample products.
    """
    logger.info("Starting database seeding...")
    await create_default_admin()
    await seed_products()
    logger.info("Database seeding completed.")
