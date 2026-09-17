# функции инициализации globals, для создания глобальных переменных

from   copy import deepcopy
from   os   import environ,statvfs
from   sys  import exit  as SYSEXIT
import zshconf.fileFuncs as FF
import zshconf.runFuncs  as RF

# проверка окружения
def sudo(isRoot:bool): return '' if isRoot else 'sudo '
def getDistro(file):  # file = объект Path
  def _errExit(file):
    RF.confError(f'файл {file} не найден или недоступен')
  try:
    for line in FF.readFile(file):
      if 'Arch Linux' in line: return 'arch'
      else:
        res = line.split('VERSION_ID="')
        if len(res) > 1:
          return res[1][0]  # второй элемент, первый символ
    _errExit(file)  # если не нашли нужную инфу
  except: _errExit(file)
def checkGUI  ():
  # проверяем 'echo $TERM'
  term    = environ.get('TERM','').lower()
  inTmux  = environ.get('TMUX') is not None
  guiterm = term != 'linux' and not inTmux
  return guiterm,inTmux
def checkSSH  ():
  res = environ.get('SSH_CONNECTION')
  if res: return res.split()[2].split('.')[-1]
def checkBTRFS():
  # здесь я использую очень простую проверку
  # если будет работать неправильно, заменить на сложную, но надёжную
  vfs = statvfs('/')
  # если inodes равны 0 — это практически со 100% вероятностью BTRFS
  return vfs.f_files == 0 and vfs.f_ffree == 0
def binAlias(dir,onBTRFS:bool,distType:str,initfile):
  # dir и initfile = объекты Path
  db = {}
  for f in dir.glob('*.py'):
    props    = FF.importModule(f).SG.dist
    chkBTRFS = onBTRFS or 'btrfs' not in props['dist']
    if distType in props['dist'] and chkBTRFS:
      # импорт ins.py перезаписывает значения скрипта rem.py
      # поэтому отделяем данные при помощи deepcopy()
      db[f.stem] = deepcopy(props)
      db[f.stem]['launch'] = f'python3 {initfile} {f.name} "$@"'
  return db

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
