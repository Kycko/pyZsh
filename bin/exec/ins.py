from sys import exit as SYSEXIT
from pzexec.pkgAlias import *

SG.dist.update({
  'abbr':'ins',
  'desc':'установка пакетов'
  })
SG.tasks = {
  'arch':{'cmd':['yay','-S'     ],'args':'' },
  'red' :{'cmd':['dnf','install'],'args':'s'}
  }

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
