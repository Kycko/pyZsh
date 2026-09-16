from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.listFuncs   as LF
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF

# основные функции
def main(args:list):
  if G.isArch:
    found = LF.rmBlanks(RF.run(['yay','-Qdtq'],'t'))
    if found: RF.run(['yay','-Rns'] + found)
    else:
      no = SF.color('нет','grn',True)
      print(f'Лишних пакетов в системе {no}')
  else: RF.run(['dnf','autoremove'],'s')

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'пакеты в ОС',
                 'desc': "удаление 'лишних' пакетов",
                 'abbr': 'autorem',
                 'help':  False}  # показывать ли "(есть HELP)"

    self.tasks = None
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
