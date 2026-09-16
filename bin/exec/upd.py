from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.listFuncs   as LF
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF
import pzexec.strings     as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  def _ROcheckUpd():
    count = len(LF.filterEnds(_run('check'),'updates',False))
    color = ('blu','grn')[bool(count)]
    print('found.....',end='',flush=True)
    print(SF.color(str(count),color))
    return count
  def _run(key:str):
    v = SG.tasks[key] # v = values
    print(SF.color(v['header'],'ylw',bold=False))
    return RF.run(**v[G.distType])

  try:
    if G.isArch: _run('upd')
    else:
      _run('cache')
      if _ROcheckUpd():
        if not _run('upd'): print() ; _run('autorem')
      else: print(f'  {SG.noUpdates}')
  except KeyboardInterrupt: print(S.userCancel)

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'пакеты в ОС',
                 'desc': 'обновление пакетов',
                 'abbr': 'upd',
                 'help':  False}  # показывать ли "(есть HELP)"

    self.noUpdates = SF.color('no updates available!','blu')

    self.tasks = {
      'cache'  :{
        'header':'----- updating cache',
        'arch'  :{'cmd':['yay','-Sy'      ],'args':'' },
        'red'   :{'cmd':['dnf','makecache'],'args':'s'}
        },
      'check'  :{
        'header':'----- checking updates',
        'red'   :{'cmd':['dnf','check-update'],'args':'st'}
        },
      'upd'    :{
        'header':'----- running upgrade',
        'arch'  :{'cmd':['yay','-Syu'   ],'args':''  },
        'red'   :{'cmd':['dnf','upgrade'],'args':'sr'}
        },
      'autorem':{
        'header':'----- autoremove',
        'red'   :{'cmd':['dnf','autoremove'],'args':'s'}
        }
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
