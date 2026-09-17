# подгрузка скриптов из bin/exec

from   sys import exit as SYSEXIT
import zshconf.globals as G


############# функции
# мои скрипты выдаём в виде функций, а не алиасов
# иначе не будут работать автодополнения

# один раз объявляем автозагрузку моста
print('autoload -Uz _pzBridge;')
for name,props in G.myBins.items():
  # регистрируем функцию
  print(name + '() { ' + props['launch'] + ' }')
  # подключаем автодополнение к конкретному скрипту
  print(f'compdef _pzBridge {name};')

############# экспортируем глобальные переменные для автодополнений
print('typeset -gA _pzGlobals;')  # регистрируем переменную
# единственная переменная, которая нужна для алиаса less
print(f"_pzGlobals[isArch]='{G.isArch}'")


# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
