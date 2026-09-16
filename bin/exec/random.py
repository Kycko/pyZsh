from   random import randint
from   sys    import exit as SYSEXIT
import pzexec.globals     as G
import pzexec.listFuncs   as LF
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF
import pzexec.strings     as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  task = SG.tasks[G.tk + args.pop(0)]
  if len(args) < task['args']: RF.raiseError()
  else                       : task['func'](args)

def number(args:list):
  def _parse(arg:str):
    try:
      nums = arg.split('-')
      for i,num in enumerate(nums): nums[i] = int(num)
      if len(nums)  ==  1 : nums.insert(0,1)
      if nums[0] > nums[1]:
        print(f'Ошибка: {nums[0]} > {nums[1]}')
        return
      return nums
    except: print(f'Ошибка: неверный формат {arg}')
  results = []
  for arg in args:
    parsed = _parse(arg)
    if parsed: results.append(str(randint(*parsed)))
    else     : return # завершаем полностью

  # финальный вывод
  counterLen = len(str(len(args)))
  argLen     = LF.getMaxLen(args)
  resLen     = LF.getMaxLen(results)

  for i,arg in enumerate(args):
    counter = '№' + str(i+1).ljust(counterLen)
    limit   = 'ограничение: ' + arg.rjust(argLen)
    res     = SF.color(results[i].rjust(resLen),'grn')
    res     = f'результат: {res}'
    print(f'{counter} | {limit} | {res}')
def color (args:list):
  def _get    (): return randint(0,255)
  def _example(r:int,g:int,b:int):  # показывает выбранный цвет
    # ↓ определяет, какой текст лучше читается на этом цвете
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    fontMod    = '0' if brightness > 128 else '255'
    txtColor   = f'\033[38;2;{fontMod};{fontMod};{fontMod}m'

    if not G.guiterm:
      msg = ' В TTY выводится не выбранный цвет, а ближайший оттенок!'
      print(SF.color(msg,'red',True))
    print(f'  {txtColor}\033[48;2;{r};{g};{b}m выбранный цвет \033[0m')

  r = _get()
  g = _get()
  b = _get()

  _example(r,g,b)  # показываем сам цвет

  # строка 1: три числа через пробел
  print(f'  RGB : {r} {g} {b}')

  # строка 2: HEX-код с ведущими нулями (если число меньше 16)
  # :02X означает:
  # - перевести в 16-ричную систему
  # - сделать длину 2 символа
  # - дополнить нулями
  # - буквы ЗАГЛАВНЫЕ
  print(f'  hex : #{r:02x}{g:02x}{b:02x}')
  print(f'  HEX : #{r:02X}{g:02X}{b:02X}')

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'прочие утилиты',
                 'desc': 'случайные числа/цвета',
                 'abbr': 'random',
                 'help': True}  # показывать ли "(есть HELP)"

    integers  = SF.color('int '  ,'red',True)
    integers += SF.color('5 3-12','grn',True)

    self.tasks = {
      '_pre'   :[S.cmdsAvailable],'_post':[],
      'func'   :None,'cmd':None,
      '::int'  :{
        '_pre' :[],'_post':[],
        'abbr' : integers,'zsh':'int','sep':':',
        'desc' :'случайные числа (сколько угодно)',
        'help' :False,
        'func' :number,
        'args' :1
        },
      '::color':{
        '_pre' :[],'_post':[],
        'abbr' : SF.color('color','cya',True),
        'zsh'  :'color',
        'sep'  :':',
        'desc' :'случайный цвет',
        'help' :False,
        'func' :color,
        'args' :0
        }
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
