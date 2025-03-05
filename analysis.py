import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
import ttkbootstrap as ttk
import calendar
import data as dt # скрипт data.py


# ФИЛЬТРАЦИЯ
def decimal_date(year, day):
  n = 355
  if calendar.isleap(year):
    n = 366
  return np.trunc((year + (day - 0.5) / n) * 1e5) / 1e5


def count_irq(time, direction, sigma, day, year):
  names_of_dir = ['north', 'east', 'up']
  n = 365
  anomaly = np.empty(3, dtype=object)
  vec_decimal_date = np.vectorize(decimal_date)

  for el in range(len(names_of_dir)):
    j = 181
    for i in range(len(time)):
      flag = dt.leap_year(year[i])

      if 0 <= i < 182:
        max_day = day[i] + i
        max_year = year[i]

        if max_day > flag:
          max_year += 1
          max_day %= dt.leap_year(max_year)
        min_day = day[i] - i
        min_year = year[i]

      elif 182 <= i <= len(day) - 182:
        max_day = day[i] + n / 2
        max_year = year[i]

        if max_day > flag:
          max_year += 1
          max_day %= dt.leap_year(max_year)
        min_day = day[i] - n / 2
        min_year = year[i]

      elif len(day) - 182 < i <= len(day) - 1:
        max_day = day[i] + j
        max_year = year[i]

        if max_day > flag:
          max_year += 1
          max_day %= dt.leap_year(max_year)
        min_day = day[i] - j
        min_year = year[i]

      if min_day < 0:
        min_year -= 1
        min_day += dt.leap_year(min_year)

      start_date = vec_decimal_date(min_year, min_day)
      end_date = vec_decimal_date(max_year, max_day)
      j -= 1

      indices = (time >= start_date) & (time <= end_date)
      box = direction[el][indices]

      if len(box) > 0:
        median = np.median(box)
        box_q1 = box[box < median]
        box_q3 = box[box > median]

        if len(box_q1) > 0:
          q1 = np.median(box_q1)
        else:
          q1 = None

        if len(box_q3) > 0:
          q3 = np.median(box_q3)
        else:
          q3 = None

      else:
        q1 = q3 = None

      if (q1 is not None) and (q3 is not None):
        iqr = q3 - q1

        if direction[el][i] < (median - 3 * iqr) or direction[el][i] > (median + 3 * iqr):
          # print(f'i={i} : direction[i]={direction[el][i]}, q1={q1}, q3={q3}, median={median}')
          anomaly[el] = np.append(anomaly[el], i)

  # Очистка и фильтрация списка выбросов
  filtered_anomaly = [None if sublist is None else [j for j in sublist if isinstance(j, int)] for sublist in anomaly]

  # Вывод информации о выбросах
  for i, sublist in enumerate(filtered_anomaly):
    if sublist is not None:
      # print(f"Выбросы: \'{names_of_dir[i]}\': {sublist}")
      print(f'{names_of_dir[i]}: длина изначальная ({len(direction[i])}), кол-во выбросов ({len(sublist)})')

  # Создание и преобразование уникального массива выбросов
  unic_anomaly = np.array(list({j for sublist in filtered_anomaly if sublist is not None for j in sublist}), dtype=int)

  # Удаление выбросов из массивов
  new_time = np.delete(time, unic_anomaly)
  new_direction = [np.delete(dir_list, unic_anomaly) for dir_list in direction]
  new_sigma = [np.delete(sig_list, unic_anomaly) for sig_list in sigma]

  return new_time, new_direction, new_sigma


# РЕГРЕССИОННЫЙ АНАЛИЗ
def heaviside(num):
  return np.heaviside(num, 1)


def diapason(direction): # динамическая ось У
  min_val = np.min(direction)
  max_val = np.max(direction)

  if max_val <= 200 and min_val >= -200:
    return -200, 200

  return min_val, max_val


def draw_time_series(pdf, interval, resolution, folder_name, name_of_station, time, direction, sigma, y, days_of_quake, V, Cm):
  names_of_dir = ['north', 'east', 'up']
  fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)

  for i, el in enumerate(ax):
    start, end = diapason(direction[i])
    el.axis([min(time), max(time), start, end])
    el.plot(time, direction[i], 'o', markersize=0.8, color='black')
    el.spines['top'].set_visible(False)
    el.spines['right'].set_visible(False)
    el.set_ylabel(names_of_dir[i] + '(mm)', fontweight='bold', verticalalignment='bottom')
  ax[2].set_xlabel("time", horizontalalignment='center')

  if interval == 1:
    error_down = np.array(direction) - np.array(sigma)
    error_up = np.array(direction) + np.array(sigma)

    for i, ax_el in enumerate(ax):
      ax_el.fill_between(time.flatten(), error_down[i].flatten(), error_up[i].flatten(), color='gray')

  for i, el in enumerate(ax): # построение модельной кривой
    el.plot(time, y[i], color='red', linewidth=0.8)

    for day in days_of_quake: # построение моментов землетрясений
      el.axvline(x=day, color='gray', linestyle='--', linewidth=0.5)

  plt.suptitle(name_of_station.upper(), fontsize=20, fontweight='bold')  # название станции

  mng = fig.canvas.manager # сохранение графиков
  mng.full_screen_toggle()
  if resolution == 0:
    plt.savefig(os.getcwd() + '/' + folder_name + '/' + name_of_station + '.jpg', dpi=300)

  elif resolution == 1:
    plt.savefig(pdf, format='pdf')

  else:
    root_graphic = Tk()
    root_graphic.title("Graphic")
    root_graphic.config(bg='#ffffff')
    root_graphic.geometry("+800+0")

    v_label = Label(root_graphic, text="Vn = {:.2f} (мм), Ve = {:.2f} (мм), Vu = {:.2f} (мм)".format(V[0].tolist(), V[1].tolist(), V[2].tolist()), font=("Arial", 14), bg="#ffffff")
    v_label.pack()
    sigma_label = Label(root_graphic, text="sigmaN = {:.2f} (мм), sigmaE = {:.2f} (мм), sigmaU = {:.2f} (мм)".format(Cm[0].tolist(), Cm[1].tolist(), Cm[2].tolist()), font=("Arial", 14), bg="#ffffff")
    sigma_label.pack()

    canvas = FigureCanvasTkAgg(fig, master=root_graphic)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def save_graph():
      plt.savefig(os.getcwd() + '/' + name_of_station + '.jpg', dpi=300)

    button = ttk.Button(root_graphic, text="Сохранить график", command=save_graph)
    button.pack()

    root_graphic.mainloop()


