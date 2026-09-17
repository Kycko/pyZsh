from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF
import pzexec.strings     as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  task = SG.tasks[G.tk+args.pop(0)]
  if len(args) >= task['args']: RF.run(task['cmd'] + args,'s')
  else                        : RF.raiseError()

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'прочее по ОС',
                 'desc': 'открыть/закрыть зашифрованный диск',
                 'abbr': 'crypt',
                 'help':  True} # показывать ли "(есть HELP)"

    part    = SF.color('раздел','blu',True)
    name    = SF.color('имя'   ,'grn')
    opencmd = ['cryptsetup','open','--type']

    postmsg = [
      S.separator,
      f'  {part} = путь к разделу (/dev/...)',
      f'  {name}    = желаемое имя (как будет отображаться в /dev/mapper/)'
      ]

    self.tasks = {
      '_pre'   :[S.cmdsAvailable],'_post':postmsg,
      'func'   :None,'cmd':None,
      '::ol'   :{
        '_pre' :[],'_post':[],
        'abbr' :f'ol {part} {name}','zsh':'ol','sep':' : ',
        'desc' :'open  luks (стандартный метод в Linux)',
        'help' :False,
        'cmd'  :opencmd + ['luks'],
        'args' :2,  # сколько аргументов требуется
        'zSugg':'___drive'
        },
      '::ov'   :{
        '_pre' :[],'_post':[],
        'abbr' :f'ov {part} {name}','zsh':'ov','sep':' : ',
        'desc' :'open  veracrypt',
        'help' :False,
        'cmd'  :opencmd + ['tcrypt'],
        'args' :2,  # сколько аргументов требуется
        'zSugg':'___drive'
        },
      '::close':{
        '_pre' :[],'_post':[],
        'abbr' :f'close     {name}','zsh':'close','sep':' : ',
        'desc' :'close ANY type',
        'help' :False,
        'cmd'  :['cryptsetup','close'],
        'args' :1 # сколько аргументов требуется
        }
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
