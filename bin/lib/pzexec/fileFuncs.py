# функции чтения, записи и импорта библиотек

from   sys import exit as SYSEXIT
from   zshconf.fileFuncs import *
import pzexec.globals  as G
import pzexec.strings  as S

def write_toFile(lines,file:str,justAdd=False):
  # если justAdd=True, предыдущие данные останутся в файле
  if isinstance(lines,str): lines = [lines]
  mode = ('w','a')[justAdd]

  with open(file,mode,encoding='utf-8') as f:
    # один f.writelines() работает быстрее,
    # чем множество f.write() внутри цикла
    f.writelines(f'{line}\n' for line in lines)
def getSpec     ():
  # возвращает путь к spec-файлу  из ~/rpmbuild/SPECS
  dir   = G.dirs['work']['rbuild']['specs']
  final = list(dir.glob('*.spec'))
  # возвращает ТОЛЬКО если нашли РОВНО один spec-файл
  if len(final) == 1: return final[0]
  else              : print(S.oneSpec)

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
