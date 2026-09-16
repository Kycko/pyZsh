from   sys import exit as SYSEXIT
import pzexec.globals  as G
import pzexec.output   as O
import pzexec.runFuncs as RF

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  final = [G.sysBins['btrfs']]
  mode  = ''
  if args and args[0] == 'usage':
    if len(args) > 1:
      final.append('filesystem')
      mode = 's'
    else: print(SG.addArgMSG) ; return
  final += args
  RF.run(final,mode)

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['btrfs','arch','red'],
                 'cat' : 'BTRFS',
                 'desc': 'проверить занятое место',
                 'abbr': 'btrfs usage',
                 'help':  False}  # показывать ли "(есть HELP)"

    self.addArgMSG = 'Добавьте точку монтирования (например, / или /home/kycko/data)'
    self.tasks     = None
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
