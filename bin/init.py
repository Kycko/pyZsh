# входная точка для всех запускаемых скриптов

import sys
from   copy    import deepcopy
from   pathlib import Path

############ подключаем нужные каталоги
# подключаем библиотеку zshconf, её активно используем

# в РО нельзя всё удалять из sys.argv, возникает ошибка
# поэтому делаем копию и работаем с ней
args    = deepcopy(sys.argv)
cur     = Path(args.pop(0)).parent
conflib = cur.parent/'zshconf/python/lib'
for lib in [cur/'lib',conflib]:
  lib = str(lib)
  # добавляем библиотеки в PATH
  if lib not in sys.path: sys.path.insert(0,lib)
import zshconf.fileFuncs as FF
import zshconf.globals   as G

############ запускаем (импортом) нужный скрипт
mod = FF.importModule(G.dirs['repos']['pyZsh']['exec']/args.pop(0))
mod.Help(mod.main,mod.SG.tasks,args,debug=False)
