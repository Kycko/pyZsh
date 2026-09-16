# общие функции обработки строк

from   sys import exit as SYSEXIT
import pzexec.globals  as G

# в агрументах используем название colr
# чтобы не было путаницы с функцией color

# преобразование
def color(string:str,colr:str,bold=False):
  colors          = G.colors['term']
  final           =   colors[colr]
  if bold: final +=   colors['bld']
  final          +=   str(string) # защита от TypeError
  final          +=   colors['rst']
  return final

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
