from   sys import exit    as SYSEXIT
import pzexec.output      as O
import pzexec.stringFuncs as SF
import pzexec.strings     as S
# из pzexec скрипт почему-то не видит G.myBins
import zshconf.globals    as G

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  def _print(db:dict,abbrLen:int):
    def _cat    (cat :str,linesColor:str):
      final = f' {G.termSymbols[0]}──────[{cat}]'
      print(SF.color(final,**linesColor))
    def _script (name:str,desc:str,last:bool,linesColor:str):
      pre   = f'{G.termSymbols[1]}' if last else '│'
      pre   = SF.color(f'{pre}',**linesColor)
      start = SF.color(f'{name.ljust(abbrLen)}','grn')
      print(f' {pre} {start} : {desc}')

    linesColor = {'colr':'grn','bold':False}
    # задаём порядок для тех категорий, которые я хочу видеть сверху
    # остальные добавляем в любом порядке
    priorCats = ['пакеты в ОС','разработка','BTRFS']
    for  cat in db.keys():
      if cat not in priorCats: priorCats.append(cat)

    for cat in priorCats:
      # приоритетная категория может отсутствовать в db
      if cat in db.keys():
        _cat(cat,linesColor)
        names = sorted(list(db[cat].keys()))
        for name in names:
          last = name == names[-1]
          _script(name,db[cat][name],last,linesColor)
    print() # в конце пустая строка
  # {категория:{upd:описание,
  #             ins:описание,
  #             ...},...}
  db      = {}
  abbrLen = 0
  for  pr in G.myBins.values():
    if pr['abbr'] != 'help':
      if len(pr['abbr']) > abbrLen : abbrLen = len(pr['abbr'])
      if pr['cat'] not in db.keys(): db[pr['cat']] = {}
      final = pr['desc']
      if pr['help']: final += f' {S.ownHelp}'
      db[pr['cat']][pr['abbr']] = final
  _print(db,abbrLen)

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    # этому скрипту больше ничего не надо
    self.dist  = {'dist':['arch','red'],'abbr':'help'}
    self.tasks = None
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
