from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  if G.guiterm: RF.run([f"DIFFPROG={G.sysBins['meld']}",'pacdiff'],'s')
  else: # в TTY сложно настроить, отключаем
    print('pacnew ' + SF.color('работает только в GUI','red',True))

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch'],
                 'cat' : 'пакеты в ОС',
                 'desc': 'обработка файлов pacnew/pacsave/...',
                 'abbr': 'pacnew',
                 'help':  False}  # показывать ли "(есть HELP)"

    self.tasks = None
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
