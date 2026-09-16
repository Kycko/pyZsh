# разные глобальные функции, не подходящие для других модулей

from   copy import deepcopy
from   sys  import exit as SYSEXIT
import pzexec.globals   as G
import pzexec.runFuncs  as RF

def getTask(args:list, db:dict):
  # понадобится не во всех скриптах
  if args:
    args = deepcopy(args)
    cur  = db
    try:
      # сперва проверяем, только потом удаляем pop'ом
      while args: cur = cur[G.tk + args[0]] ; args.pop(0)
    except: pass
    return cur,args
  else: RF.raiseError()
def getIB  (type:str,index:int):  # IB = index/boolean
  # служебная функция; возвращает сам index либо true/false
  return index if type == 'index' else index >= 0

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
