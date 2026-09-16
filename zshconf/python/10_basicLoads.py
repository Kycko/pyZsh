# базовые установки и загрузка разных модулей

from   sys import exit as SYSEXIT
import zshconf.globals as G

print('autoload -Uz compinit; compinit')

############### история команд
print('setopt INC_APPEND_HISTORY')
# для autosuggest = match_prev_cmd требуется сохранять дубликаты в истории
# ↓ эта опция убирает дубли при пролистывании стрелками ↑/↓
print('setopt HIST_FIND_NO_DUPS')
# print('setopt HIST_IGNORE_ALL_DUPS')  # пока отключил для autosuggest strategy
print('setopt HIST_REDUCE_BLANKS')
# ↓ это эксперимент, пробуем
print('ZSH_AUTOSUGGEST_STRATEGY=(match_prev_cmd history)')

############### стили
print("zstyle ':completion:*' menu select")
print("zstyle ':completion:*' matcher-list 'm:{[:lower:][:upper:]}={[:upper:][:lower:]}'")
print("zstyle ':completion::complete:*' gain-privileges 1")
# print("zstyle ':completion:*:dnf5:*' truncate names") # для DNF5
print('setopt   menu_complete')
print('unsetopt beep')

# WORDCHARS задаёт символы, которые считаются ЧАСТЬЮ слов
# Посмотреть значение по умолчанию: в чистом zsh запустить echo $WORDCHARS
# Я удалил отсюда слеш, чтобы при нажатии Ctrl+Backspace
#   удалялся не весь путь, а часть до слеша или пробела
# Поведение Ctrl+вправо и Ctrl+влево меняется аналогичным образом
print("WORDCHARS='*?_-.[]~=&;!#$%^(){}<>'")

############### загрузка модулей/плагинов
for path in G.sources_toLoad: print(f'source {path}')

############### защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
