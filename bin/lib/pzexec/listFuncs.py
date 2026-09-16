# общие функции обработки списков

from   copy import deepcopy
from   sys  import exit   as SYSEXIT
import pzexec.stringFuncs as SF

# фильтры
def filter_byStr(list:list,txt:str,lower=True,strip='',colorize='',bold=False):
  # возвращает список только тех элементов, в которых есть txt
  # strip может быть ''/'a'(для элементов list)/'b'(для txt)/'ab'
  # в colorize можно передать название цвета из G.colors, чтобы подсветить найденное
  #   в этом случае будет работать параметр bold
  final = []
  for item in list:
    if SF.findSub(item,txt,lower=lower,strip=strip):
      if colorize: item = SF.findToColor(item,txt,colorize,bold)
      final.append(item)
  return final

# проверка данных
def getMaxLen(list:list,rmColors=True):
  if rmColors: list = cutColors(list)
  return max(map(len,list),default=0)

# преобразование
def cutColors(list:list):
  return [SF.cutColors(item) for item in list]
def rmBlanks (list:list):
  wcopy = deepcopy(list)
  while '' in wcopy: wcopy.remove('')
  return wcopy

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
