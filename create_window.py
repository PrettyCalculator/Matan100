import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
import database


class CreateTicketWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Конструктор нового билета")
        self.geometry("500x550")
        self.resizable(False, False)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.selected_image_paths = []

        # Графические элементы формы
        lbl_header = ctk.CTkLabel(self, text="СОЗДАНИЕ НОВОГО БИЛЕТА", font=("Arial", 14, "bold"), text_color="black")
        lbl_header.pack(pady=15)

        self.new_ticket_id = ctk.CTkEntry(self, placeholder_text="Номер билета (например: 5)", width=400,
                                          text_color="black")
        self.new_ticket_id.pack(pady=10)

        self.new_ticket_title = ctk.CTkEntry(self, placeholder_text="Название билета (например: Теорема Ролля)",
                                             width=400, text_color="black")
        self.new_ticket_title.pack(pady=10)

        self.new_ticket_keywords = ctk.CTkEntry(self, placeholder_text="Ключевые слова через запятую (производная...)",
                                                width=400, text_color="black")
        self.new_ticket_keywords.pack(pady=10)

        self.btn_select_files = ctk.CTkButton(
            self, text="📁 Выбрать изображения билета",
            fg_color="#3a3a45", hover_color="#4e4e5a", width=400, text_color="black",
            command=self.select_ticket_images
        )
        self.btn_select_files.pack(pady=15)

        self.lbl_files_status = ctk.CTkLabel(self, text="Изображения не выбраны", text_color="black",
                                             font=("Arial", 12, "italic"))
        self.lbl_files_status.pack(pady=5)

        self.btn_submit = ctk.CTkButton(
            self, text="Сохранить билет в базу данных",
            fg_color="#10b981", hover_color="#059669", font=("Arial", 13, "bold"), width=400, height=40,
            text_color="white",
            command=self.submit_new_ticket
        )
        self.btn_submit.pack(pady=25)

    def select_ticket_images(self):
        files = filedialog.askopenfilenames(
            title="Выберите страницы билета",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg")]
        )
        if files:
            self.selected_image_paths = list(files)
            self.lbl_files_status.configure(
                text=f"Выбрано файлов: {len(self.selected_image_paths)}",
                text_color="white"
            )

    def submit_new_ticket(self):
        t_id = self.new_ticket_id.get().strip()
        t_title = self.new_ticket_title.get().strip()
        t_kw_str = self.new_ticket_keywords.get().strip()

        if not t_id or not t_title:
            self.lbl_files_status.configure(text="Ошибка: Заполни Номер и Название!", text_color="#ef4444")
            return

        try:
            ticket_number = int(t_id)
        except ValueError:
            self.lbl_files_status.configure(text="Ошибка: Номер билета должен быть числом!", text_color="#ef4444")
            return

        if any(item["ticket"] == ticket_number for item in self.parent.search_map):
            self.lbl_files_status.configure(text=f"Ошибка: Билет №{ticket_number} уже существует!",
                                            text_color="#ef4444")
            return

        if not self.selected_image_paths:
            self.lbl_files_status.configure(text="Ошибка: Выберите хотя бы одно изображение!", text_color="#ef4444")
            return

        new_ticket_pages = database.save_new_ticket_images(self.parent.search_map, self.selected_image_paths)

        # --- АВТОМАТИЧЕСКИЙ ПАРСИНГ НАЗВАНИЯ НА КЛЮЧЕВЫЕ СЛОВА ---
        # Очищаем слова от знаков препинания (запятые, точки, скобки), если они есть
        clean_title = t_title.replace(",", " ").replace(".", " ").replace("(", " ").replace(")", " ")
        title_words = [w.strip().lower() for w in clean_title.split() if len(w.strip()) > 1]

        # Парсим теги, введенные пользователем вручную
        manual_keywords = [k.strip().lower() for k in t_kw_str.split(",") if k.strip()]

        # Объединяем оба списка через set() для гарантированного удаления дубликатов
        unique_keywords = list(set(title_words + manual_keywords))

        new_ticket_obj = {
            "ticket": ticket_number,
            "title": t_title,
            "pages": new_ticket_pages,
            "keywords": unique_keywords  # Сохраняем уникальный оптимизированный список
        }

        self.parent.search_map.append(new_ticket_obj)
        database.save_database(self.parent.search_map)

        self.parent.status_label.configure(text=f"Успешно создан Билет №{ticket_number}!", text_color="white")
        self.on_close()

    def on_close(self):
        self.grab_release()
        self.destroy()