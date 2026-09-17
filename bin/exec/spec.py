import sys
from   datetime import datetime
from   locale   import LC_TIME,setlocale
import pzexec.fileFuncs   as FF
import pzexec.globalFuncs as GF
import pzexec.globals     as G
import pzexec.listFuncs   as LF
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF
import pzexec.strings     as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  def _mod (task:dict,fArgs:list):  # доп. действия ПЕРЕД запуском
    if 'rpmbuild'   in task['mod']: RF.installRPMbuild()
    if 'getSpecArg' in task['mod']:
      if fArgs: task['cmd'] += f' {fArgs[0]}'
      else:
        print(f'Добавьте путь к {SG.specabbr}-файлу')
        sys.exit()
    if 'addArg'     in task['mod']: task['cmd'] += fArgs
    if 'fin'        in task['mod'] and sys.stdout.isatty():
      # isatty() специфичен для этого скрипта
      # он проверяет, ПЕРЕНАПРАВЛЯЕТСЯ ли вывод ( через >, например)
      task['cmd'] += ' | highlight --out-format=xterm256'
      task['cmd'] += ' --style=kellys --syntax=spec --quiet --force'
      task['cmd'] += ' | less -R'
    if 'getSpec'    in task['mod']: task['cmd'].append(str(FF.getSpec()))
    # if 'check'      in task['mod']: specCheck.main(fArgs)
  def _post():                      # и после запуска
    if 'date' in task['mod']:
      file = G.files['mail'][G.distType]
      try   : email = FF.readFile(file)[0]
      except: print(f'{S.noFile} {file}') ; return

      start = '' if G.isArch else '* '

      # setlocale важен, чтобы получить на английском
      setlocale(LC_TIME,'en_US.UTF-8')
      date = datetime.now().strftime('%a %b %d %Y')

      print(f'{start}{date} Anton Samartsev <{email}> - 0:')

  task,fArgs = GF.getTask(args,SG.tasks)
  _mod(task,fArgs)
  try: RF.run(task['cmd'],task['args'])
  except  KeyboardInterrupt: print() ; print(S.userCancel)
  except: pass
  _post()

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    def _descriptionCMDs():
      db = {}
      for  t,task in self.tasks.items():
        if t.startswith(G.tk) and task['cmd']:
          db[t] = task['cmd']
          if isinstance(db[t],list): db[t] = ' '.join(db[t])

      mLen = LF.getMaxLen([cmd for cmd in db.values()],False)

      for  t,task in self.tasks.items():
        if t.startswith(G.tk):
          try:
            prefix = SF.color(db[t].ljust(mLen),'ylw')
            prefix = f'[= {prefix}] '
          except: prefix = ''.ljust(mLen+5)
          task['desc'] = prefix + task['desc']
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'разработка',
                 'desc': 'разное для написания spec-файлов',
                 'abbr': 'spec',
                 'help':  True} # показывать ли "(есть HELP)"

    changelog     = SF.color('changelog','blu',True)
    self.specabbr = SF.color('spec'     ,'red',True)

    self.tasks = {
      '_pre'  :[S.cmdsAvailable],'_post':[],
      'func'  :None,'cmd':None,
      '::date':{
        '_pre':[],'_post':[],
        'abbr': 'date','zsh':'date','sep':':',
        'desc':f"дата для {changelog}'а {self.specabbr}-файлов",
        'help':False,
        'cmd' :[],'args':'','mod':['date']
        }
      }

    if not G.isArch:
      macro     = SF.color('%{макрос}','grn')
      macroabbr = SF.color('макроса'  ,'grn')
      rbuild    = SF.color('rpmbuild/','blu',True)
      specfile  = SF.color('файл.spec','red',True)
      srcrpm    = SF.color('src.rpm'  ,'red',True)
      ver       = SF.color('версия'   ,'blu',True)
      vers      = SF.color('версии'   ,'blu',True)

      self.tasks.update({
        '::fin'  :{
          '_pre' :[],'_post':[],
          'abbr' : 'fin   ' + specfile,'zsh':'fin','sep':':',
          'desc' :f'показать {self.specabbr}-файл с учётом замены макросов',
          'help' :False,
          'cmd'  :'rpmspec -P','args':'h','mod':['getSpecArg','fin'],
          'zSugg':'___spec'
          },
        # '::check':{
        #   '_pre' :[],'_post':[],
        #   'abbr' : 'check ' + specfile,'zsh':'check','sep':':',
        #   'desc' :f'проверить {self.specabbr}-файл на соответствие правилам',
        #   'help' :False,
        #   'cmd'  :[],'args':'','mod':['check']
        #   },
        '::m'    :{
          '_pre' :[],'_post':[],
          'abbr' :'m   ' + macro,'zsh':'m','sep':':',
          'desc' :'показать значение ' + macroabbr,
          'help' :False,
          'cmd'  :['rpm','-E'],'args':'','mod':['addArg']
          },
        '::cv'   :{
          '_pre' :[],'_post':[],
          'abbr' :f'cv {ver} {ver}','zsh':'cv','sep':':',
          'desc' : 'сравнить ' + vers,
          'help' :False,
          'cmd'  :['rpmdev-vercmp'],'args':'','mod':['addArg']
          },
        '::is'   :{
          '_pre' :[],'_post':[],
          'abbr' : 'is','zsh':'is','sep':':',
          'desc' :f'установка зависимостей из {rbuild}{self.specabbr}',
          'help' :False,
          'cmd'  :['dnf','builddep'],'args':'s','mod':['rpmbuild','getSpec']
          },
        '::ir'   :{
          '_pre' :[],'_post':[],
          'abbr' :'ir  ' + srcrpm,'zsh':'ir','sep':':',
          'desc' :'установка зависимостей из ' + srcrpm,
          'help' :False,
          'cmd'  :['dnf','builddep'],'args':'s','mod':['rpmbuild','addArg'],
          'zSugg':'___srcrpm'
          },
        '::dwn'  :{
          '_pre' :[],'_post':[],
          'abbr' :'dwn ' + specfile,'zsh':'dwn','sep':':',
          'desc' :'скачать исходники',
          'help' :False,
          # строкой, потому что getSpecArg нужен и для spec fin
          'cmd'  :'spectool -g','args':'h','mod':['getSpecArg'],
          'zSugg':'___spec'
          }
        })

      _descriptionCMDs()
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print   ("This is module, please don't execute.")
  sys.exit()
