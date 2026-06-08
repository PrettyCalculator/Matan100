import os
import json
import shutil

IMAGES_FOLDER = "page_images"


def load_database():
    """Загрузка билетов из JSON файла."""
    if not os.path.exists("database.json"):
        with open("database.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    with open("database.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_database(search_map):
    """Сохранение базы данных в JSON файл."""
    with open("database.json", "w", encoding="utf-8") as f:
        json.dump(search_map, f, ensure_ascii=False, indent=2)


def search_tickets(search_map, query):
    """Поиск билетов по номеру, ключевым словам или названию с сортировкой."""
    if not query:
        return []

    matches = []
    for item in search_map:
        ticket_id = str(item["ticket"])
        title = item["title"]
        keywords = item["keywords"]

        if query == ticket_id or any(query in kw.lower() for kw in keywords) or (query in title.lower()):
            matches.append(item)

    matches.sort(key=lambda x: int(x["ticket"]))
    return matches[:6]


def save_new_ticket_images(search_map, source_file_paths):
    """
    Копирует файлы в папку IMAGES_FOLDER (если их там еще нет)
    и возвращает список чистых имён файлов (без путей) для привязки к билету.
    """
    if not os.path.exists(IMAGES_FOLDER):
        os.makedirs(IMAGES_FOLDER)

    assigned_pages = []

    for src_path in source_file_paths:
        # Получаем чистое имя файла, например "calculus_page_5.png"
        filename = os.path.basename(src_path)
        dest_path = os.path.join(IMAGES_FOLDER, filename)

        # ОПТИМИЗАЦИЯ: Если файла с таким именем в папке нет — копируем его
        if not os.path.exists(dest_path):
            try:
                shutil.copy(src_path, dest_path)
            except Exception as e:
                print(f"Ошибка при копировании файла {filename}: {e}")
        else:
            # Если файл уже существует, мы просто мирно используем его,
            # не устраивая конфликтов и не перезаписывая его поверх.
            print(f"Файл {filename} уже существует в базе. Переиспользование.")

        # В список страниц билета сохраняем именно имя файла (или его часть без расширения)
        # Чтобы не переписывать логику отображения, сохраним имя целиком или имя без расширения.
        # Если твоя старая логика искала чисто по имени файла, сохраняем filename без расширения:
        name_inside_db = os.path.splitext(filename)[0]

        # Если у тебя в коде имена страниц хранятся как 'page_1', 'page_2' (то есть строки),
        # то 'name_inside_db' идеально запишется в JSON как строка типа 'calculus_page_5'
        assigned_pages.append(name_inside_db)

    return assigned_pages