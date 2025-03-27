import os
import psycopg2
from faker import Faker
import uuid
from datetime import datetime
from slugify import slugify

# Connect using env variable from Heroku
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cursor = conn.cursor()

faker = Faker()

# Static values (IDs & image)
image_url = "https://storage.cloud.google.com/usenlease-media/category_images/1000027605.jpg"
address_id = "SJGY-3pOQFG2Y2Zw"
category_id = "Xzli15S8QhSErCBp"
owner_id = "RS_TW2-pTDy5Gols"

# Insert records
for _ in range(50):
    equipment_id = str(uuid.uuid4())[:16]
    name = faker.unique.word().capitalize() + " Equipment"
    slug = slugify(name + "-" + str(uuid.uuid4())[:4])
    description = faker.text(max_nb_chars=200)
    terms = faker.sentence(nb_words=8)
    hourly_rate = round(faker.pydecimal(left_digits=2, right_digits=2, positive=True), 2)
    available_quantity = faker.random_int(min=1, max=20)
    now = datetime.utcnow()

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

    image_id = str(uuid.uuid4())[:16]
    cursor.execute("""
        INSERT INTO equipment_management_image (
            id, image, equipment_id
        ) VALUES (%s, %s, %s)
    """, (
        image_id, image_url, equipment_id
    ))

conn.commit()
cursor.close()
conn.close()

print("✅ Inserted 50 equipment records with images.")
