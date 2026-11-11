"""
Management command that seeds the database with sample tags and products.

Usage:
    python manage.py seed_products

Safe to run more than once: existing tags, categories and products are
matched by name and updated instead of duplicated.

Note: generated with AI assistance (Claude) - see README for attribution.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Category, Product, Tag

# (name, parent name or None)
CATEGORIES = [
    ("Electronics", None),
    ("Monitors", "Electronics"),
    ("Office essentials", None),
    ("Groceries", None),
    ("Personal care", None),
    ("Pet essentials", None),
]

TAGS = [
    "wireless", "waterproof", "eco-friendly", "bestseller", "on-sale", "premium",
    "budget", "portable", "handmade", "gift-idea", "smart", "durable",
]

# (name, category, price, tags, description)
PRODUCTS = [
    # Electronics
    ("Wireless Noise-Cancelling Headphones", "Electronics", "249.99",
     ["wireless", "premium", "bestseller"],
     "Over-ear headphones with active noise cancellation and a 30-hour rechargeable battery."),
    ("Portable Bluetooth Speaker", "Electronics", "59.99",
     ["wireless", "waterproof", "portable", "gift-idea"],
     "Compact rechargeable speaker, waterproof for pool and beach use."),
    ("Smartwatch Fitness Tracker", "Electronics", "129.00",
     ["smart", "waterproof", "portable", "gift-idea"],
     "Tracks heart rate, sleep and steps; water-resistant to 50 m."),
    ("20,000 mAh Power Bank", "Electronics", "34.99",
     ["portable", "budget", "durable"],
     "Rechargeable battery pack that charges two devices at once."),
    ("Smart Speaker with Voice Assistant", "Electronics", "89.00",
     ["smart", "wireless", "on-sale"],
     "Plays music and controls smart home devices by voice."),
    # Monitors
    ("27-inch 4K Monitor", "Monitors", "399.99",
     ["premium", "on-sale"],
     "IPS display with USB-C charging and a height-adjustable stand."),
    ("24-inch 1080p Monitor", "Monitors", "129.99",
     ["budget", "bestseller"],
     "Everyday display with slim bezels and HDMI input."),
    ("34-inch Ultrawide Curved Monitor", "Monitors", "549.00",
     ["premium"],
     "Curved display built for multitasking and gaming."),
    ("15.6-inch Portable USB-C Monitor", "Monitors", "179.00",
     ["portable"],
     "Lightweight second screen powered by a single USB-C cable."),
    # Office essentials
    ("Ergonomic Wireless Mouse", "Office essentials", "39.99",
     ["wireless", "bestseller"],
     "Contoured mouse with a rechargeable battery and silent clicks."),
    ("Stainless Steel Desk Organizer", "Office essentials", "24.50",
     ["durable", "budget"],
     "Mesh organizer with five compartments for pens and papers."),
    ("Recycled Paper Notebook Set", "Office essentials", "14.99",
     ["eco-friendly", "budget"],
     "Three A5 notebooks made from 100% recycled paper."),
    ("Adjustable Laptop Stand", "Office essentials", "45.00",
     [],
     "Aluminum stand that raises your screen to eye level."),
    # Groceries
    ("Organic Coffee Beans 1 kg", "Groceries", "22.99",
     ["eco-friendly", "bestseller"],
     "Medium-roast whole beans from certified organic farms."),
    ("Extra Virgin Olive Oil 1 L", "Groceries", "18.49",
     ["on-sale"],
     "Cold-pressed oil from Spanish olives."),
    ("Sourdough Bread Loaf", "Groceries", "7.50",
     ["handmade"],
     "Naturally leavened loaf baked fresh daily."),
    ("Wildflower Honey 500 g", "Groceries", "12.99",
     ["handmade", "gift-idea"],
     "Raw, unfiltered honey from local beekeepers."),
    # Personal care
    ("Bamboo Toothbrush 4-Pack", "Personal care", "9.99",
     ["eco-friendly", "budget"],
     "Biodegradable toothbrushes with soft bristles."),
    ("Rechargeable Electric Toothbrush", "Personal care", "79.99",
     ["smart", "waterproof"],
     "Pressure sensor and two-minute timer; safe to use in the shower."),
    ("Lavender Soap Bar", "Personal care", "6.50",
     ["handmade", "eco-friendly", "gift-idea"],
     "Cold-process soap with natural lavender oil."),
    ("Stainless Steel Safety Razor", "Personal care", "32.00",
     ["durable", "premium"],
     "Reusable razor that cuts down on plastic waste."),
    # Pet essentials
    ("Stainless Steel Pet Bowl Set", "Pet essentials", "19.99",
     ["durable", "budget"],
     "Non-slip bowls that are dishwasher safe."),
    ("Waterproof Dog Rain Jacket", "Pet essentials", "42.00",
     ["waterproof", "durable"],
     "Reflective jacket for walks in wet weather."),
    ("Automatic Pet Feeder", "Pet essentials", "99.99",
     ["smart", "on-sale"],
     "Schedules up to six meals a day with portion control."),
    ("Organic Dog Treats", "Pet essentials", "11.99",
     [],
     "Grain-free treats made with organic chicken."),
]


class Command(BaseCommand):
    help = "Seed the database with sample categories, tags and products."

    @transaction.atomic
    def handle(self, *args, **options):
        # Categories: parents are listed before children, so lookups succeed.
        categories = {}
        for name, parent_name in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                name=name,
                defaults={"parent": categories.get(parent_name)},
            )
            categories[name] = category

        tags = {name: Tag.objects.get_or_create(name=name)[0] for name in TAGS}

        created_count = 0
        for name, category_name, price, tag_names, description in PRODUCTS:
            product, created = Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": categories[category_name],
                    "price": Decimal(price),
                    "description": description,
                },
            )
            # set() replaces the product's tags with exactly this list.
            product.tags.set([tags[t] for t in tag_names])
            created_count += created

        self.stdout.write(self.style.SUCCESS(
            f"Done: {len(categories)} categories, {len(tags)} tags, "
            f"{len(PRODUCTS)} products ({created_count} new)."
        ))
