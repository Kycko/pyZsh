from   sys import exit  as SYSEXIT
import pzexec.fileFuncs as FF
import pzexec.output    as O
from   pzexec.pkgAlias import *
if not G.isArch: import pzexec.packages as PKG

SG.dist.update({
  'abbr':'ins',
  'desc':'установка пакетов'
  })
SG.tasks = {
  'arch':{'cmd':['yay','-S'     ],'args':'' },
  'red' :{'cmd':['dnf','install'],'args':'s'}
  }

class Help(O.Help):
  def printZSH(self): self.zshPackages(False,True)

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