def regression(pdf, interval, resolution, name_of_station, folder_name, main_file, file_with_quakes=None):
  time, direction, sigma, day, year = dt.basic_initial(main_file)
  time, direction, sigma = count_irq(time, direction, sigma, day, year)
  days_of_quake, count_of_quake = dt.additional_initial(file_with_quakes, time) if file_with_quakes else ([], 0)
  print(f"Количество землетрясений на станции: {count_of_quake} (с {int(np.min(year))} по {int(np.max(year))} года)")

  try:
    # матрица А
    n = 6 + 2 * count_of_quake # количество столбцов в матрице А, count_of_quake - это кол-во скачков в связи с землетрясениями
    A = np.ones((len(time), n))
    A[:, 1] *= time
    A[:, 2] *= np.sin(2 * np.pi * time)
    A[:, 3] *= np.cos(2 * np.pi * time)
    A[:, 4] *= np.sin(4 * np.pi * time)
    A[:, 5] *= np.cos(4 * np.pi * time)
    A[:, 6:6 + count_of_quake] *= heaviside(time[:, np.newaxis] - days_of_quake)
    for i in range(len(time)):
      for j in range(n):
        if 6 + count_of_quake <= j < 6 + 2 * count_of_quake:
          if j != 6 + 2 * count_of_quake - 1:
            A[i][j] *= heaviside(time[i] - days_of_quake[j - 6 - count_of_quake]) * heaviside(days_of_quake[j - 5 - count_of_quake] - time[i]) * time[i]
          else:
            A[i][j] *= heaviside(time[i] - days_of_quake[j - 6 - count_of_quake]) * time[i]

    C = [np.eye(len(time)) * (sigma[k] ** 2) for k in range(3)]  # матрица С, создаем единичную матрицу

    C_inv_N = np.linalg.inv(C[0]) # обратная матрица
    C_inv_E = np.linalg.inv(C[1])
    C_inv_U = np.linalg.inv(C[2])

    Cm_N = np.linalg.solve(np.dot(np.dot(A.transpose(), C_inv_N), A), np.eye(A.shape[1])) # Результирующая ковариационная матрица
    Cm_E = np.linalg.solve(np.dot(np.dot(A.transpose(), C_inv_E), A), np.eye(A.shape[1]))
    Cm_U = np.linalg.solve(np.dot(np.dot(A.transpose(), C_inv_U), A), np.eye(A.shape[1]))

    x_N = np.dot(np.dot(np.dot(Cm_N, A.transpose()), C_inv_N), direction[0])
    x_E = np.dot(np.dot(np.dot(Cm_E, A.transpose()), C_inv_E), direction[1])
    x_U = np.dot(np.dot(np.dot(Cm_U, A.transpose()), C_inv_U), direction[2])

    y = [np.dot(A, x_N), np.dot(A, x_E), np.dot(A, x_U)]

    draw_time_series(pdf, interval, resolution, folder_name, name_of_station, time, direction, sigma, y, days_of_quake,
                     [x_N[1], x_E[1], x_U[1]], [Cm_N[1][1], Cm_E[1][1], Cm_U[1][1]])

    a = x_N[0], x_E[0], x_U[0]
    b = x_N[1], x_E[1], x_U[1]
    c = x_N[2], x_E[2], x_U[2]
    d = x_N[3], x_E[3], x_U[3]
    e = x_N[4], x_E[4], x_U[4]
    f = x_N[5], x_E[5], x_U[5]
    h = x_N[6:6 + count_of_quake], x_E[6:6 + count_of_quake], x_U[6:6 + count_of_quake]
    k = (x_N[6 + count_of_quake:6 + 2 * count_of_quake], x_E[6 + count_of_quake:6 + 2 * count_of_quake],
         x_U[6 + count_of_quake:6 + 2 * count_of_quake])
    sgm = [Cm_N[1][1], Cm_E[1][1], Cm_U[1][1]]
    return a, b, c, d, e, f, h, k, sgm

  except np.linalg.LinAlgError:
    print('Программа не смогла обработать станцию! Обратная матрица не считается')
    return 'error', 'error'
