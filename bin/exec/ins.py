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
  def printZSH(self):
    file = G.files['cache']['pkglist']

    if file.is_file(): final = FF.readFile(file)
    # фоллбэк на случай отсутствия файла кеша
    elif G.isArch: final = RF.run(['pacman','-Slq'],'t')
    else:
      final = []
      for  pkg in PKG.DNF().api.sack.query().available().latest():
        if pkg.arch in ('x86_64','noarch') and pkg.name not in final:
          final.append(pkg.name)

    for line in final: print(line)

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
