from settings import *
from moviepy.editor import ImageClip, AudioFileClip
import tkinter as tk
from pymongo import MongoClient
from tkinter import messagebox

def SwithWindowDraw(openwindow, closewindow):
    openwindow.deiconify()
    closewindow.withdraw()

def SwithWindowOpen(openwindow, closewindow):
    openwindow.mainloop()
    closewindow.withdraw()

def SwithWindowClos(openwindow, closewindow):
    openwindow.deiconify()
    closewindow.destroy()


class GUIMaker:
    def PullManga(self):
        # 1. Создаем модальное (дочернее) окно поверх основного
        # Передаем self.root (или как называется твое главное окно), чтобы они были связаны
        chooser_win = tk.Toplevel(self.root)
        chooser_win.title("Выберите мангу")
        chooser_win.geometry("350x400")

        # Делаем так, чтобы пользователь не мог кликнуть на главное окно, пока не закроет это
        chooser_win.grab_set()

        # 2. Создаем переменную Tkinter для хранения выбранного ID
        # Так как в БД ID — это число (инт), используем IntVar
        selected_id = tk.IntVar(value=-1)  # По умолчанию -1 (ничего не выбрано)

        # Шапка окна
        label = tk.Label(chooser_win, text="Доступная манга в базе:", font=("Arial", 12, "bold"), pady=10)
        label.pack()

        # Контейнер со скроллом, если манг будет очень много (опционально, фрейм для порядка)
        frame = tk.Frame(chooser_win)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # 3. Выкачиваем из БД всю мангу и перебираем её
        # Сортируем по ID для красоты
        manga_list = self.collection_manga.find().sort("ID", 1)

        has_manga = False
        for manga in manga_list:
            has_manga = True
            # Создаем Radiobutton для каждой манги
            rb = tk.Radiobutton(
                frame,
                text=f"[{manga['ID']}] {manga['name']}",  # Что видит пользователь
                variable=selected_id,  # Общая переменная для группы
                value=manga['ID'],  # Что запишется в переменную при клике
                anchor=tk.W,  # Прижимаем текст влево
                font=("Arial", 10)
            )
            rb.pack(fill=tk.X, pady=2, anchor=tk.W)

        if not has_manga:
            no_manga_lbl = tk.Label(frame, text="База данных пуста!", fg="red")
            no_manga_lbl.pack(pady=20)

        # 4. Логика закрытия и возврата значения
        def on_confirm():
            if selected_id.get() == -1:
                messagebox.showwarning("Внимание", "Вы не выбрали ни одну мангу!", parent=chooser_win)
            else:
                # Закрываем окно, завершая его ожидание
                chooser_win.destroy()

        # Кнопка подтверждения
        confirm_btn = tk.Button(
            chooser_win,
            text="Выбрать",
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            command=on_confirm
        )
        confirm_btn.pack(pady=15, fill=tk.X, padx=20)

        # 5. Смертельный трюк: заставляем Python ЖДАТЬ, пока это окно не закроется
        chooser_win.wait_window()

        # Код возобновит работу здесь ТОЛЬКО после chooser_win.destroy()
        return selected_id.get()

    def screenshot(self):
        self.image = self.prtscreen.Start_Screan()

    def AddManga(self, screan, name):

        if screan == None or name == None:
            exit

        last_document = self.collection_manga.find_one(sort=[("ID", -1)])

        if last_document and "ID" in last_document:
            new_id = last_document["ID"] + 1
        else:
            new_id = 1

        self.collection_manga.insert_one({"name":name, "manga":screan,"ID":new_id})

        SwithWindowClos(self.menu,self.page)


    def EditManga(self, ID):
        SwithWindowOpen(self.page,self.menu)
         #____________________________________________________________________________________________

    def __init__(self):
        # init Buff
        self.image = None

        # init class settings
        self.prtscreen = ScreenSelector()

        # GUI
        self.menu = tk.Tk() # Меню
        self.page = tk.Tk() # Страница которую обрабатывают
        self.line = tk.Tk() # Реплика персонажа
        self.menu.title("Меню")
        self.page.title("Добавить страничку манги")
        self.line.title("Добавить реплику к страничке")

        # menu
        self.bNewManga = tk.Button(self.menu, text="Добавить новую мангу в БД", bg="lightblue", command=SwithWindowOpen(self.page,self.menu))
        self.bNewManga.pack(side=tk.TOP, fill=tk.X, padx=2, pady=4)
        self.bEditManga = tk.Button(self.menu, text="Редактирывать мангу", bg="lightblue", command=self.EditManga(self.PullManga()))
        self.bEditManga.pack(side=tk.TOP, fill=tk.X, padx=2, pady=4)

        # page
        self.eNamepage = tk.Entry(self.page,text="Название")
        self.eNamepage.pack(side=tk.TOP, fill=tk.X, padx=4, pady=8)
        self.bImagepage = tk.Button(self.page, text="Добавить изображение", bg="lightblue", command=self.prtscreen.Start_Screan())
        self.bAddmangapage = tk.Button(self.page, text="Добавить мангу", bg="lightblue", command=self.AddManga())
        self.bAddmangapage.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # MongoDb
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["manga_project"]
        self.collection_manga = self.db["Manga"]
        self.collection_pages = self.db["Pages"]
        self.menu.mainloop()
