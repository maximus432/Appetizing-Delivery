import sqlite3
import hashlib
import os

DB_NAME = 'delivery.db'  # Убедись, что это имя совпадает с твоей базой данных

def get_connection():
    """Возвращает подключение к базе данных"""
    return sqlite3.connect(DB_NAME)

def hash_password(password):
    """Хеширование пароля через SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Создание таблиц и автоматическое наполнение базы данных вкусными блюдами и клиентами"""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            PasswordHash TEXT NOT NULL,
            FullName TEXT NOT NULL,
            Email TEXT,
            Phone TEXT,
            Address TEXT,
            Role TEXT NOT NULL CHECK(Role IN ('admin', 'client')),
            IsActive INTEGER DEFAULT 1
        )
    ''')

    # 2. Создаем таблицу блюд (меню)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Dishes (
            DishID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Description TEXT,
            Price REAL NOT NULL,
            Category TEXT NOT NULL,
            IsAvailable INTEGER DEFAULT 1
        )
    ''')

    # 3. Создаем таблицу заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            DeliveryAddress TEXT NOT NULL,
            Status TEXT NOT NULL DEFAULT 'new',
            TotalAmount REAL NOT NULL,
            Comment TEXT,
            PaymentMethod TEXT,
            FOREIGN KEY (UserID) REFERENCES Users(UserID)
        )
    ''')

    # 4. Создаем таблицу позиций в заказе
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderItems (
            OrderItemID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER NOT NULL,
            DishID INTEGER NOT NULL,
            Quantity INTEGER NOT NULL,
            PriceAtMoment REAL NOT NULL,
            FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
            FOREIGN KEY (DishID) REFERENCES Dishes(DishID)
        )
    ''')

    # 5. Создаем таблицу логов безопасности
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ActivityLog (
            LogID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            ActionType TEXT NOT NULL,
            Description TEXT NOT NULL,
            ActionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES Users(UserID)
        )
    ''')

    conn.commit()

    # --- АВТОМАТИЧЕСКОЕ НАПОЛНЕНИЕ (СЕЕМ ДАННЫЕ) ---
    
    # Проверяем, есть ли уже администратор в базе
    cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = 'admin'")
    if cursor.fetchone()[0] == 0:
        admin_pass = hash_password('admin123')
        cursor.execute('''
            INSERT INTO Users (Username, PasswordHash, FullName, Email, Phone, Address, Role, IsActive)
            VALUES ('admin', ?, 'Администратор Системы', 'admin@neonfood.ru', '+7 (900) 000-00-00', 'Офис доставки', 'admin', 1)
        ''', (admin_pass,))

    # Проверяем, добавлен ли ты (Балабан Максим)
    cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = 'maxim_balaban'")
    if cursor.fetchone()[0] == 0:
        client_pass = hash_password('client123')
        cursor.execute('''
            INSERT INTO Users (Username, PasswordHash, FullName, Email, Phone, Address, Role, IsActive)
            VALUES ('maxim_balaban', ?, 'Балабан Максим', 'maxim@delivery.ru', '+7 (999) 123-45-67', 'ул. Университетская, д. 12, кв. 34', 'client', 1)
        ''', (client_pass,))

    # Добавляем других реалистичных клиентов для массовости
    other_clients = [
        ('ivan_client', 'Иван Иванов', 'ivan@mail.ru', 'ул. Ленина, д. 10, кв. 45'),
        ('anna_delivery', 'Анна Смирнова', 'anna@yandex.ru', 'пр. Мира, д. 25, кв. 102'),
        ('dmitry_food', 'Дмитрий Петров', 'dima@gmail.com', 'ул. Пушкина, д. 4, кв. 12')
    ]
    for username, name, email, addr in other_clients:
        cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (username,))
        if cursor.fetchone()[0] == 0:
            client_pass = hash_password('client123')
            cursor.execute('''
                INSERT INTO Users (Username, PasswordHash, FullName, Email, Phone, Address, Role, IsActive)
                VALUES (?, ?, ?, ?, '+7 (999) 000-00-00', ?, 'client', 1)
            ''', (username, client_pass, name, email, addr))

    # Проверяем меню. Если оно пустое, загружаем все 12 аппетитных блюд
    cursor.execute("SELECT COUNT(*) FROM Dishes")
    if cursor.fetchone()[0] == 0:
        dishes = [
            # Пицца
            ('Пицца Пепперони', 'Сочные колбаски пепперони, много моцареллы, фирменный томатный соус и итальянские травы.', 580.00, 'Пицца', 1),
            ('Пицца Маргарита', 'Классическая пицца с сочными томатами, нежной моцареллой, соусом песто и базиликом.', 490.00, 'Пицца', 1),
            ('Пицца Четыре Сыра', 'Изысканное сочетание сыров: моцарелла, пармезан, горгонзола и чеддер на сливочной основе.', 640.00, 'Пицца', 1),
            
            # Горячее
            ('Паста Карбонара', 'Спагетти в нежном сливочном соусе с обжаренным беконом, яичным желтком и тертым пармезаном.', 450.00, 'Паста', 1),
            ('Борщ Домашний', 'Традиционный наваристый борщ на говяжьем бульоне со свеклой. Подается со сметаной и зеленью.', 320.00, 'Супы', 1),
            ('Грибной Крем-Суп', 'Нежный бархатистый крем-суп из свежих шампиньонов и белых грибов со сливками и сухариками.', 350.00, 'Супы', 1),
            
            # Салаты
            ('Салат Цезарь с курицей', 'Хрустящий салат романо, сочная куриная грудка гриль, черри, гренки и пармезан под соусом.', 390.00, 'Салаты', 1),
            ('Салат Греческий', 'Свежие огурцы, томаты, сладкий перец, маслины Каламата и нежный сыр Фета с оливковым маслом.', 340.00, 'Салаты', 1),
            
            # Десерты
            ('Тирамису', 'Классический итальянский десерт на основе сыра маскарпоне и печенья савоярди с кофейной пропиткой.', 290.00, 'Десерты', 1),
            ('Шоколадный Фондан', 'Горячий шоколадный кекс с хрустящей корочкой и жидкой тающей начинкой внутри.', 310.00, 'Десерты', 1),
            
            # Напитки
            ('Домашний Лимонад', 'Освежающий цитрусовый лимонад собственного приготовления с добавлением мяты и льда.', 180.00, 'Напитки', 1),
            ('Капучино', 'Классический кофейный напиток с нежной молочной пенкой из зерен свежей арабики.', 160.00, 'Напитки', 1)
        ]
        cursor.executemany('''
            INSERT INTO Dishes (Name, Description, Price, Category, IsAvailable)
            VALUES (?, ?, ?, ?, ?)
        ''', dishes)

    conn.commit()
    conn.close()

def verify_user(username, password):
    """Проверка логина и пароля"""
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT UserID, FullName, Role, IsActive FROM Users WHERE Username = ? AND PasswordHash = ?", (username, hashed))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        if row[3] == 0:
            return "blocked"
        return row[0], row[1], row[2]  # Возвращает UserID, FullName, Role
    return None

def log_action(user_id, action_type, description):
    """Запись действия в лог системы безопасности"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ActivityLog (UserID, ActionType, Description)
        VALUES (?, ?, ?)
    ''', (user_id, action_type, description))
    conn.commit()
    conn.close()

# Автоматически запускаем инициализацию при импорте модуля
init_db()