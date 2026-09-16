# горячие клавиши

from   sys import exit as SYSEXIT
import zshconf.globals as G

############### функции
def _updHotkeys():
  home = '^[[H' if G.guiterm else '^[[1~'
  end  = '^[[F' if G.guiterm else '^[[4~'
  if G.guiterm: ctrlDel = '^[[3;5~'
  else: # в RO TTY-кейкод Ctrl+Delete совпадает с Delete
    ctrlDel = '^[[3~' if G.isArch else None

  actions = {'home'   :{'code':home   ,'action':'beginning-of-line'},
             'end'    :{'code':end    ,'action':'end-of-line'},
             'ctrlDel':{'code':ctrlDel,'action':'kill-word'}}
  actions.update(G.hotkeys)
  return actions

############### базовые
suffix = 'line-or-beginning-search'
print(f'autoload -Uz  up-{suffix} down-{suffix}')
print(f'zle      -N   up-{suffix}')
print(f'zle      -N down-{suffix}')

# чтобы exit срабатывал даже когда в строке что-то введено
print('exit_zsh() { exit }')
print('zle      -N  exit_zsh')

############### привязка клавиш к командам
for  key in _updHotkeys().values():
  if key['code'] is not None:
    c,a = key['code'],key['action']
    print(f"bindkey '{c}' {a}")

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
