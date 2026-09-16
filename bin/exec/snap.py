from   sys import exit    as SYSEXIT
import pzexec.fileFuncs   as FF
import pzexec.globals     as G
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF
import pzexec.strings     as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main   (args:list):
  task = SG.tasks[G.tk+args.pop(0)]
  if len(args) < task['args']: RF.raiseError()
  else:
    args = args[:task['args']]
    if task['func']: task['func'](args)
    else:
      try: RF.run(['snapper'] + task['cmd'] + args,'s')
      except KeyboardInterrupt: print(S.userCancel)
def restore(args:list):
  def _findRoot():
    # находит корень и выдаёт '/dev/nvme0n1p3'
    for line in FF.readFile(G.files['mounts']):
      parts = line.split()
      if len(parts) > 1 and parts[1] == '/': return parts[0]
  def _print(dirs:dict,snapnum:str):
    cur     = SF.color(dirs['cur']   .stem,'grn',True)
    broken  = SF.color(dirs['broken'].stem,'red',True)
    snapnum = SF.color(snapnum            ,'blu',True)

    print(S.separator)
    print(f'Текущий {cur} перемещён в {broken}, снимок {snapnum} восстановлен.')
    print(f'Можно перезагрузить ПК для загрузки в восстановленный {cur}.')

  root = _findRoot()
  if root:
    snapnum = args[0]
    d       = G.dirs['snaps']
    cur     = str(d['cur'])
    broken  = str(d['broken'])
    fsnap   = d['from'].replace('$num$',snapnum)

    RF.run(['mount',root,'/mnt'],'s')
    if d['broken'].exists(): RF.run(['rm','-rf',broken],'s')
    RF.run(['mv',cur,broken],'s')
    RF.run([G.sysBins['btrfs'],'subvolume','snapshot',fsnap,cur])

    _print(d,snapnum)
  else:
    print('Не удалось определить корневое устройство')
    print(SF.color('Выполните восстановление вручную','red',True))

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist   = {'dist':['btrfs','arch','red'],
                   'cat' : 'BTRFS',
                   'desc': 'снимки файловой системы',
                   'abbr': 'snap',
                   'help':  True} # показывать ли "(есть HELP)"

    sam         = SF.color('САМ','ylw')
    restoreDesc = f'restore {sam} смонтирует в /mnt устройство (/dev/...) текущего корня.'

    shot        = SF.color( 'снимок'         ,'blu',True)
    shotnum     = SF.color( 'номер_снимка'   ,'blu',True)
    desc        = SF.color("'описание'"      ,'grn',True)
    newdesc     = SF.color("'новое_описание'",'grn',True)

    self.tasks  = {
      '_pre'     :[S.cmdsAvailable],
      '_post'    :[S.separator,restoreDesc],
      'func'     :None,'cmd':None,
      '::list'   :{
        '_pre'   :[],'_post':[],
        'abbr'   :'list','zsh':'list','sep':':',
        'desc'   :'показать список снимков','help':False,
        'func'   :None,
        'cmd'    :['list','--columns',
                 'number,description,cleanup,type,date,read-only'],
        'args'   :0 # сколько аргументов надо добавить к cmd
        },
      '::new'    :{
        '_pre'   :[],'_post':[],
        'abbr'   :f'new    {desc}','zsh':'new','sep':':',
        'desc'   :'создать read-only снимок','help':False,
        'func'   :None,
        'cmd'    :['create','--read-only','-d'],
        'args'   :1 # сколько аргументов надо добавить к cmd
        },
      '::rename' :{
        '_pre'   :[],'_post':[],
        'abbr'   :f'rename {newdesc} {shotnum}','zsh':'rename','sep':':',
        'desc'   :'изменить описание','help':False,
        'func'   :None,
        'cmd'    :['modify','--description'],
        'args'   :2 # сколько аргументов надо добавить к cmd
        },
      '::del'    :{
        '_pre'   :[],'_post':[],
        'abbr'   :f'del     {shotnum}','zsh':'del','sep':':',
        'desc'   :f'удалить {shot}','help':False,
        'func'   :None,
        'cmd'    :['delete'],
        'args'   :1 # сколько аргументов надо добавить к cmd
        },
      # пробовал спрятать restore, когда ФС не в режиме readonly, но это сложно
      '::restore':{
        '_pre'   :[],'_post':[],
        'abbr'   :f'restore {shotnum}','zsh':'restore','sep':':',
        'desc'   :f'восстановить {shot}','help':False,
        'func'   :restore,
        'cmd'    :None,
        'args'   :1 # сколько аргументов надо добавить к cmd
        }
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
