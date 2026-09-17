# общая логика для ins и rem

from   sys import exit as SYSEXIT
import pzexec.globals  as G
import pzexec.strings  as S
import pzexec.runFuncs as RF

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  if args:
    props = SG.tasks[G.distType]
    props['cmd'] += args
    try: RF.run(**props)
    except KeyboardInterrupt: print(S.userCancel)
  else: print(S.addPkg)

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'пакеты в ОС',
                 'desc': None,
                 'abbr': None,
                 'help': False} # показывать ли "(есть HELP)"

    self.tasks = None
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
