import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import db_helper
import random
import time

# Установка базового стиля
ctk.set_appearance_mode("dark")

# "Вкусная" цветовая палитра (Шоколад, Томат, Сыр, Сливки)
COLOR_BG_DARK = "#1E120F"      # Темно-кофейный (основной фон)
COLOR_CARD_BG = "#2B1B17"      # Насыщенный шоколадный (карточки и панели)
COLOR_TOMATO = "#E2583E"       # Аппетитный томатный (акценты, кнопки заказа)
COLOR_CHEESE = "#F39C12"       # Теплый сырный (цены, выделения)
COLOR_CREAM = "#F5E6D3"        # Сливочный цвет для второстепенного текста
COLOR_SUCCESS = "#27AE60"      # Зеленая петрушка (успех)

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🍕 ДОСТАВКА ЕДЫ — ВКУСНЫЙ ИНТЕРФЕЙС 🍔")
        self.geometry("1100x720")
        self.resizable(True, True)
        self.minsize(1000, 650)
        
        self.configure(fg_color=COLOR_BG_DARK)
        
        self.current_user_id = None
        self.current_user = None
        self.current_role = None
        
        # Корзина клиента
        self.cart = {}
        
        self.show_login_screen()

    def show_login_screen(self):
        self.clear_window()
        
        self.login_frame = ctk.CTkFrame(
            master=self, width=380, height=480, 
            corner_radius=20, fg_color=COLOR_CARD_BG,
            border_width=2, border_color=COLOR_TOMATO
        )
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        label_title = ctk.CTkLabel(
            master=self.login_frame, text="ПРИЯТНОГО АППЕТИТА!", 
            font=("Segoe UI", 24, "bold"), text_color=COLOR_TOMATO
        )
        label_title.pack(pady=(45, 5), padx=10)
        
        label_subtitle = ctk.CTkLabel(
            master=self.login_frame, text="Авторизация в службе доставки еды", 
            font=("Segoe UI", 12), text_color=COLOR_CREAM
        )
        label_subtitle.pack(pady=(0, 35))

        self.entry_login = ctk.CTkEntry(
            master=self.login_frame, width=280, 
            placeholder_text="Логин", height=48, corner_radius=12,
            fg_color="#120A08", border_color="#402B25", text_color="white"
        )
        self.entry_login.pack(pady=10)

        self.entry_password = ctk.CTkEntry(
            master=self.login_frame, width=280, 
            placeholder_text="Пароль", show="*", height=48, corner_radius=12,
            fg_color="#120A08", border_color="#402B25", text_color="white"
        )
        self.entry_password.pack(pady=10)

        btn_login = ctk.CTkButton(
            master=self.login_frame, text="ВОЙТИ И ЗАКАЗАТЬ ➔", 
            width=280, height=48, corner_radius=12, 
            font=("Segoe UI", 14, "bold"), fg_color=COLOR_TOMATO, hover_color="#C0392B",
            command=self.handle_login
        )
        btn_login.pack(pady=(35, 20))

    def handle_login(self):
        login = self.entry_login.get().strip()
        password = self.entry_password.get().strip()
        
        if not login or not password:
            messagebox.showwarning("Внимание", "Заполните все поля!")
            return
            
        user_data = db_helper.verify_user(login, password)
        
        if user_data == "blocked":
            messagebox.showerror("Доступ заблокирован", "Ваш аккаунт деактивирован!")
        elif user_data:
            self.current_user_id, self.current_user, self.current_role = user_data
            db_helper.log_action(self.current_user_id, "login", f"Пользователь {self.current_user} вошел в систему.")
            
            if self.current_role == "admin":
                self.show_admin_dashboard()
            else:
                self.show_client_dashboard()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    # ==================== ИНТЕРФЕЙС АДМИНИСТРАТОРА ====================
    
    def show_admin_dashboard(self):
        self.clear_window()
        
        # Левая панель меню (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_CARD_BG)
        self.sidebar.pack(side="left", fill="y")
        
        logo = ctk.CTkLabel(
            self.sidebar, text="🍅 НАСТРОЙКИ АДМИНА", 
            font=("Segoe UI", 16, "bold"), text_color=COLOR_TOMATO
        )
        logo.pack(pady=35, padx=20)
        
        self.btn_dishes = ctk.CTkButton(
            self.sidebar, text="🍔 Меню блюд", 
            anchor="w", height=45, corner_radius=10,
            fg_color="#3D2822", hover_color=COLOR_TOMATO, font=("Segoe UI", 12, "bold"),
            command=self.load_dishes_tab
        )
        self.btn_dishes.pack(pady=5, padx=15, fill="x")
        
        self.btn_orders = ctk.CTkButton(
            self.sidebar, text="📦 Заказы клиентов", 
            anchor="w", height=45, corner_radius=10,
            fg_color="transparent", hover_color=COLOR_TOMATO, font=("Segoe UI", 12, "bold"),
            command=self.load_orders_tab
        )
        self.btn_orders.pack(pady=5, padx=15, fill="x")

        self.btn_logs = ctk.CTkButton(
            self.sidebar, text="📋 Логи системы", 
            anchor="w", height=45, corner_radius=10,
            fg_color="transparent", hover_color=COLOR_TOMATO, font=("Segoe UI", 12, "bold"),
            command=self.load_logs_tab
        )
        self.btn_logs.pack(pady=5, padx=15, fill="x")
        
        btn_logout = ctk.CTkButton(
            self.sidebar, text="🚪 Выйти из панели", 
            fg_color="#A93226", hover_color="#7B241C", 
            height=38, corner_radius=10, font=("Segoe UI", 11, "bold"),
            command=self.show_login_screen
        )
        btn_logout.pack(side="bottom", pady=25, padx=15, fill="x")

        self.main_container = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_container.pack(side="right", fill="both", expand=True, padx=25, pady=25)
        
        self.load_dishes_tab()

    def load_dishes_tab(self):
        self.clear_container()
        self.set_active_button(self.btn_dishes)
        
        title = ctk.CTkLabel(self.main_container, text="Управление Меню Блюд", font=("Segoe UI", 24, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 20))
        
        actions_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 15))
        
        btn_add = ctk.CTkButton(
            actions_frame, text="+ Добавить блюдо в меню", 
            fg_color=COLOR_SUCCESS, hover_color="#1E8449",
            font=("Segoe UI", 13, "bold"), height=40, corner_radius=10,
            command=self.add_dish_dialog
        )
        btn_add.pack(side="left")

        # Аппетитный стиль таблиц
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLOR_CARD_BG, foreground="white", fieldbackground=COLOR_CARD_BG, rowheight=35, borderwidth=0)
        style.configure("Treeview.Heading", background=COLOR_TOMATO, foreground="white", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[('selected', COLOR_TOMATO)])

        columns = ("id", "name", "desc", "price", "category", "status")
        self.tree = ttk.Treeview(self.main_container, columns=columns, show="headings", style="Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название блюда")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("price", text="Стоимость")
        self.tree.heading("category", text="Категория")
        self.tree.heading("status", text="Доступность")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("desc", width=300, anchor="w")
        self.tree.column("price", width=110, anchor="center")
        self.tree.column("category", width=130, anchor="center")
        self.tree.column("status", width=110, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.refresh_dishes_table()

    def refresh_dishes_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = db_helper.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DishID, Name, Description, Price, Category, IsAvailable FROM Dishes")
        for row in cursor.fetchall():
            status = "🟢 Доступно" if row[5] == 1 else "🔴 Стоп-лист"
            self.tree.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:.2f} ₽", row[4], status))
        conn.close()

    def add_dish_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Новое блюдо")
        dialog.geometry("420x500")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLOR_CARD_BG)
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry(f"+{self.winfo_x() + 300}+{self.winfo_y() + 100}")

        lbl = ctk.CTkLabel(dialog, text="ДОБАВЛЕНИЕ БЛЮДА", font=("Segoe UI", 18, "bold"), text_color=COLOR_TOMATO)
        lbl.pack(pady=25)

        entry_name = ctk.CTkEntry(dialog, placeholder_text="Название блюда", width=320, height=42, fg_color="#120A08", border_color="#402B25")
        entry_name.pack(pady=10)

        entry_desc = ctk.CTkEntry(dialog, placeholder_text="Описание ингредиентов", width=320, height=42, fg_color="#120A08", border_color="#402B25")
        entry_desc.pack(pady=10)

        entry_price = ctk.CTkEntry(dialog, placeholder_text="Цена (руб.)", width=320, height=42, fg_color="#120A08", border_color="#402B25")
        entry_price.pack(pady=10)

        entry_category = ctk.CTkEntry(dialog, placeholder_text="Категория (Пицца, Суп)", width=320, height=42, fg_color="#120A08", border_color="#402B25")
        entry_category.pack(pady=10)

        def save():
            name = entry_name.get().strip()
            desc = entry_desc.get().strip()
            price_str = entry_price.get().strip()
            category = entry_category.get().strip()

            if not name or not price_str or not category:
                messagebox.showwarning("Внимание", "Заполните обязательные поля!")
                return

            try:
                price = float(price_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом!")
                return

            conn = db_helper.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Dishes (Name, Description, Price, Category, IsAvailable)
                VALUES (?, ?, ?, ?, 1)
            ''', (name, desc, price, category))
            conn.commit()
            conn.close()

            db_helper.log_action(self.current_user_id, "dish_created", f"Добавлено новое блюдо: '{name}'")

            dialog.destroy()
            self.refresh_dishes_table()
            messagebox.showinfo("Успех", f"Блюдо '{name}' добавлено!")

        btn_save = ctk.CTkButton(dialog, text="Сохранить", fg_color=COLOR_SUCCESS, hover_color="#1E8449", command=save, height=45, width=200, font=("Segoe UI", 13, "bold"))
        btn_save.pack(pady=30)

    def load_orders_tab(self):
        self.clear_container()
        self.set_active_button(self.btn_orders)

        title = ctk.CTkLabel(self.main_container, text="Заказы клиентов (Управление)", font=("Segoe UI", 24, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 20))

        control_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        control_frame.pack(fill="x", pady=(0, 15))

        btn_view_items = ctk.CTkButton(
            control_frame, text="🔍 Показать состав заказа", 
            fg_color=COLOR_TOMATO, hover_color="#C0392B",
            height=40, font=("Segoe UI", 12, "bold"),
            command=self.show_order_items
        )
        btn_view_items.pack(side="left", padx=(0, 15))

        self.status_combobox = ctk.CTkComboBox(
            control_frame, values=["new", "cooking", "delivering", "delivered", "cancelled"],
            width=160, height=40, font=("Segoe UI", 12)
        )
        self.status_combobox.pack(side="left", padx=(0, 15))
        self.status_combobox.set("new")

        btn_update_status = ctk.CTkButton(
            control_frame, text="⚡ Изменить статус", 
            fg_color=COLOR_CHEESE, hover_color="#D35400",
            height=40, font=("Segoe UI", 12, "bold"), text_color="black",
            command=self.update_order_status
        )
        btn_update_status.pack(side="left")

        columns = ("id", "client", "date", "address", "status", "amount", "payment", "comment")
        self.orders_tree = ttk.Treeview(self.main_container, columns=columns, show="headings", style="Treeview")
        
        self.orders_tree.heading("id", text="ID")
        self.orders_tree.heading("client", text="Клиент")
        self.orders_tree.heading("date", text="Дата")
        self.orders_tree.heading("address", text="Адрес доставки")
        self.orders_tree.heading("status", text="Статус")
        self.orders_tree.heading("amount", text="Сумма")
        self.orders_tree.heading("payment", text="Тип оплаты")
        self.orders_tree.heading("comment", text="Комментарий")

        self.orders_tree.column("id", width=50, anchor="center")
        self.orders_tree.column("client", width=140, anchor="w")
        self.orders_tree.column("date", width=130, anchor="center")
        self.orders_tree.column("address", width=170, anchor="w")
        self.orders_tree.column("status", width=90, anchor="center")
        self.orders_tree.column("amount", width=100, anchor="center")
        self.orders_tree.column("payment", width=110, anchor="center")
        self.orders_tree.column("comment", width=160, anchor="w")

        self.orders_tree.pack(fill="both", expand=True)
        self.refresh_orders_table()

    def refresh_orders_table(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        conn = db_helper.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.OrderID, u.FullName, o.OrderDate, o.DeliveryAddress, o.Status, o.TotalAmount, o.PaymentMethod, o.Comment
            FROM Orders o
            JOIN Users u ON o.UserID = u.UserID
            ORDER BY o.OrderID DESC
        ''')
        for row in cursor.fetchall():
            status_map = {
                "new": "🆕 Новый",
                "cooking": "👨‍🍳 Готовится",
                "delivering": "🚴 В пути",
                "delivered": "✅ Доставлен",
                "cancelled": "❌ Отменен"
            }
            status_text = status_map.get(row[4], row[4])
            self.orders_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], status_text, f"{row[5]:.2f} ₽", row[6], row[7]))
        conn.close()

    def show_order_items(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите заказ!")
            return

        order_id = self.orders_tree.item(selected_item, "values")[0]

        details_win = ctk.CTkToplevel(self)
        details_win.title(f"Состав заказа #{order_id}")
        details_win.geometry("520x380")
        details_win.resizable(False, False)
        details_win.configure(fg_color=COLOR_CARD_BG)
        details_win.transient(self)
        details_win.grab_set()

        lbl = ctk.CTkLabel(details_win, text=f"Блюда в заказе #{order_id}", font=("Segoe UI", 18, "bold"), text_color=COLOR_TOMATO)
        lbl.pack(pady=20)

        columns = ("name", "qty", "price_unit", "sum")
        items_tree = ttk.Treeview(details_win, columns=columns, show="headings", style="Treeview")
        items_tree.heading("name", text="Название")
        items_tree.heading("qty", text="Кол-во")
        items_tree.heading("price_unit", text="Цена")
        items_tree.heading("sum", text="Итог")

        items_tree.column("name", width=220, anchor="w")
        items_tree.column("qty", width=70, anchor="center")
        items_tree.column("price_unit", width=100, anchor="center")
        items_tree.column("sum", width=100, anchor="center")
        items_tree.pack(fill="both", expand=True, padx=20, pady=10)

        conn = db_helper.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.Name, oi.Quantity, oi.PriceAtMoment
            FROM OrderItems oi
            JOIN Dishes d ON oi.DishID = d.DishID
            WHERE oi.OrderID = ?
        ''', (order_id,))
        
        for row in cursor.fetchall():
            name, qty, price = row
            total = qty * price
            items_tree.insert("", "end", values=(name, qty, f"{price:.2f} ₽", f"{total:.2f} ₽"))
        conn.close()

        btn_close = ctk.CTkButton(details_win, text="Закрыть", command=details_win.destroy, height=38, fg_color="#402B25", hover_color="#1E120F")
        btn_close.pack(pady=20)

    def update_order_status(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите заказ!")
            return

        raw_id = self.orders_tree.item(selected_item, "values")[0]
        order_id = int(raw_id)
        new_status = self.status_combobox.get()

        conn = db_helper.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Orders SET Status = ? WHERE OrderID = ?", (new_status, order_id))
        conn.commit()
        conn.close()

        db_helper.log_action(self.current_user_id, "status_changed", f"Статус заказа #{order_id} изменен на '{new_status}'")
        self.refresh_orders_table()
        messagebox.showinfo("Успех", "Статус успешно обновлен!")

    def load_logs_tab(self):
        self.clear_container()
        self.set_active_button(self.btn_logs)
        
        title = ctk.CTkLabel(self.main_container, text="Логи активности", font=("Segoe UI", 24, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 20))

        columns = ("id", "user", "action", "desc", "date")
        self.log_tree = ttk.Treeview(self.main_container, columns=columns, show="headings", style="Treeview")
        self.log_tree.heading("id", text="ID")
        self.log_tree.heading("user", text="Пользователь")
        self.log_tree.heading("action", text="Действие")
        self.log_tree.heading("desc", text="Описание лога")
        self.log_tree.heading("date", text="Дата")

        self.log_tree.column("id", width=60, anchor="center")
        self.log_tree.column("user", width=160, anchor="w")
        self.log_tree.column("action", width=130, anchor="center")
        self.log_tree.column("desc", width=380, anchor="w")
        self.log_tree.column("date", width=160, anchor="center")
        self.log_tree.pack(fill="both", expand=True)

        conn = db_helper.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.LogID, u.FullName, l.ActionType, l.Description, l.ActionDate 
            FROM ActivityLog l
            LEFT JOIN Users u ON l.UserID = u.UserID
            ORDER BY l.LogID DESC
        ''')
        for row in cursor.fetchall():
            user = row[1] if row[1] else "⚙️ Системный процесс"
            self.log_tree.insert("", "end", values=(row[0], user, row[2], row[3], row[4]))
        conn.close()

    # ==================== ИНТЕРФЕЙС КЛИЕНТА (ЗАКАЗ ЕДЫ) ====================

    def show_client_dashboard(self):
        self.clear_window()
        self.cart = {}
        
        # Левая панель меню
        self.menu_panel = ctk.CTkFrame(self, fg_color=COLOR_BG_DARK)
        self.menu_panel.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # Шапка
        welcome_frame = ctk.CTkFrame(self.menu_panel, fg_color="transparent")
        welcome_frame.pack(fill="x", pady=(10, 15))

        lbl_welcome = ctk.CTkLabel(
            welcome_frame, text=f"👋 Добро пожаловать, {self.current_user}!", 
            font=("Segoe UI", 22, "bold"), text_color=COLOR_TOMATO
        )
        lbl_welcome.pack(anchor="w")
        
        lbl_subtitle = ctk.CTkLabel(
            welcome_frame, text="Выбирайте вкусную еду или испытайте удачу в нашем интерактиве!", 
            font=("Segoe UI", 12), text_color=COLOR_CREAM
        )
        lbl_subtitle.pack(anchor="w")

        # Наш интерактивный виджет "Мне повезет!"
        self.interactive_frame = ctk.CTkFrame(self.menu_panel, fg_color=COLOR_CARD_BG, height=80, corner_radius=12, border_width=1, border_color=COLOR_CHEESE)
        self.interactive_frame.pack(fill="x", pady=(0, 15))
        self.interactive_frame.pack_propagate(False)

        self.lbl_roulette = ctk.CTkLabel(
            self.interactive_frame, text="🤔 Не знаете, что заказать? Мы выберем за вас!", 
            font=("Segoe UI", 13, "italic"), text_color="white"
        )
        self.lbl_roulette.pack(side="left", padx=20)

        self.btn_roulette = ctk.CTkButton(
            self.interactive_frame, text="🎲 КНОПКА: МНЕ ПОВЕЗЕТ!", 
            fg_color=COLOR_CHEESE, hover_color="#D35400", text_color="black",
            font=("Segoe UI", 12, "bold"), height=35, corner_radius=8,
            command=self.run_food_roulette
        )
        self.btn_roulette.pack(side="right", padx=20)

        # Таблица меню
        columns = ("id", "name", "desc", "price", "category")
        self.client_menu_tree = ttk.Treeview(self.menu_panel, columns=columns, show="headings", style="Treeview")
        self.client_menu_tree.heading("id", text="ID")
        self.client_menu_tree.heading("name", text="Блюдо")
        self.client_menu_tree.heading("desc", text="Состав")
        self.client_menu_tree.heading("price", text="Стоимость")
        self.client_menu_tree.heading("category", text="Категория")
        
        self.client_menu_tree.column("id", width=40, anchor="center")
        self.client_menu_tree.column("name", width=180, anchor="w")
        self.client_menu_tree.column("desc", width=260, anchor="w")
        self.client_menu_tree.column("price", width=100, anchor="center")
        self.client_menu_tree.column("category", width=110, anchor="center")
        self.client_menu_tree.pack(fill="both", expand=True, pady=(0, 15))
        
        self.load_client_menu()

        # Кнопка добавления в корзину
        btn_add_to_cart = ctk.CTkButton(
            self.menu_panel, text="🛒 ДОБАВИТЬ ВЫБРАННОЕ В КОРЗИНУ", 
            fg_color=COLOR_TOMATO, hover_color="#C0392B",
            height=45, font=("Segoe UI", 13, "bold"), corner_radius=12,
            command=self.add_selected_to_cart
        )
        btn_add_to_cart.pack(fill="x")

        # Правая панель (Корзина и Оформление)
        self.cart_panel = ctk.CTkFrame(self, width=320, fg_color=COLOR_CARD_BG, corner_radius=15, border_width=1, border_color="#402B25")
        self.cart_panel.pack(side="right", fill="y", padx=20, pady=20)
        self.cart_panel.pack_propagate(False)

        lbl_cart_title = ctk.CTkLabel(self.cart_panel, text="🛒 КОРЗИНА ЗАКАЗА", font=("Segoe UI", 16, "bold"), text_color=COLOR_TOMATO)
        lbl_cart_title.pack(pady=20)

        self.cart_listbox = ctk.CTkTextbox(self.cart_panel, fg_color="#120A08", border_color="#402B25", corner_radius=10, font=("Segoe UI", 12))
        self.cart_listbox.pack(fill="both", expand=True, padx=15, pady=5)
        self.update_cart_display()

        # Поля доставки
        self.entry_address = ctk.CTkEntry(
            self.cart_panel, placeholder_text="Введите адрес доставки", 
            height=40, fg_color="#120A08", border_color="#402B25", corner_radius=8
        )
        self.entry_address.pack(fill="x", padx=15, pady=10)
        
        # Стандартный адрес клиента из базы
        conn = db_helper.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Address FROM Users WHERE UserID = ?", (self.current_user_id,))
        default_address = cursor.fetchone()[0]
        conn.close()
        if default_address:
            self.entry_address.insert(0, default_address)

        self.entry_comment = ctk.CTkEntry(
            self.cart_panel, placeholder_text="Комментарий курьеру", 
            height=40, fg_color="#120A08", border_color="#402B25", corner_radius=8
        )
        self.entry_comment.pack(fill="x", padx=15, pady=5)

        # Оформить
        self.btn_checkout = ctk.CTkButton(
            self.cart_panel, text="🚀 ОФОРМИТЬ ДОСТАВКУ", 
            fg_color=COLOR_SUCCESS, hover_color="#1E8449",
            height=45, font=("Segoe UI", 13, "bold"), corner_radius=12,
            command=self.checkout_order
        )
        self.btn_checkout.pack(fill="x", padx=15, pady=15)

        btn_logout = ctk.CTkButton(
            self.cart_panel, text="🚪 Выйти из аккаунта", 
            fg_color="#A93226", hover_color="#7B241C", 
            height=30, corner_radius=8, font=("Segoe UI", 11),
            command=self.show_login_screen
        )
        btn_logout.pack(pady=(0, 15))

    def load_client_menu(self):
        conn = db_helper.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DishID, Name, Description, Price, Category FROM Dishes WHERE IsAvailable = 1")
        for row in cursor.fetchall():
            self.client_menu_tree.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:.2f} ₽", row[4]))
        conn.close()

    def add_selected_to_cart(self):
        selected_item = self.client_menu_tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите блюдо из меню слева!")
            return

        values = self.client_menu_tree.item(selected_item, "values")
        dish_id = int(values[0])
        dish_name = values[1]
        price = float(values[3].replace(" ₽", ""))

        self.add_to_cart_logic(dish_id, dish_name, price)

    def add_to_cart_logic(self, dish_id, dish_name, price):
        if dish_id in self.cart:
            self.cart[dish_id]['qty'] += 1
        else:
            self.cart[dish_id] = {'name': dish_name, 'price': price, 'qty': 1}
        self.update_cart_display()

    # ИНТЕРАКТИВ: Случайный выбор блюда ("Пищевая рулетка")
    def run_food_roulette(self):
        # Получаем все блюда из таблицы Treeview
        items = self.client_menu_tree.get_children()
        if not items:
            messagebox.showwarning("Упс", "В меню сейчас пусто!")
            return

        self.btn_roulette.configure(state="disabled")
        
        # Эмуляция "вращения рулетки" — быстро перебираем случайные блюда на экране
        for i in range(12):
            random_item = random.choice(items)
            values = self.client_menu_tree.item(random_item, "values")
            self.lbl_roulette.configure(text=f"🌀 Выбираем...  ➔  {values[1]}", text_color=COLOR_CHEESE)
            self.update()
            time.sleep(0.08 + (i * 0.02))  # Замедляем кручение

        # Финальный выбор
        winner_item = random.choice(items)
        values = self.client_menu_tree.item(winner_item, "values")
        dish_id = int(values[0])
        dish_name = values[1]
        price = float(values[3].replace(" ₽", ""))

        self.lbl_roulette.configure(text=f"🎉 Рекомендуем попробовать: {dish_name}!", text_color=COLOR_SUCCESS)
        
        # Предлагаем добавить блюдо дня
        ans = messagebox.askyesno("Счастливое блюдо!", f"Рулетка выбрала блюдо:\n⭐ {dish_name} ({price:.2f} ₽) ⭐\n\nЖелаете добавить его в корзину?")
        if ans:
            self.add_to_cart_logic(dish_id, dish_name, price)
            
        self.btn_roulette.configure(state="normal")

    def update_cart_display(self):
        self.cart_listbox.configure(state="normal")
        self.cart_listbox.delete("1.0", "end")
        
        total_sum = 0.0
        if not self.cart:
            self.cart_listbox.insert("1.0", "Корзина пуста.\nДобавьте вкусняшек!")
        else:
            for dish_id, info in self.cart.items():
                cost = info['price'] * info['qty']
                total_sum += cost
                self.cart_listbox.insert("end", f"🔸 {info['name']}\n   {info['qty']} шт. х {info['price']} ₽ = {cost:.2f} ₽\n\n")
            
            self.cart_listbox.insert("end", f"-----------------------\nИТОГО К ОПЛАТЕ: {total_sum:.2f} ₽")
        
        self.cart_listbox.configure(state="disabled")
        self.current_total_sum = total_sum

    def checkout_order(self):
        if not self.cart:
            messagebox.showwarning("Внимание", "Добавьте товары в корзину!")
            return

        address = self.entry_address.get().strip()
        comment = self.entry_comment.get().strip()

        if not address:
            messagebox.showwarning("Внимание", "Укажите адрес доставки!")
            return

        conn = db_helper.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO Orders (UserID, DeliveryAddress, Status, TotalAmount, Comment, PaymentMethod)
                VALUES (?, ?, 'new', ?, ?, 'card_online')
            ''', (self.current_user_id, address, self.current_total_sum, comment))
            
            order_id = cursor.lastrowid
            
            for dish_id, info in self.cart.items():
                cursor.execute('''
                    INSERT INTO OrderItems (OrderID, DishID, Quantity, PriceAtMoment)
                    VALUES (?, ?, ?, ?)
                ''', (order_id, dish_id, info['qty'], info['price']))
                
            conn.commit()
            
            db_helper.log_action(self.current_user_id, "order_created", f"Создан новый заказ #{order_id} на сумму {self.current_total_sum:.2f} ₽")
            
            messagebox.showinfo("Готово!", f"Заказ #{order_id} успешно отправлен на кухню! 🍕")
            
            self.cart = {}
            self.update_cart_display()
            self.entry_comment.delete(0, "end")
            self.lbl_roulette.configure(text="🤔 Не знаете, что заказать? Мы выберем за вас!", text_color="white")
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось оформить: {e}")
        finally:
            conn.close()

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def set_active_button(self, active_btn):
        for btn in [self.btn_dishes, self.btn_orders, self.btn_logs]:
            if btn == active_btn:
                btn.configure(fg_color=COLOR_TOMATO)
            else:
                btn.configure(fg_color="transparent")

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()