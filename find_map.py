import json
from io import BytesIO
import datetime
from tkinter import Tk, Button, Entry, Label, Canvas, X, NW, END
from PIL import ImageTk, Image
import requests

class FindMapApp:
    def __init__(self):
        # создание и инициализация окна и атрибутов
        self.what_to_find = None
        self.root = Tk()
        self.root.geometry('800x600')
        self.root.title('Поиск по карте')
        self.root.resizable(False, False)
        self.label = Label(text='Поиск по карте', font=('Verdana', 16))
        self.label.pack(fill=X)
        self.label_clock = Label(font=('Verdana', 22))
        self.label_header = Label(text='Адрес:', font=('Verdana', 14))
        self.entry = Entry(width=50, font=('Verdana', 14))
        self.button_find = Button(text='Найти', width=10, command=self.search)
        self.button_plus = Button(text='+', command=self.zoom_plus)
        self.button_minus = Button(text='-', command=self.zoom_minus)
        self.canvas = Canvas(width=600, height=450)
        # размещаем элементы на окне
        self.label_header.place(x=15, y=35)
        self.entry.place(x=87, y=35)
        self.button_find.place(x=700, y=35)
        self.canvas.place(x=100, y=75)
        self.label_clock.place(x=320, y=540)
        self.button_plus.place(x=475, y=540)
        self.button_minus.place(x=250, y=540)
        self.delta = '0.001'  # для приблежения и удаления за 1 клик
        # добавляем пустышку
        self.image = Image.new('RGB', (600, 450), (255, 255, 255))
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
        self.show_time()
        self.root.mainloop()

    def search(self):  # запрос
        self.what_to_find = self.entry.get().strip()
        if len(self.what_to_find) < 3:
            self.entry.delete(0, END)
            self.entry.insert(END, 'СПб, Можайская, 2')
            self.what_to_find = self.entry.get()
        geocoder_params = {
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'geocode': self.what_to_find,
            'format': 'json'
        }
        url = 'http://geocode-maps.yandex.ru/1.x/'
        response = requests.get(url, params=geocoder_params).json()
        # print(json.dumps(response, indent=4, ensure_ascii=False))
        toponym = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        coords = toponym['Point']['pos']
        coords = coords.split()
        map_params = {
            'll': ','.join(coords),
            'spn': f'{self.delta},{self.delta}',
            'l': 'map',
            'pt': ','.join(coords) + ',pm2dgl'
        }
        map_url = 'http://static-maps.yandex.ru/1.x/'
        response = requests.get(map_url, params=map_params)
        self.image = Image.open(BytesIO(response.content))
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=NW, image=self.photo)

    def zoom_plus(self):
        zoom = float(self.delta) / 1.5
        self.delta = str(zoom)
        self.search()

    def zoom_minus(self):
        zoom = float(self.delta) * 1.5
        if zoom > 32.700:
            zoom = 32.700
        self.delta = str(zoom)
        self.search()

    def show_time(self):
        time_ = datetime.datetime.now().strftime('%H:%M:%S')
        self.label_clock['text'] = time_
        self.root.after(1000, self.show_time)

