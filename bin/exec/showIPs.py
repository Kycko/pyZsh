from   sys import exit  as SYSEXIT
import pzexec.output    as O
import pzexec.strings   as S
import zshconf.runFuncs as RF

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  if args:
    try: RF.run('lsof -i -nP | grep -i --color=auto '+args[0],'hs')
    except KeyboardInterrupt: print(S.userCancel)
  else: print("Добавьте имя программы для grep'а")

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'прочее по ОС',
                 'desc': 'проверить, какие IP нужны программе',
                 'abbr': 'showIPs',
                 'help':  False}  # показывать ли "(есть HELP)"

    self.tasks = None
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
