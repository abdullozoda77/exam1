from database import SessionLocal, engine, Base
from models import User, Category, Product, CartItem, Review, Favorite
from crud import create_order
from auth import hash_password

Base.metadata.create_all(bind=engine)

CATEGORIES = ['Phones', 'Laptops', 'Headphones', 'Watches', 'Accessories']

PRODUCTS = [
    ('iPhone 16', 'Apple smartphone, 128 GB', 999, 10, 'Phones'),
    ('Samsung Galaxy S24', 'Samsung smartphone, 256 GB', 899, 7, 'Phones'),
    ('Xiaomi Redmi Note 13', 'Cheap and good smartphone', 249, 25, 'Phones'),
    ('MacBook Air M3', '13 inch, 8 GB RAM, 256 GB', 1199, 4, 'Laptops'),
    ('Lenovo IdeaPad 5', '15 inch, 16 GB RAM, 512 GB', 749, 6, 'Laptops'),
    ('HP Laptop 15s', '15 inch, 8 GB RAM, 512 GB', 549, 0, 'Laptops'),
    ('AirPods Pro 2', 'Wireless headphones with noise cancelling', 249, 15, 'Headphones'),
    ('Sony WH-1000XM5', 'Over-ear wireless headphones', 399, 3, 'Headphones'),
    ('Apple Watch Series 10', 'Smart watch, 45 mm', 429, 8, 'Watches'),
    ('USB-C Charger 30W', 'Fast charger', 29, 40, 'Accessories'),
    ('Phone Case', 'Silicone case', 15, 2, 'Accessories'),
]

USERS = [
    ('Rustam Ahmadov', 'rustam', 'rustam@mail.tj', '+992 900 11 22 33'),
    ('Malika Yusupova', 'malika', 'malika@mail.tj', '+992 918 22 33 44'),
    ('Daler Sharipov', 'daler', 'daler@mail.tj', '+992 935 33 44 55'),
]

CARTS = [
    ('rustam@mail.tj', 'iPhone 16', 1),
    ('rustam@mail.tj', 'USB-C Charger 30W', 2),
    ('malika@mail.tj', 'MacBook Air M3', 1),
    ('malika@mail.tj', 'AirPods Pro 2', 1),
]

REVIEWS = [
    ('rustam@mail.tj', 'iPhone 16', 5, 'Very fast phone, great camera'),
    ('malika@mail.tj', 'MacBook Air M3', 5, 'Light and quiet, battery is amazing'),
    ('malika@mail.tj', 'AirPods Pro 2', 4, 'Good sound, a bit expensive'),
    ('daler@mail.tj', 'Phone Case', 2, 'Broke after one month'),
]

FAVORITES = [
    ('daler@mail.tj', 'Sony WH-1000XM5'),
    ('daler@mail.tj', 'Apple Watch Series 10'),
]


db = SessionLocal()

if db.query(Product).first():
    print('The database already has data, nothing added. Delete database.db to start again.')
else:
    categories = {}
    for name in CATEGORIES:
        categories[name] = Category(name=name)
        db.add(categories[name])
    db.commit()

    products = {}
    for name, description, price, stock, category in PRODUCTS:
        products[name] = Product(name=name, description=description, price=price, stock=stock,
                                 category_id=categories[category].id)
        db.add(products[name])
    db.commit()

    users = {}
    for name, username, email, phone in USERS:
        users[email] = User(name=name, username=username, email=email, phone=phone,
                            password_hash=hash_password('12345'))
        db.add(users[email])
    db.commit()

    for email, product, quantity in CARTS:
        db.add(CartItem(user_id=users[email].id, product_id=products[product].id, quantity=quantity))
    db.commit()

    create_order(db, users['rustam@mail.tj'].id)
    create_order(db, users['malika@mail.tj'].id)

    db.add(CartItem(user_id=users['rustam@mail.tj'].id, product_id=products['AirPods Pro 2'].id, quantity=1))

    for email, product, rating, text in REVIEWS:
        db.add(Review(user_id=users[email].id, product_id=products[product].id, rating=rating, text=text))

    for email, product in FAVORITES:
        db.add(Favorite(user_id=users[email].id, product_id=products[product].id))

    db.commit()
    print(f'Added: {len(CATEGORIES)} categories, {len(PRODUCTS)} products, {len(USERS)} users, '
          f'2 orders, {len(REVIEWS)} reviews, {len(FAVORITES)} favorites')

db.close()
