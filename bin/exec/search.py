from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.listFuncs   as LF
import pzexec.output      as O
import pzexec.stringFuncs as SF
import pzexec.strings     as S
import pzexec.runFuncs    as RF

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  task  = SG.tasks[G.tk + args[0]]
  query = args[1]

  checker = task['local'] and not G.isArch
  fRun    = {'cmd' :task['cmd'],
             'args':['e','te'][checker]}
  if G.isArch or not task['local']: fRun['cmd'].append(query)
  found = RF.run(**fRun)

  # local в RO надо grep'ать отдельно, repo - нет
  if checker:
    for line in LF.filter_byStr(found,query,colorize='ylw'):
      print(line)

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'пакеты в ОС',
                 'desc': 'поиск пакетов',
                 'abbr': 'search',
                 'help': True}  # показывать ли "(есть HELP)"

    query = SF.color('Добавьте строку для поиска','red',True)
    self.tasks = {
      '_pre'   :[S.cmdsAvailable],'_post':[],
      'func'   :None,'cmd':None,
      '::local':{
        '_pre' :[query],'_post':[],
        'abbr' :'local','zsh':'local','sep':':',
        'desc' :'поиск локальный','help':False,
        'cmd'  :['yay','-Qs'] if G.isArch else ['dnf','list','--installed'],
        'local':True
        },
      '::repo' :{
        '_pre' :[query],'_post':[],
        'abbr' :'repo','zsh':'repo','sep':':',
        'desc' :'поиск в репозиториях','help':False,
        'cmd'  :['yay','-Ss'] if G.isArch else ['dnf','search'],
        'local':False
        }
      }

    if G.isArch:
      self.tasks['::file'] = {
        '_pre' :[query],'_post':[],
        'abbr' :'file','zsh':'file','sep':':',
        'desc' :'поиск по файлу (только имя либо полный путь)',
        'help' :False,
        'cmd'  :['pkgfile','-s'],
        'local':False,
        'zSugg':'_path'
        }
    else:
      self.tasks['::rv'] = {
        '_pre' :[query],'_post':[],
        'abbr' :'rv','zsh':'rv','sep':':',
        'desc' :'repo + все версии','help':False,
        'cmd'  :['dnf','search','--showduplicates'],
        'local':False
        }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
