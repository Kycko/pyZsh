import os
from   sys      import exit as SYSEXIT
from   datetime import datetime
from   time     import time
import pzexec.fileFuncs     as FF
import pzexec.globals       as G
import pzexec.listFuncs     as LF
import pzexec.output        as O
import pzexec.stringFuncs   as SF
import pzexec.strings       as S
import pzexec.runFuncs      as RF
if not G.isArch: import pzexec.packages as PKG

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  task = SG.tasks[G.tk + args[0]]
  if task['func'] is None: RF.run(**task['cmd'][G.distType])
  else:
    try: task['func'](args)
    except KeyboardInterrupt: print(S.userCancel)

def fork (args:list):
  def _run(task:str): pkg() if task == 'pkg' else pyZsh()
  task = args.pop(0)
  # ↓ добавить ЛЮБОЙ аргумент, чтобы запустить отдельным процессом
  if args:
    if os.fork() == 0:
      os.setsid()         # отрезаем связь с сессией терминала
      if os.fork() == 0:  # запускаем в отдельных процессах
        # эта конструкция обязательна, чтобы в finally закрыть процесс
        try    : _run(task)
        finally: os._exit(0)
      os._exit(0)
  else:
    _run(task)
    print(SF.color('Обновлено!','grn'))
    status(args)
def write(file,status:bool=None): # file = объект Path
  final = str(int(time()))
  if status is not None: final += f' {status}'
  FF.write_toFile(final,file)
def pkg  ():
  os.makedirs(str(G.dirs['cache']['pkg']),exist_ok=True)
  cFiles = G.files['cache']

  if G.isArch: pkgs = RF.run(['yay','-Slq'],'t')
  else:
    base = PKG.DNF()  # "прогреваем" кеш DNF
    if base.dbLoaded:
      # получаем только уникальные имена доступных пакетов
      pkgs = set(pkg.name for pkg in base.api.sack.query().available())

  if pkgs:  # на всякий случай, чтобы не перезаписывать пустотой
    pkgs = LF.rmBlanks(sorted(pkgs))
    FF.write_toFile(pkgs,cFiles['pkglist'])
    # записываем текущий timestamp
    write(cFiles['updTime']['pkg'])
def pyZsh():  # проверяет наличие обновлений моего pyZsh
  # проверка нужна, чтобы в виртуалках не запускалось
  os.makedirs(str(G.dirs['cache']['root']),exist_ok=True)

  preCMD = [G.sysBins['git'],'-C',str(G.dirs['repos']['pyZsh']['root'])]
  # скачиваем изменения из удаленного репозитория без слияния
  RF.run(preCMD + ['fetch'],'eo')
  # финальный вывод
  status = not RF.run(preCMD+['log','@..@{u}','--oneline'],'et')[0]
  write(G.files['cache']['updTime']['pyZsh'],status)

def status(args:str): # args[0] = 'status'
  def _get(type:str,manual:bool):
    def _return(days:int):
      # ключ для S.cache{}
      cKey = ['old','fresh'][days < SG.timeout]
      if data and data[0] == 'False': cKey = 'old'

      # как давно обновлён
      if   days > 4: time = f'{days} дней назад'
      elif days > 1: time = f'{days} дня назад'
      elif days    : time =  '1 день назад'
      else         : time =  'сегодня'
      if days >= SG.timeout:  time = SF.color(time,'red',True)

      # вывод
      return f'{S.cache[cKey]} (обновлён {time})'
    file = G.files['cache']['updTime'][type]
    if manual and not file.is_file():  # запустили проверку статуса вручную
      return S.noFile.lower()
    else:
      try   : data = FF.readFile(file)[0].strip().split()
      except: return SF.color("обновите данные ('clr')",'red',True)

      diff = datetime.now() - datetime.fromtimestamp(int(data.pop(0)))
      days = diff.days

      return _return(days)
  if len(args) > 1 and args[1] == 'fastfetch': print(_get(args[2],False))
  else:
    maxLen = LF.getMaxLen(SG.caches,False)
    for type in SG.caches:
      print(f'{type.ljust(maxLen)} : {_get(type,True)}')

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    def _abbr      (txt   :str): return SF.color(txt,'cya',True)
    def _statusDesc(dnfstr:str,pyZshstr:str):
      pre   = 'посмотреть статус'
      dnf   = 'dnf'   in self.caches
      pyZsh = 'pyZsh' in self.caches

      if   dnf and pyZsh: return f'{pre} кешей {dnfstr} и {pyZshstr}'
      elif dnf          : return f'{pre} кеша {dnfstr}'
      elif pyZsh        : return f'{pre} кеша {pyZshstr}'
      else              : return ''

    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'пакеты в ОС',
                 'desc':f'обновление кешей пакетов/pyZsh',
                 'abbr': 'updCache',
                 'help':  True} # показывать ли "(есть HELP)"

    # спустя сколько дней считаем кеш слишком старым
    # (для функции status)
    self.timeout = 4

    rootcache = 'обновить системный кеш пакетов'
    usercache = 'обновить кеш пакетов пользователя (мой кастомный)'
    if not G.isArch:
      rootcache += f" {SF.color('root','red',True)}'а"

    dnfstr   = SF.color('DNF'  ,'red',True)
    pyZshstr = SF.color('pyZsh','grn')

    self.tasks = {
      '_pre'   :[S.cmdsAvailable],
      '_post'  :[],
      'func'   :None,
      'cmd'    :None,
      '::sys'  :{'_pre':[],'_post':[],
                 'abbr':_abbr('sys'),'zsh':'sys',
                 'sep' :':',
                 # здесь без DNF, это показывается и в Арче
                 'desc':rootcache,
                 'help':False,
                 'func':None,
                 'cmd' :{'arch':{'cmd':['yay','-Sy']},
                         'red' :{'cmd':['dnf','makecache'],'args':'s'}}},
      '::pkg'  :{'_pre':[],'_post':[],
                 'abbr':_abbr('pkg'),'zsh':'pkg',
                 'sep' :':',
                 'desc':usercache,
                 'help':False,
                 'func':fork}
      }

    self.caches = ['pkg']

    if not G.inVirt:
      self.caches.append('pyZsh')
      self.tasks['::pyZsh'] = {
        '_pre':[],'_post':[],
        'abbr':_abbr('pyZsh'),'zsh':'pyZsh',
        'sep' :':',
        'desc':f'обновить кеш {pyZshstr} (статус репозитория)',
        'help':False,
        'func':fork
        }

    # хочу, чтобы status был последним, поэтому здесь
    self.tasks['::status'] = {
      '_pre':[],'_post':[],
      'abbr':_abbr('status'),'zsh':'status',
      'sep' : ':',
      'desc':_statusDesc(dnfstr,pyZshstr),
      'help':False,
      'func':status
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
