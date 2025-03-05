from tkinter import *
from tkinter import filedialog as fd
import ttkbootstrap as ttk
import os
import analysis # скрипт analysis.py


class MyApp:
  def __init__(self, root):
    self.cont1, self.open_file_button, self.open_folder_button = None, None, None # Окно
    self.root = root
    self.style = ttk.Style(theme='lumen')
    self.style.configure('TCheckbutton', background='#335087', foreground='white')
    self.root.title("Regression analysis")
    self.root = self.style.master
    self.root.configure(bg="#335087")
    self.root.geometry('800x600')
    self.position = {"padx": 6, "pady": 6, "anchor": NW}

    self.interval = 0 # Переменные
    self.folder_path = ""
    self.folder_name = StringVar()
    self.resolution = -1
    self.file_path = ""
    self.file_path_quike = ""

    self.clear_window()

  def clear_window(self):
    for widget in self.root.winfo_children():
      widget.destroy()

    text = ttk.Label(text="Загрузить папку или конкретные файлы из папки?")
    text.configure(background="#335087", foreground="white")
    text.pack(**self.position)

    self.cont1 = Frame()
    self.cont1.pack(fill=X)
    self.cont1.columnconfigure(index=0, weight=1)
    self.cont1.columnconfigure(index=1, weight=1)
    self.cont1.configure(bg="#335087")

    self.open_choose_folder()
    self.open_choose_file()

  def open_choose_folder(self):
    self.open_folder_button = ttk.Button(self.cont1, text='Поток файлов', command=self.create_choose_folder)
    self.open_folder_button.grid(row=0, column=0)

  def create_choose_folder(self):
    self.clear_window()
    choice = ['Да', 'Нет']
    selected_choice = StringVar()

    first_question = ttk.Label(text="1. Нужно строить на графиках доверительные интервалы?")
    first_question.configure(background="#335087", foreground="white")
    first_question.pack(**self.position)

    def select():
      if selected_choice.get() == choice[0]:
        self.interval = 1
      elif selected_choice.get() == choice[1]:
        self.interval = 0

    for el in choice:
      first_button = ttk.Radiobutton(text=el, value=el, variable=selected_choice, command=select, style='TCheckbutton')
      first_button.pack(**self.position)

    # ---------------------------------------------------------------------------------------
    second_question = ttk.Label(text="2. Выберите папку, где хранятся данные по станциям(если такая есть)?")
    second_question.configure(background="#335087", foreground="white")
    second_question.pack(**self.position)

    def choose_folder():
      self.folder_path = fd.askdirectory()
      second_button.configure(text=f"Выбрана папка: {self.folder_path}")

    second_button = ttk.Button(self.root, text='Выберите папку', command=choose_folder)
    second_button.pack(**self.position)

    # ---------------------------------------------------------------------------------------
    third_question = ttk.Label(
      text="3. Введите название папки, в которую добавят, полученные графики по данным, переданным из папки")
    third_question.configure(background="#335087", foreground="white")
    third_question.pack(**self.position)

    third_button = ttk.Entry(self.root, textvariable=self.folder_name)
    third_button.pack(**self.position)

    # ---------------------------------------------------------------------------------------
    choice_of_res = ['.jpg', '.pdf']
    selected_resolution = StringVar()

    fourth_question = ttk.Label(
      text="4. Выберите разрешение, с каким будут загружаться графики по данным, переданным из папки")
    fourth_question.configure(background="#335087", foreground="white")
    fourth_question.pack(**self.position)

    def select_resolution():
      self.resolution = choice_of_res.index(selected_resolution.get())

    for el in choice_of_res:
      fourth_button = ttk.Radiobutton(text=el, value=el, variable=selected_resolution, command=select_resolution, style='TCheckbutton')
      fourth_button.pack(**self.position)

    self.confirm()

  def open_choose_file(self):
    self.open_file_button = ttk.Button(self.cont1, text='Загрузить файлы из папки', command=self.create_choose_file)
    self.open_file_button.grid(row=0, column=1)

  def create_choose_file(self):
    self.clear_window()
    choice = ['Да', 'Нет']
    selected_choice = StringVar()
    interval = 0

    first_question = ttk.Label(text="1. Нужно строить на графиках доверительные интервалы?")
    first_question.configure(background="#335087", foreground="white")
    first_question.pack(**self.position)

    def select():
      if selected_choice.get() == choice[0]:
        self.interval = 1
      elif selected_choice.get() == choice[1]:
        self.interval = 0

    for el in choice:
      first_button = ttk.Radiobutton(text=el, value=el, variable=selected_choice, command=select, style='TCheckbutton')
      first_button.pack(**self.position)

    # ---------------------------------------------------------------------------------------
    second_file_question = ttk.Label(text="2. Выберите файлы, чтобы увидеть график станции сейчас:")
    second_file_question.configure(background="#335087", foreground="white")
    second_file_question.pack(**self.position)

    def choose_file_quike():
      self.file_path_quike = fd.askopenfilename()
      file_button_quike.configure(text=f"Выбран файл zem: {self.file_path_quike}")

    def choose_file():
      self.file_path = fd.askopenfilename()
      file_button.configure(text=f"Выбран файл neu: {self.file_path}")
      _, _, _, _, _, _, _, _, _ = analysis.regression("", self.interval, NONE, self.file_path[-15:-11], os.getcwd(), self.file_path, self.file_path_quike)

    file_button_quike = ttk.Button(self.root, text='Выберите файл c землетрясениями', command=choose_file_quike)
    file_button_quike.pack(**self.position)
    file_button = ttk.Button(self.root, text='Выберите файл', command=choose_file)
    file_button.pack(**self.position)

    self.confirm()

  def confirm(self):
    confirm_button = ttk.Button(self.root, text="Ок", command=self.destroy)
    confirm_button.pack(anchor='s', expand=1)

  def destroy(self):
    self.root.destroy()


if __name__ == "__main__":
  root = Tk()
  app = MyApp(root)
  root.mainloop()
