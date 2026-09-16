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
def getPkg      (end:str):  # возвращает нужный пакет из ~/rpmbuild/SRPMS
  # здесь не получается использовать LF и SF: циклический импорт
  dir   = G.dirs['work']['rbuild']['srpms']
  files = []
  for  file in dir.iterdir():
    # проверяем окончание '.src.rpm', поэтому не через file.suffix
    if file.name.endswith(end): files.append(file)

  if len(files) == 1: return files[0]
  else:
    cl  = G.colors['term']
    msg = f"В {dir}{cl['red']}{cl['bld']} должен быть один пакет '{end}'{cl['rst']}"
    print(msg)
def getRPMs     (toStrings=False):
  # возвращает ВСЕ пакеты из ~/rpmbuild/RPMS
  final = []
  for  dir in G.dirs['work']['rbuild']['rpms'].iterdir():
    if dir.is_dir():
      for  file in dir.glob('*.rpm'):
        final.append(str(file) if toStrings else file)
  return final

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
