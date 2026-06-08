import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image

import database
from create_window import CreateTicketWindow


class TicketBasedExamHelper(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Поиск по конспекту Эльвины")
        self.geometry("1150x850")
        # СВОЙСТВО -topmost УБРАНО: окно теперь ведет себя как обычное

        self.search_map = database.load_database()
        self.current_ticket = None
        self.current_page_index = 0

        # Загрузка иконки удаления
        self.delete_icon = None
        if os.path.exists("icons/delete.png"):
            try:
                pil_img = Image.open("icons/delete.png")
                self.delete_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(16, 16))
            except Exception as e:
                print(f"Не удалось загрузить delete.png: {e}")

        # Сетка панели управления и просмотра
        self.grid_columnconfigure(0, weight=0, minsize=360)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =================================================================
        # ЛЕВАЯ ПАНЕЛЬ: ДИНАМИЧЕСКИЙ САЙДБАР С БИЛЕТАМИ
        # =================================================================
        self.left_panel = ctk.CTkFrame(self, corner_radius=0, fg_color="#1e1e24")
        self.left_panel.grid(row=0, column=0, sticky="nsew")

        self.lbl_title = ctk.CTkLabel(self.left_panel, text="ПОИСК ИСПЫТАТЕЛЬНЫХ БИЛЕТОВ", font=("Arial", 14, "bold"),
                                      text_color="white")
        self.lbl_title.pack(anchor="w", padx=20, pady=(20, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.refresh_ticket_list)

        self.entry_search = ctk.CTkEntry(
            self.left_panel, placeholder_text="Введи номер билета или тему...",
            textvariable=self.search_var, font=("Arial", 14), height=42, fg_color="#2a2a35", border_color="#3b82f6",
            text_color="white"
        )
        self.entry_search.pack(fill="x", padx=20, pady=(0, 15))

        # СКРОЛЛИРУЕМЫЙ КОНТЕЙНЕР ДЛЯ ВСЕХ ПЛАШЕК БИЛЕТОВ
        self.tickets_scroll_frame = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent", label_text="")
        self.tickets_scroll_frame.pack(fill="both", expand=True, padx=15, pady=5)
        self.ticket_widgets = []

        # --- БЛОК: МОДИФИКАЦИЯ БАЗЫ ---
        self.separator1 = ctk.CTkFrame(self.left_panel, height=2, fg_color="#2a2a35")
        self.separator1.pack(fill="x", padx=10, pady=10)

        self.lbl_add_title = ctk.CTkLabel(self.left_panel, text="МОДИФИКАЦИЯ БАЗЫ", font=("Arial", 13, "bold"),
                                          text_color="white")
        self.lbl_add_title.pack(anchor="w", padx=20, pady=(0, 5))

        self.lbl_selected_ticket = ctk.CTkLabel(self.left_panel, text="Билет не выбран", font=("Arial", 12, "italic"),
                                                text_color="white")
        self.lbl_selected_ticket.pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_new_keyword = ctk.CTkEntry(
            self.left_panel, placeholder_text="Введи новое ключевое слово...",
            font=("Arial", 13), height=35, fg_color="#2a2a35", border_color="#10b981", text_color="white"
        )
        self.entry_new_keyword.pack(fill="x", padx=20, pady=(0, 8))

        self.btn_add_keyword = ctk.CTkButton(
            self.left_panel, text="Добавить к выбранному билету",
            font=("Arial", 12, "bold"), fg_color="#10b981", hover_color="#059669", height=35, text_color="white",
            command=self.add_keyword_to_database
        )
        self.btn_add_keyword.pack(fill="x", padx=20, pady=(0, 10))

        # --- БЛОК КНОПКИ СОЗДАНИЯ ---
        self.separator2 = ctk.CTkFrame(self.left_panel, height=2, fg_color="#2a2a35")
        self.separator2.pack(fill="x", padx=10, pady=10)

        self.btn_create_ticket = ctk.CTkButton(
            self.left_panel, text="➕ СОЗДАТЬ НОВЫЙ БИЛЕТ",
            font=("Arial", 13, "bold"), fg_color="#2563eb", hover_color="#1d4ed8", height=42, text_color="white",
            command=self.open_create_ticket_window
        )
        self.btn_create_ticket.pack(fill="x", padx=20, pady=(0, 10))

        self.status_label = ctk.CTkLabel(self.left_panel, text="Система готова", text_color="white")
        self.status_label.pack(side="bottom", pady=5)

        self.refresh_ticket_list()

        # =================================================================
        # ПРАВАЯ ПАНЕЛЬ: ЭКРАН ПРОСМОТРА
        # =================================================================
        self.right_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f0f12")
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=0)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.scroll_view = ctk.CTkScrollableFrame(self.right_frame, corner_radius=0, fg_color="transparent",
                                                  label_text="КОНСПЕКТ БИЛЕТА", label_text_color="white")
        self.scroll_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.view_label = ctk.CTkLabel(self.scroll_view, text="Выберите билет из списка слева", font=("Arial", 16),
                                       text_color="#555566")
        self.view_label.pack(expand=True, fill="both", pady=250)

        self.nav_frame = ctk.CTkFrame(self.right_frame, height=50, fg_color="#14141a", corner_radius=0)
        self.nav_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))

        self.btn_prev = ctk.CTkButton(self.nav_frame, text="⬅ Назад", width=100, command=self.prev_page,
                                      state="disabled", text_color="white")
        self.btn_prev.pack(side="left", padx=20, pady=10)

        self.lbl_page_counter = ctk.CTkLabel(self.nav_frame, text="Страница: 0 / 0", font=("Arial", 13, "bold"),
                                             text_color="white")
        self.lbl_page_counter.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.nav_frame, text="Вперед ➡", width=100, command=self.next_page,
                                      state="disabled", text_color="white")
        self.btn_next.pack(side="right", padx=20, pady=10)

    def refresh_ticket_list(self, *args):
        """Очищает и перерисовывает список плашек билетов с динамической высотой и ровным выравниванием."""
        for widget in self.ticket_widgets:
            widget.destroy()
        self.ticket_widgets.clear()

        query = self.search_var.get().strip().lower()

        if not query:
            matches = sorted(self.search_map, key=lambda x: int(x["ticket"]))
        else:
            matches = database.search_tickets(self.search_map, query)

        for item in matches:
            t_num = item["ticket"]
            t_title = item["title"]

            # 1. ГЛАВНЫЙ КОНТЕЙНЕР (Сетка grid для слоев)
            card = ctk.CTkFrame(self.tickets_scroll_frame, fg_color="#2a2a35", corner_radius=8)
            card.pack(fill="x", pady=5, padx=2)
            card.grid_columnconfigure(0, weight=1)  # Левая текстовая зона растягивается
            card.grid_columnconfigure(1, weight=0)  # Правая зона под кнопку удаления фиксированная
            self.ticket_widgets.append(card)

            btn_text = f"Билет №{t_num}\n{t_title}"

            # 2. КЛИКАБЕЛЬНАЯ ОБОЛОЧКА (Прозрачная кнопка во весь размер)
            click_zone = ctk.CTkButton(
                card, text="", fg_color="transparent", hover_color="#343442",
                corner_radius=8, command=lambda i=item: self.select_ticket(i)
            )
            # Размещаем в grid
            click_zone.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

            # 3. ТЕКСТОВЫЙ ЭЛЕМЕНТ (Размещаем в ту же ячейку ПАРАЛЛЕЛЬНО кнопке)
            # ВСЕ УПРАВЛЕНИЕ ИДЕТ ТОЛЬКО ЧЕРЕЗ GRID, НИКАКИХ PACK!
            lbl_text = ctk.CTkLabel(
                card, text=btn_text, font=("Arial", 12, "bold"), text_color="white",
                wraplength=230, justify="left", anchor="w"
            )
            lbl_text.grid(row=0, column=0, sticky="w", padx=12, pady=10)

            # Пробрасываем клик и ховер-эффекты
            lbl_text.bind("<Button-1>", lambda event, i=item: self.select_ticket(i))
            lbl_text.bind("<Enter>", lambda event: click_zone._on_enter())
            lbl_text.bind("<Leave>", lambda event: click_zone._on_leave())

            # 4. КВАДРАТНАЯ КНОПКА УДАЛЕНИЯ (Справа)
            if self.delete_icon:
                del_btn = ctk.CTkButton(
                    card, text="", image=self.delete_icon, width=34, height=34,
                    fg_color="#ef4444", hover_color="#dc2626", corner_radius=6,
                    command=lambda i=item: self.delete_ticket_by_id(i["ticket"])
                )
            else:
                del_btn = ctk.CTkButton(
                    card, text="❌", font=("Arial", 11), width=34, height=34,
                    fg_color="#ef4444", hover_color="#dc2626", corner_radius=6,
                    command=lambda i=item: self.delete_ticket_by_id(i["ticket"])
                )
            del_btn.grid(row=0, column=1, padx=8, pady=10, sticky="e")

    def select_ticket(self, ticket_item):
        self.current_ticket = ticket_item
        self.current_page_index = 0
        self.lbl_selected_ticket.configure(text=f"Активен: Билет №{ticket_item['ticket']}", text_color="white")
        self.update_image_view()

    def update_image_view(self):
        if not self.current_ticket or not self.current_ticket["pages"]:
            return

        pages_list = self.current_ticket["pages"]
        actual_page_num = pages_list[self.current_page_index]

        image_path = None
        # Проверяем, содержит ли actual_page_num уже имя файла (например "page_5" или "my_doc")
        for ext in ['.png', '.jpg', '.jpeg']:
            # Сначала ищем по чистому имени из базы данных
            test_path1 = os.path.join(database.IMAGES_FOLDER, f"{actual_page_num}{ext}")
            # Запасной вариант на случай старых билетов, где хранились только голые цифры
            test_path2 = os.path.join(database.IMAGES_FOLDER, f"page_{actual_page_num}{ext}")

            if os.path.exists(test_path1):
                image_path = test_path1
                break
            elif os.path.exists(test_path2):
                image_path = test_path2
                break

        if not image_path:
            self.status_label.configure(text=f"Ошибка: Карта страницы {actual_page_num} не найдена!",
                                        text_color="#ef4444")
            return

        pil_img = Image.open(image_path)
        target_width = 750
        width_ratio = target_width / float(pil_img.size[0])
        target_height = int((float(pil_img.size[1]) * float(width_ratio)))

        pil_img = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_width, target_height))

        self.view_label.configure(image=ctk_img, text="")
        self.view_label.image = ctk_img
        self.scroll_view._parent_canvas.yview_moveto(0.0)

        self.lbl_page_counter.configure(
            text=f"Страница {self.current_page_index + 1} из {len(pages_list)} (Файл: стр. {actual_page_num})",
            text_color="white"
        )
        self.btn_prev.configure(state="normal" if self.current_page_index > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page_index < len(pages_list) - 1 else "disabled")

    def next_page(self):
        if self.current_ticket and self.current_page_index < len(self.current_ticket["pages"]) - 1:
            self.current_page_index += 1
            self.update_image_view()

    def prev_page(self):
        if self.current_ticket and self.current_page_index > 0:
            self.current_page_index -= 1
            self.update_image_view()

    def add_keyword_to_database(self):
        """Добавление нового тега/слова к открытому в данный момент билету с защитой от дубликатов."""
        if not self.current_ticket:
            self.status_label.configure(text="Сначала откройте нужный билет!", text_color="#ef4444")
            return

        new_word = self.entry_new_keyword.get().strip().lower()
        if not new_word:
            return

        # Оптимизация: Проверяем, есть ли уже такое слово в базе (в любом регистре)
        existing_keywords = [kw.lower() for kw in self.current_ticket["keywords"]]

        if new_word in existing_keywords:
            self.status_label.configure(text=f"Слово '{new_word}' уже привязано к этому билету!", text_color="#ef4444")
            self.entry_new_keyword.delete(0, tk.END)
            return

        # Если слова нет — добавляем и сохраняем
        self.current_ticket["keywords"].append(new_word)
        database.save_database(self.search_map)
        self.status_label.configure(text=f"Добавлено слово '{new_word}' к Билету №{self.current_ticket['ticket']}",
                                    text_color="white")
        self.entry_new_keyword.delete(0, tk.END)

    def delete_current_ticket(self):
        if not self.current_ticket:
            self.status_label.configure(text="Ошибка: Билет для удаления не выбран!", text_color="#ef4444")
            return

        target_id = self.current_ticket["ticket"]
        self.delete_ticket_by_id(target_id)

    def delete_ticket_by_id(self, target_id):
        self.search_map = [item for item in self.search_map if item["ticket"] != target_id]
        database.save_database(self.search_map)

        if self.current_ticket and self.current_ticket["ticket"] == target_id:
            self.current_ticket = None
            self.current_page_index = 0
            self.view_label.configure(image="", text="Билет успешно удален.", text_color="white")
            self.view_label.image = None
            self.lbl_selected_ticket.configure(text="Билет не выбран", text_color="white")
            self.lbl_page_counter.configure(text="Страница: 0 / 0", text_color="white")
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")

        self.status_label.configure(text=f"Билет №{target_id} удален из базы", text_color="#ef4444")
        self.refresh_ticket_list()

    def open_create_ticket_window(self):
        # Больше не меняем состояние главного окна, просто открываем конструктор
        win = CreateTicketWindow(self)
        win.bind("<Destroy>", lambda e: self.on_create_window_destroyed())

    def on_create_window_destroyed(self):
        self.search_map = database.load_database()
        self.refresh_ticket_list()