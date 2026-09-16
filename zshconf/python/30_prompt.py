# файл для создания "приветствий" терминала

from   sys import exit as SYSEXIT
import zshconf.globals as G

################## функции
def _block      (data   :str):
  return f'──[{data}%b{prcolor}]' # %b сбрасывает жирность
def _exportPaths(prcolor:str):
  # пути для замены в промпте
  clrCode = G.colors['prompt']['dirPrefix']
  final   = []
  for full,conf in G.dirs['prompt'].items():
    if G.distType in conf['distro']:
      # ↓ важный слеш, чтобы не заменять корень этого пути
      f = f'{full}/'
      s = conf['subst'] # надо переменную без кавычек
      final.append(f'[{f}]="{clrCode}{s}:{prcolor}"')

  print( 'typeset -gA _pzPathDirs')
  print(f"_pzPathDirs=({' '.join(final)})")

################## чтобы zsh вычислял изменения каждый раз
print('setopt prompt_subst')

################## основная логика
# цвета
clrs    = G.colors['prompt']['lines']
sshKey  = ['local','ssh' ][G.inSSH]
userKey = ['user' ,'root'][G.isRoot]
prcolor = clrs[sshKey][userKey]

# формируем строки
symb  = G.termSymbols
line1 = prcolor + symb[0] + _block('%T')  # время
if G.inSSH: # чтобы у красного root'a был блок нужного цвета
  fColor = clrs['ssh']['user']
  line1 += _block(f'{fColor}virtRO{G.sshDistro}')
line1 += '\\${_pzPromptGit}'
line1 += '\\${_pzPromptDir}'

line2 = f'{symb[1:]} %f%b'

################## экспорт
print(f'PROMPT="{line1}\n{line2}"')
print('_pzPromptBlock="' + _block('\\${_pzvar}') + '"')
_exportPaths(prcolor) # замена путей (repos: и build:)

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
