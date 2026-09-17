from   sys import exit as SYSEXIT
import pzexec.output   as O
from   pzexec.pkgAlias import *

SG.dist.update({
  'abbr':'rem',
  'desc':'удаление пакетов'
  })
SG.tasks = {
  'arch':{'cmd':['yay','-Rs'   ],'args':'' },
  'red' :{'cmd':['dnf','remove'],'args':'s'}
  }

class Help(O.Help):
  def printZSH(self): self.zshPackages(True)

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
