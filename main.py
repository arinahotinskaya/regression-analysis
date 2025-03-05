import analysis # скрипт analysis.py
import os
from matplotlib.backends.backend_pdf import PdfPages
from tkinter import *
import interface # скрипт interface.py


if __name__ == '__main__':
  root = Tk()
  app = interface.MyApp(root)
  root.mainloop()

  if app.folder_path != "":
    folder_path = app.folder_path
    folder_name = app.folder_name.get()

    # Проверка существования папки folder_name и создание при необходимости
    folder_path_full = os.path.join(os.getcwd(), folder_name)
    if not os.path.isdir(folder_path_full):
      os.mkdir(folder_path_full)

    # Проверка существования папки station-txt и создание при необходимости
    station_txt_path = os.path.join(folder_path_full, 'station-txt')
    if not os.path.isdir(station_txt_path):
      os.mkdir(station_txt_path)

    # Создание файла velocity.txt для записи скоростей
    file = open(os.getcwd() + '/' + app.folder_name.get() + '/' + "velocity.txt", "w")  # создаем файл, куда запишем полученные скорости
    file.write('station Vn(mm) Ve(mm) Vu(mm) sigmaN(mm) sigmaE(mm) sigmaU(mm)\n')

    content = os.listdir(str(app.folder_path))
    # Фильтрация элементов списка content, чтобы исключить ".DS_Store"
    content = [el for el in content if el != '.DS_Store']

    name_of_stations = list(set([el[:4] for el in content]))
    count = len(name_of_stations)
    print(name_of_stations)

    pdf = PdfPages(os.path.join(folder_path_full, f"{folder_name}.pdf")) if app.resolution == 1 else 0

    while count != 0:
      station_name = name_of_stations[count - 1]
      print(f"\nСтанция {station_name}:")
      station_file_path = os.path.join(station_txt_path, f"{station_name}.txt")

      with open(station_file_path, "w") as file_station:
        neu, zem = -1, -1
        for el in content:
          file_path = os.path.join(folder_path, el)
          if not (os.path.exists(file_path) and el.startswith(station_name)):
            continue
          if el.endswith('.neu'):
            neu = el
          elif el.endswith('.zem'):
            zem = el
        if zem == -1:
          a, V, c, d, e, f, h, k, sigma = analysis.regression(pdf, app.interval, app.resolution, name_of_stations[count - 1], app.folder_name.get(), app.folder_path + '/' + neu)
        elif zem != -1:
          a, V, c, d, e, f, h, k, sigma = analysis.regression(pdf, app.interval, app.resolution, name_of_stations[count - 1], app.folder_name.get(), app.folder_path + '/' + neu, app.folder_path + '/' + zem)

        line1 = 'station: {}\n(north, east, up)\n'.format(name_of_stations[count - 1])
        line2 = 'a(n, e, u): {} {} {}\n'.format(a[0], a[1], a[2])
        line3 = 'V(n, e, u): {} {} {}\n'.format(V[0], V[1], V[2])
        line4 = 'c(n, e, u): {} {} {}\n'.format(c[0], c[1], c[2])
        line5 = 'd(n, e, u): {} {} {}\n'.format(d[0], d[1], d[2])
        line6 = 'e(n, e, u): {} {} {}\n'.format(e[0], e[1], e[2])
        line7 = 'f(n, e, u): {} {} {}\n'.format(f[0], f[1], f[2])
        line8 = 'h(n, e, u): {} {} {}\n'.format(h[0], h[1], h[2])
        line9 = 'k(n, e, u): {} {} {}\n'.format(k[0], k[1], k[2])
        file_station.write(line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9)
        file.write(name_of_stations[count - 1] + ' ' + str("{:.2f}".format(V[0])) + ' ' + str("{:.2f}".format(V[1]))
                   + ' ' + str("{:.2f}".format(V[2])) + ' ' + str("{:.2f}".format(sigma[0])) + ' ' + str("{:.2f}".format(sigma[1]))
                   + ' ' + str("{:.2f}".format(sigma[2])) + '\n')
        count -= 1

    if app.resolution == 1:
      pdf.close()
    file.close()
