# подгрузка скриптов из bin/exec

from   sys import exit as SYSEXIT
import zshconf.globals as G


############# функции
# мои скрипты выдаём в виде функций, а не алиасов
# иначе не будут работать автодополнения
for name,props in G.myBins.items():
  init = G.files['binInit']
  file = props['file'].name
  print(name + '() {')
  print(f'python3 {init} {file} "$@"')
  print('}')


############# экспортируем глобальные переменные для автодополнений
print('typeset -gA _pzGlobals;')  # регистрируем переменную

for name,value in G.__dict__.items():
  # игнорируем встроенные системные атрибуты типа __file__
  if name.startswith('__'): continue
  # берём только
  if isinstance(value,(bool,str)):
    print(f"_pzGlobals[{name}]='{value}';")

# из словарей придётся доставать по отдельности
print(f"_pzGlobals[dnfCache]='{G.files['cache']['pkglist']}'")


# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
