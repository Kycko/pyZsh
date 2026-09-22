# подгрузка скриптов из bin/exec

from   sys import exit as SYSEXIT
import zshconf.globals as G


############# функции
# мои скрипты выдаём в виде функций, а не алиасов
# иначе не будут работать автодополнения

# один раз объявляем автозагрузку моста
# сначала я задавал fpath в 10_basicLoads.py, но были ошибки у root'а
sDir = G.dirs['repos']['pyZsh']['zshSugg']
if sDir.is_dir(): print(f'fpath=({sDir} $fpath)')
print('autoload -Uz _pzBridge;')

for name,props in G.myBins.items():
  # регистрируем функцию
  print(name + '() { ' + props['launch'] + ' }')
  # подключаем автодополнение к конкретному скрипту
  # если оно включено в SG.dist{}
  if props['zSugg']: print(f'compdef _pzBridge {name};')

############# экспортируем глобальные переменные для автодополнений
print('typeset -gA _pzGlobals;')  # регистрируем переменную
# единственная переменная, которая нужна для алиаса less
print(f"_pzGlobals[isArch]='{G.isArch}'")


# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
