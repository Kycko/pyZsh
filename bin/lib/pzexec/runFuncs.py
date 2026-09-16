# функции запуска и остановки программ

from   sys import exit  as SYSEXIT
import pzexec.strings   as S
from   zshconf.runFuncs import *
if not G.isArch: import pzexec.packages as PKG

# запуск команд, аргументы
def installRPMbuild():
  # сперва проверяет, установлен ли уже rpm-build
  if PKG.RPM(False).query('rpm-build') is None:
    print(S.installRPMbuild)
    return not int(run(['dnf','install','rpm-build'],'rs'))
  else: return True

# прочие мелкие
def raiseError(): raise ValueError('app forced ValueError!')

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
