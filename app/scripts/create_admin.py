"""
CLI script to manage admin users in the e-commerce application.

Usage:
    python -m app.scripts.create_admin
    python -m app.scripts.create_admin --email custom@example.com --password mypassword
"""
import asyncio
import argparse
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.db.models.user import User
from app.db.models.product import Product
from app.db.models.cart import Cart
from app.db.models.order import Order
from app.core.security import hash_password
from app.core.config import settings

async def create_admin_user(email: str, password: str):
    """Create or update an admin user."""
    # Initialize database connection
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[User, Product, Cart, Order])
    
    try:
        # Check if user already exists
        existing_user = await User.find_one(User.email == email)
        
        if existing_user:
            # Update existing user to admin with new password
            existing_user.role = "admin"
            existing_user.hashed_password = hash_password(password)
            await existing_user.save()
            print(f"✅ User '{email}' updated to admin role with new password.")
        else:
            # Create new admin user
            admin_user = User(
                email=email,
                hashed_password=hash_password(password),
                role="admin"
            )
            await admin_user.insert()
            print(f"✅ Admin user '{email}' created successfully.")
        
        print(f"\nAdmin Credentials:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"\n⚠️  Please keep these credentials secure!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description="Create or update an admin user")
    parser.add_argument(
        "--email",
        type=str,
        default="admin@example.com",
        help="Admin email (default: admin@example.com)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default="admin123",
        help="Admin password (default: admin123)"
    )
    
    args = parser.parse_args()
    
    print(f"Creating admin user: {args.email}")
    asyncio.run(create_admin_user(args.email, args.password))

if __name__ == "__main__":
    main()

