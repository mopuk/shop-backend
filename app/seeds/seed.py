import argparse
import asyncio

from app.seeds.products_seed import reset_products, seed_products
from app.seeds.reference_seeds import reset_references, seed_references
from app.seeds.variants_seed import reset_variants, seed_variants


def parse_args():
    parser = argparse.ArgumentParser(description="Seed the database with initial data.")
    parser.add_argument(
        "--reset", action="store_true", help="Delete existing data before seeding"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete existing data without seeding",
    )
    return parser.parse_args()


async def main(reset: bool = False, delete: bool = False):
    if reset:
        await reset_variants()
        await reset_products()
        await reset_references()
    if delete:
        await reset_variants()
        await reset_products()
        await reset_references()
        return
    await seed_references()
    await seed_products()
    await seed_variants()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(reset=args.reset, delete=args.delete))
