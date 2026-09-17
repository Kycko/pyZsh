from   sys import exit    as SYSEXIT
import pzexec.fileFuncs   as FF
import pzexec.output      as O
import pzexec.stringFuncs as SF
import pzexec.strings     as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(pkgs:list):
  def _run(pkgs:list):
    if pkgs[0] == '-f':
      try   : pkgs = FF.readFile(pkgs[1])
      except: print(S.noFile) ; return
    pkgs = progress.checkPkgs  (pkgs,False)
    pkgs = progress.getDeps    (pkgs,'p')
    pkgs = progress.whoRequires(pkgs)
    progress  .show_whoRequires(pkgs)
  for line in SG.help['main']: print(line)
  if len(pkgs) > 1 or (pkgs and pkgs[0] != '-f'): _run(pkgs)
  else: print(SG.help['addPkg'])

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['red'],
                 'cat' : 'пакеты в ОС',
                 'desc': 'проверить, кому требуется пакет',
                 'abbr': 'whoRequires',
                 'help': True}  # показывать ли "(есть HELP)"

    self.tasks = None

    pkg  = SF.color('Добавьте пакет(ы)','red',True)
    file = SF.color('-f ФАЙЛ'          ,'ylw')

    self.help = {
      'main'  :['В названии пакета ВАЖНА КАПИТАЛИЗАЦИЯ!',
                S.separator],
      'addPkg':f'{pkg} или {file} для чтения списка пакетов из файла'
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/

class Help(O.Help):
  def printZSH(self):
    if self.args and self.args[0] == '-f': print('___path')
    else: super().zshPackages(False)
progress = O.Progress()

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
