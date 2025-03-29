import os
import psycopg2
import random
from faker import Faker
import uuid
from datetime import datetime, timezone
from slugify import slugify

# Connect to database
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cursor = conn.cursor()

faker = Faker()

# 🖼️ Image-to-tag mapping
image_tag_map = {
    "equipment_images/bugga.jpeg": "Buggy",
    "equipment_images/car.jpg": "Car",
    "equipment_images/bike_b.jpeg": "Bike",
    "equipment_images/bmw-latest.jpg": "BMW",
    "equipment_images/Contemporary-kitchen-with-stools-e1513286268248.jpg": "Kitchen"
}

# Convert keys to list for random selection
image_pool = list(image_tag_map.keys())

# Static foreign keys
address_id = "SJGY-3pOQFG2Y2Zw"
category_id = "Xzli15S8QhSErCBp"
owner_id = "RS_TW2-pTDy5Gols"

# 🏷️ Ensure all tags exist and get their IDs
tag_id_map = {}
for tag_name in set(image_tag_map.values()):
    # Check if tag already exists
    cursor.execute("SELECT id FROM equipment_management_tag WHERE name = %s", (tag_name,))
    row = cursor.fetchone()

    if row:
        tag_id = row[0]
    else:
        # Create new tag
        tag_id = str(uuid.uuid4())[:16]
        cursor.execute("INSERT INTO equipment_management_tag (id, name) VALUES (%s, %s)", (tag_id, tag_name))

    tag_id_map[tag_name] = tag_id

# 🔁 Insert 10,000 equipment records
for _ in range(10000):
    equipment_id = str(uuid.uuid4())[:16]

    base_name = faker.word().capitalize() + " Equipment"
    name = base_name + " " + str(uuid.uuid4())[:4]
    slug = slugify(name)

    description = faker.text(max_nb_chars=200)
    terms = faker.sentence(nb_words=8)
    hourly_rate = round(faker.pydecimal(left_digits=2, right_digits=2, positive=True), 2)
    available_quantity = faker.random_int(min=1, max=20)
    now = datetime.now(timezone.utc)

    # Insert equipment
    cursor.execute("""
        INSERT INTO equipment_management_equipment (
            id, name, description, hourly_rate, available_quantity,
            is_available, date_created, date_updated, terms, slug,
            address_id, category_id, owner_id, is_featured, is_trending, is_verified
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        equipment_id, name, description, hourly_rate, available_quantity,
        True, now, now, terms, slug,
        address_id, category_id, owner_id, False, False, True
    ))

    # Pick random image and tag
    image_path = random.choice(image_pool)
    tag_name = image_tag_map[image_path]
    tag_id = tag_id_map[tag_name]

    # Insert image
    image_id = str(uuid.uuid4())[:16]
    cursor.execute("""
        INSERT INTO equipment_management_image (
            id, image, equipment_id, is_pickup, is_return
        ) VALUES (%s, %s, %s, %s, %s)
    """, (
        image_id, image_path, equipment_id, False, False
    ))

    # Insert equipment-tag relationship (let DB handle ID)
    cursor.execute("""
        INSERT INTO equipment_management_equipment_tags (
            equipment_id, tag_id
        ) VALUES (%s, %s)
    """, (
        equipment_id, tag_id
    ))

# Finalize
conn.commit()
cursor.close()
conn.close()

print("✅ Inserted 10,000 equipment records with tagged images.")
