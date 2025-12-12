import asyncio
import logging
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.vendor import Vendor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_vendor_codes():
    logger.info("Starting vendor code population...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Fetch all vendors
            result = await db.execute(select(Vendor))
            vendors = result.scalars().all()
            
            updated_count = 0
            
            for vendor in vendors:
                meta = vendor.metadata_ or {}
                current_code = meta.get("vendor_code")
                
                if not current_code:
                    # Generate code: V-{id:03d}
                    new_code = f"V-{vendor.id:03d}"
                    meta["vendor_code"] = new_code
                    vendor.metadata_ = meta
                    updated_count += 1
                    logger.info(f"Assigned code {new_code} to vendor {vendor.name} (ID: {vendor.id})")
            
            if updated_count > 0:
                await db.commit()
                logger.info(f"Successfully updated {updated_count} vendors with new codes.")
            else:
                logger.info("No vendors needed updates.")
                
        except Exception as e:
            logger.error(f"Error updating vendor codes: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(fix_vendor_codes())
