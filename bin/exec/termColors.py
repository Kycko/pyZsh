from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.output      as O
import pzexec.stringFuncs as SF

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  # берём из globals, ключи словаря упорядочены
  for i,color in enumerate(list(G.colors['term'].keys())[:8]):
    basic = SF.color(f'Цвет {i}'     ,color)
    bold  = SF.color(f'Цвет {i} Bold',color,True)
    print(f'{basic}  |  {bold}')

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'прочие утилиты',
                 'desc': 'вывести палитру стандартных цветов терминала',
                 'abbr': 'termColors',
                 'help':  False}  # показывать ли "(есть HELP)"

    self.tasks = None
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
