from sys import exit as SYSEXIT
from pzexec.pkgAlias import *

SG.dist.update({
  'abbr':'rem',
  'desc':'удаление пакетов'
  })
SG.tasks = {
  'arch':{'cmd':['yay','-Rs'   ],'args':'' },
  'red' :{'cmd':['dnf','remove'],'args':'s'}
  }

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
