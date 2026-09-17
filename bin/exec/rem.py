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
  def printZSH(self):
    cmd = ['pacman','-Qq'] if G.isArch else ['rpm','-qa','--qf','%{NAME}\n']
    try   : final = RF.run(cmd,'t')
    except: final = []

    for line in final: print(line)

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
