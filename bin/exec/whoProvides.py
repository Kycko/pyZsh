from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.output      as O
import pzexec.stringFuncs as SF
import pzexec.strings     as S
import zshconf.runFuncs   as RF

# через python dnf/rpm сложно, поэтому вызываем напрямую

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  task,query = args
  RF.run(SG.tasks[G.tk+task]['cmd'] + [query])

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['red'],
                 'cat' : 'пакеты в ОС',
                 'desc': 'какой пакет предоставляет файл',
                 'abbr': 'whoProvides',
                 'help':  True} # показывать ли "(есть HELP)"

    cnc    = SF.color('конкретному' ,'udl',False)
    quoted = SF.color('в кавычках'  ,'udl',False)
    rpmqf  = SF.color('rpm -qf'     ,'ylw',False)
    dnfpr  = SF.color('dnf provides','ylw',False)

    self.tasks = {
      '_pre' :[S.cmdsAvailable],
      '_post':[],
      'func' :None,
      'cmd'  :None,
      '::l'  :{'_pre' :[],'_post':[],
               'abbr' :f'l + путь к {cnc} файлу',
               'zsh'  : 'l',
               'sep'  : ':',
               'desc' :f'локальный поиск     (аналог: {rpmqf})',
               'help' :False,
               'cmd'  :['rpm','-qf']},
      '::r'  :{'_pre' :[],'_post':[],
               'abbr' :f"r + условный файл {quoted} ('*/file')",
               'zsh'  :'r',
               'sep'  :':',
               'desc' :f'поиск в репозитории (аналог: {dnfpr})',
               'help' :False,
               'cmd'  :['dnf','provides']}
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
