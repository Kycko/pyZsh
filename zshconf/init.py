# этот скрипт вызывается при запуске оболочки
# если надо запустить tmux, запускает его
# ИНАЧЕ просто выполняет импорт всех модулей из ./python

from pathlib import Path
from sys     import path as sysPath

############ подключаем нужные каталоги
# вторая библиотека нужна для импорта переменных из bin/exec'ов
cur    = Path(__file__).resolve().parent
py     = cur/'python'
binlib = cur.parent/'bin/lib'
for lib in [py/'lib',binlib]:
  lib = str(lib)
  # добавляем библиотеки в PATH
  if lib not in sysPath: sysPath.insert(0,lib)
import zshconf.fileFuncs as FF
import zshconf.globals   as G

############ создаём списки с абсолютными путями
pre  = [] # ПЕРЕД tmux запускаем 00-09
post = [] # остальные 10-99
for f in py.glob('*.py'):
  fList = pre if f.stem.startswith('0') else post
  fList.append(f)
pre .sort()
post.sort()

############## запуск
# это запускаем в любом случае
for file in pre: FF.importModule(file)

tmuxBin = G.sysBins['tmux']
if G.guiterm or G.inTmux or not tmuxBin:
  for file in post: FF.importModule(file)
else: print(f'exec {tmuxBin} -u') # запускаем tmux
