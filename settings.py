import tkinter as tk # Импортируем tkinter для создания окна выбора области
from PIL import ImageGrab # ImageGrab позволяет делать снимки экрана
import paddleocr # для перевода из фото в текст
import cv2 # для подготовки изображений
#from matplotlib.image import interpolations_names
import torch
import torchaudio


class ScreenSelector: # Класс отвечает за выбор области экрана

    def __init__(self):
        self.start_x = None
        self.start_y = None

        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.2)
        self.root.configure(bg="gray")
        self.canvas = tk.Canvas(self.root,cursor="cross"  )# Создаем холст  курсор-крестик
        self.canvas.pack(fill="both",expand=True) # пакуем на весь экран
        self.rect = None # ID прямоугольника
        self.canvas.bind("<ButtonPress-1>",self.on_press)#ЛКМ
        self.canvas.bind("<B1-Motion>",self.on_drag)# зажата
        self.canvas.bind("<ButtonRelease-1>",self.on_release)# дубай отпуск

    def on_press(self, event):

        self.start_x = event.x
        self.start_y = event.y

        # Создаем прямоугольник нулевого размера
        # Пока не потащил мышь
        self.rect = self.canvas.create_rectangle(self.start_x,self.start_y,self.start_x,self.start_y,outline="blue",width=1)

    def on_drag(self, event):

        # Изменяем размеры прямоугольника
        self.canvas.coords(self.rect,self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        self.root.destroy()
        screenshot = ImageGrab.grab( bbox=(x1,y1,x2,y2))
        screenshot.save("selected_area.png")
        print("Скриншот сохранен: selected_area.png")
        return screenshot

    def Start_Screan(self):
        self.root.mainloop()  # пошло говно по трубам


class ScreenshotTranslation:# Класс для перевода текста с картинки в String
    def __init__(self):
        self.translation = paddleocr.PaddleOCR(lang='ru', use_gpu=True,use_angle_cls=True,show_log=False,det_limit_side_len=3000,det_db_thresh=0.2,det_db_box_thresh=0.3)
        self.gray_color_image = None

    def Start_translation(self, screen):
        self.gray_color_image = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        self.gray_color_image = cv2.resize(self.gray_color_image,None, fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
        self.gray_color_image = cv2.equalizeHist(self.gray_color_image)
        self.gray_color_image = cv2.threshold(self.gray_color_image,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return  self.translation.ocr(self.gray_color_image)

class TextToSpeak:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model, self.example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',model='silero_tts',language='ru',speaker='v4_ru')
        self.model.to(self.device)
        self.speaker = 'xenia'# Доступные спикеры: 'aidar', 'baya', 'kseniya', 'xenia', 'eugene', 'random'
        self.sample_rate = 48000
        self.audio = None


    def Start_Create_Audio(self, text):# Нейросеть сама расставит ударения
        # Автоматическое добавление буквы 'ё'
        self.audio = self.model.apply_tts(text=text,speaker=self.speaker,sample_rate=self.sample_rate,put_accent=True,put_yo=True)
        return self.audio

# def main():
#     # Проверяем, видит ли Python твою RTX 4060
#     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#     print(f"Используем вычислительное устройство: {device}")
#
#     print("Загрузка модели Silero TTS (при первом запуске скачается около 50МБ)...")
#     # Загружаем последнюю модель v4 для русского языка
#     model, example_text = torch.hub.load(
#         repo_or_dir='snakers4/silero-models',
#         model='silero_tts',
#         language='ru',
#         speaker='v4_ru'
#     )
#     # Переносим модель в память видеокарты
#     model.to(device)
#
#     # Текст, который нужно озвучить (можешь вставить текст из манги)
#     text = "Привет! Это проверка работы локальной нейросети. Я идеально говорю по-русски, знаю где ставить удар+ения, и всё это генерируется на твоей крутой видеокарте."
#
#     # Настройки голоса
#     # Доступные спикеры: 'aidar', 'baya', 'kseniya', 'xenia', 'eugene', 'random'
#     speaker = 'xenia'
#     sample_rate = 48000  # Студийное качество звука
#
#     print(f"Генерирую аудио голосом '{speaker}'...")
#
#     # Генерация аудио
#     audio = model.apply_tts(
#         text=text,
#         speaker=speaker,
#         sample_rate=sample_rate,
#         put_accent=True,  # Нейросеть сама расставит ударения
#         put_yo=True  # Автоматическое добавление буквы 'ё'
#     )
#
#     # Сохраняем результат в файл
#     output_filename = "output.wav"
#     # torchaudio требует двумерный тензор, поэтому делаем unsqueeze(0)
#     torchaudio.save(output_filename, audio.unsqueeze(0).cpu(), sample_rate)
#
#     print(f"Готово! Аудио сохранено в файл {output_filename}. Можешь открывать и слушать.")
#
