from   sys import exit    as SYSEXIT
import pzexec.globalFuncs as GF
import pzexec.globals     as G
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF
import pzexec.strings     as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  db,fArgs = GF.getTask(args,SG.tasks)
  if   args[0] == 'a':
    if fArgs: RF.run(db['cmd'] + fArgs)
    else    : print(SF.color('Добавьте путь к патчу','red',True))
  elif args[0] == 'c': RF.run(db['cmd'],'h') ; print(SG.cMsg)
  else               : RF.raiseError()

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist  = {'dist':['red'],
                  'cat' : 'разработка',
                  'desc': 'создание и применение патчей',
                  'abbr': 'patch',
                  'help': True}  # показывать ли "(есть HELP)"

    workdir    = G.dirs['work']['local']['patches']
    newpatch   = G.files['newPatch']

    curDir     = SF.color('текущему'   ,'udl')
    patchName  = SF.color(newpatch.name,'cya',True)
    printedDir = str(workdir).replace('/home/kycko','~')
    printedDir = SF.color(printedDir,'ylw')
    created    = SF.color('создан'  ,'grn',True)

    self.cMsg  = f'Патч {patchName} {created} в каталоге {printedDir}'

    self.tasks = {
      '_pre':[S.cmdsAvailable],'_post':[],
      'func':None,'cmd':None,
      '::a' :{
        '_pre':[],'_post':[],
        'abbr':f"a [{SF.hlFirst('apply','blu')}]",
        'zsh' : 'a',
        'sep' : ':',
        'desc':f'применить патч к {curDir} каталогу',
        'help': False,
        'cmd' :[G.sysBins['patch'],'-p1','-i']
        },
      '::c' :{
        '_pre':[],'_post':[],
        'abbr':f"c [{SF.hlFirst('create','blu')}]",
        'zsh' : 'c',
        'sep' : ':',
        'desc':f'создать {patchName} в каталоге {printedDir}',
        'help': False,
        'cmd' :f"cd {workdir} && diff -Nrup init patched > {newpatch}"
        }
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
