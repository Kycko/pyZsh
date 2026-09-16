# цвета

import re
from   os  import environ
from   sys import exit  as SYSEXIT
import zshconf.globals  as G
import zshconf.runFuncs as RF

def _lsColors():  # меняет цвета объектов в выводе команды ls
  try:
    # генерация стандартной базы
    result = RF.run([G.sysBins['dircolors'],'-b'],'t')[0]
    # вывод dircolors -b выглядит как: LS_COLORS='...'; export LS_COLORS;
    # извлекаем только само значение цвета между одинарными кавычками
    colors = re.search(r"LS_COLORS='(.*?)'",result).group(1)
  except: colors = environ.get('LS_COLORS','')

  if colors:  # умная замена флага папок (di=...) на жёлтый цвет (33)
    G.exports['LS_COLORS'] = re.sub(r'di=[0-9;]+','di=33',colors)

if not G.guiterm:
  # иначе zsh-autosuggest показывает подсказки таким же
  # белым цветом, как и набранный текст
  print("ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=black,bold'")
  # задаём оттенки для TTY
  for i,code in G.colors['TTY'].items():
    print(rf"echo -en '\e]P{i}{code}'")

_lsColors()

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
