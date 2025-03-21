import pandas as pd
import calendar
import os


def leap_year(year):
  if calendar.isleap(year):
    return 366
  else:
    return 365


def decimal_date(decimal):
  year = int(decimal)
  day = int((decimal - year) * leap_year(year) + 1)
  return year, day


def merge_data(folder_path, name_of_station):
  n = 1000
  file_n = pd.read_csv(folder_path + '/' + name_of_station + '.N', delim_whitespace=True, header=None, names=['time', 'north', 'sigmaN'])
  file_e = pd.read_csv(folder_path + '/' + name_of_station + '.E', delim_whitespace=True, header=None, names=['time', 'east', 'sigmaE'])
  file_u = pd.read_csv(folder_path + '/' + name_of_station + '.U', delim_whitespace=True, header=None, names=['time', 'up', 'sigmaU'])

  file_n['north'], file_n['sigmaN'] = file_n['north'] / n, file_n['sigmaN'] / n
  file_e['east'], file_e['sigmaE'] = file_e['east'] / n, file_e['sigmaE'] / n
  file_u['up'], file_u['sigmaU'] = file_u['up'] / n, file_u['sigmaU'] / n

  merged_data = file_n.merge(file_e, on='time', how='inner').merge(file_u, on='time', how='inner')

  merged_data[['year', 'day']] = pd.DataFrame(merged_data['time'].apply(lambda x: decimal_date(x)).to_list(), index=merged_data.index)
  merged_data = merged_data[['time', 'year', 'day', 'north', 'east', 'up', 'sigmaN', 'sigmaE', 'sigmaU']]
  merged_data.to_csv(folder_path + '/' + name_of_station + '_GPSRaw.neu', sep=' ', index=False, header=False)


if __name__ == '__main__':
  folder_path = input("Введите путь до папки, файлы которой хотите обработать: ")
  print(folder_path)
  content = os.listdir(folder_path)
  # Фильтрация элементов списка content, чтобы исключить ".DS_Store"
  content = [el for el in content if el != '.DS_Store']

  name_of_stations = list(set([el[:-2] for el in content]))
  print(name_of_stations)

  for el in name_of_stations:
    merge_data(folder_path, el)
