# общие для нескольких скриптов функции вывода на экран разной информации

# НЕ МЕНЯТЬ ПОРЯДОК во избежание частичных импортов
from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.strings     as S
import pzexec.stringFuncs as SF
import pzexec.listFuncs   as LF

# шаблон, реализация try-except
class Help():
  # init + обёртки (реализация try-except)
  def __init__ (self,appFunc,taskdb:dict,args:list,debug:bool):
    # appFunc = какую функцию запустить, если все проверки пройдут
    self.db   = taskdb
    self.args = args
    try:
      # remove() выдаст ValueError, если флаг отсутствует
      args.remove(G.zshFlag) ; self.printZSH()
    except:
      self.debug = debug
      with self: appFunc(args)
  def __enter__(self): return self
  def __exit__ (self,type,val,tb):
    if type:  # если произошла ошибка
      self.printMain()
      if self.debug: print() ; print(S.separator) ; print()
      return not self.debug # 'return True' подавляет ошибку

  # вывод основной справки и дополнений zsh
  def getTask  (self):
    cur = self.db
    try:
      for arg in self.args: cur = cur[G.tk + arg]
    except: pass
    return cur
  def printMain(self):
    # в Globals() обозначаем:
    #   аргументы-подпункты должны начинаться с G.tk (например, '::revert')
    #   сообщения перед/после списка: '_pre':[]/'_post':[]
    #   разделитель abbr и desc: 'sep'
    def _getLeftLen(db  :dict):
      found = []
      for  tKey,tData in db.items():
        if tKey.startswith(G.tk): found.append(tData['abbr'])
      return LF.getMaxLen(found)
    def _getLine   (data:dict,leftLen:int):
      left  = SF.alignColored(data['abbr'],leftLen)
      final = f"  {left} {data['sep']} {data['desc']}"
      if data['help']: final += f' {S.ownHelp}'
      return final

    db      = self.getTask()
    leftLen = _getLeftLen(db)
    for line in db['_pre']: print(line)
    for  tKey,tData in db.items():
      if tKey.startswith(G.tk): print(_getLine(tData,leftLen))
    for line in db['_post']: print(line)
  def printZSH (self):
    for  k,d in self.getTask().items():
      if k.startswith(G.tk): print(f"{d['zsh']}:{d['desc']}")

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
