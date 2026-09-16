from   random import choice
from   sys    import exit as SYSEXIT
import pzexec.globals     as G
import pzexec.output      as O
import pzexec.strings     as S
import pzexec.runFuncs    as RF

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  pkgs = SG.tasks[G.distro]
  if G.distro != '7': pkgs = choice(list(pkgs.values()))

  try:
    # успешное выполнение возвращает 0
    if not RF.run(['dnf','install'] + pkgs,'rs'):
      RF.run(['systemctl','set-default','graphical.target'],'s')
  except KeyboardInterrupt: print(S.userCancel)

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['red'],
                 'cat' : 'разработка',
                 'desc': 'автоматическая установка DE',
                 'abbr': 'installDE',
                 'help':  False}  # показывать ли "(есть HELP)"

    self.tasks = {'8':{'plasma':['dolphin',
                                 'konsole',
                                 'kscreen',
                                 'plasma-desktop',
                                 'sddm'],
                       'gnome' :['gdm',
                                 'gnome-session-xsession',
                                 'gnome-terminal',
                                 'nautilus',
                                 'ubuntu-fonts'],
                       'mate'  :['caja',
                                 'gdm',
                                 'mate-desktop',
                                 'mate-session-manager',
                                 'mate-terminal']}}

    add7 = ['mesa-dri-drivers','xorg-x11-server-Xorg']
    self.tasks['7'] = self.tasks['8']['mate'] + add7
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
