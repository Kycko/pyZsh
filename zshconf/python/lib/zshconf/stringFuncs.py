# общие функции обработки строк

from sys import exit as SYSEXIT

# цвета
def fColor(colr:str,bold=False):
  # преобразует цвет в f-строку (вида %B%F{yellow})
  final  = '%B' if bold else '%b'
  final += '%F{' + colr + '}'
  return final

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
