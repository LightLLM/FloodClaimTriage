"""Seed database with sample data for development and testing"""
import asyncio
from datetime import date, datetime

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.base import async_session_maker
from app.models import Event, Property, User


async def seed_users():
    """Create sample users with different roles"""
    async with async_session_maker() as session:
        # Check if users already exist
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Users already exist, skipping...")
            return

        users = [
            User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role="admin",
                is_active=True,
            ),
            User(
                email="analyst@example.com",
                hashed_password=get_password_hash("analyst123"),
                full_name="Jane Analyst",
                role="analyst",
                is_active=True,
            ),
            User(
                email="reviewer@example.com",
                hashed_password=get_password_hash("reviewer123"),
                full_name="Bob Reviewer",
                role="reviewer",
                is_active=True,
            ),
            User(
                email="viewer@example.com",
                hashed_password=get_password_hash("viewer123"),
                full_name="Alice Viewer",
                role="viewer",
                is_active=True,
            ),
        ]

        for user in users:
            session.add(user)

        await session.commit()
        print(f"Created {len(users)} users")


async def seed_events():
    """Create sample flood events"""
    async with async_session_maker() as session:
        # Check if events already exist
        result = await session.execute(select(Event).limit(1))
        if result.scalar_one_or_none():
            print("Events already exist, skipping...")
            return

        events = [
            Event(
                event_type="flood",
                name="Texas Flood August 2023",
                event_date=date(2023, 8, 15),
                stac_collection_id="sentinel2-floods-tx-2023",
                status="active",
            ),
            Event(
                event_type="flood",
                name="Florida Hurricane September 2023",
                event_date=date(2023, 9, 10),
                stac_collection_id="sentinel2-hurricane-fl-2023",
                status="active",
            ),
            Event(
                event_type="flood",
                name="California Atmospheric River January 2024",
                event_date=date(2024, 1, 5),
                stac_collection_id="sentinel2-atmospheric-river-ca-2024",
                status="draft",
            ),
        ]

        for event in events:
            session.add(event)

        await session.commit()
        print(f"Created {len(events)} events")


async def seed_properties():
    """Create sample properties"""
    async with async_session_maker() as session:
        # Check if properties already exist
        result = await session.execute(select(Property).limit(1))
        if result.scalar_one_or_none():
            print("Properties already exist, skipping...")
            return

        # Sample properties in Texas (Houston area)
        # Using WKB format for PostGIS Point geometry
        # Format: POINT(longitude latitude)
        properties = []
        
        # Generate 100 sample properties
        for i in range(100):
            # Distribute around Houston (-95.3698, 29.7604)
            lon = -95.3698 + (i % 10 - 5) * 0.1
            lat = 29.7604 + (i // 10 - 5) * 0.1
            
            # Simple WKB Point representation (this is a placeholder)
            # In production, use proper WKB encoding or GeoAlchemy2 functions
            geom_wkb = b"\\x01\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"
            
            prop = Property(
                external_property_id=f"PROP-{i+1:05d}",
                geometry=geom_wkb,
                address_hash=f"hash_{i}",
                building_type="residential" if i % 3 != 0 else "commercial",
                exposure_value=250000 + (i * 10000),
                region="TX",
                data_source="sample_portfolio",
            )
            properties.append(prop)

        for prop in properties:
            session.add(prop)

        await session.commit()
        print(f"Created {len(properties)} properties")


async def main():
    """Run all seed functions"""
    print("Starting database seeding...")
    print("-" * 50)

    await seed_users()
    await seed_events()
    await seed_properties()

    print("-" * 50)
    print("Database seeding complete!")
    print("\nSample login credentials:")
    print("  Admin:    admin@example.com / admin123")
    print("  Analyst:  analyst@example.com / analyst123")
    print("  Reviewer: reviewer@example.com / reviewer123")
    print("  Viewer:   viewer@example.com / viewer123")


if __name__ == "__main__":
    asyncio.run(main())
