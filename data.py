import numpy as np
import calendar
import pandas as pd


def leap_year(year): # проверка на високосность года
  if calendar.isleap(year):
    return 366
  return 365


def decimal_date(year, day):
  time_event = []

  for i in range(0, len(year)):
    time_event.append(np.trunc((year[i] + (day[i] - 0.5) / leap_year(year[i])) * 1e5) / 1e5)

  return time_event


def basic_initial(file_name, chunk_size=1000):
  data = np.loadtxt(file_name, skiprows=1, usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8), dtype=np.float32)
  time, year, day, north, east, up, sigmaN, sigmaE, sigmaU = np.split(data, 9, axis=1)
  n = 1000
  direction = [north * n, east * n, up * n]
  sigma = [sigmaN * n, sigmaE * n, sigmaU * n]
  return time.flatten(), direction, sigma, day.flatten(), year.flatten()


def additional_initial(file_name, time):
  data = np.loadtxt(file_name, skiprows=1, usecols=(0, 1), dtype=np.float32)
  year, day = np.split(data, 2, axis=1)
  time_event = decimal_date(year, day)

  days = np.array([])
  for j in range(len(time_event)):
    if min(time) <= time_event[j] <= max(time):
      days = np.append(days, time_event[j])
  return days, len(days)
