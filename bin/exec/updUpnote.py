from   pathlib import Path
from   sys     import exit as SYSEXIT
import pzexec.fileFuncs    as FF
import pzexec.globals      as G
import pzexec.output       as O
import pzexec.stringFuncs  as SF
import zshconf.runFuncs    as RF

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  def _preCheck(workdir:Path):
    def _color(string:str): return SF.color(string,'red',True)
    if str(Path().resolve()) == str(workdir):
      try:
        return {'ver':args.pop(0),'rel':args.pop(0)}
      except:
        ver = _color('версия')
        rel = _color('релиз')
        print(f'Два обязательных аргумента: {ver} и {rel}')
        return None
    else:
      print(f'Сперва перейдите в каталог {workdir}')
      return None
  workdir = G.dirs['repos']['local']['aurSrc']/'upnote-appimage'
  vNew    = _preCheck(workdir)
  if vNew is not None:
    search   = {'ver':'pkgver=','rel':'pkgrel='}
    pkgbuild = workdir/'PKGBUILD'

    data     = FF.readFile(pkgbuild,False)
    for i,line in enumerate(data):
      for key,start in search.items():
        if key in vNew.keys() and line.startswith(start):
          data[i] = search[key] + vNew.pop(key)

    FF.write_toFile(data,pkgbuild)
    RF.run(['makepkg --printsrcinfo > .SRCINFO'],'h')

    pbuild = SF.color('pkgctl build','cya',True)
    print( '1. Проверьте изменения в репозитории (gdh)')
    print( '2. Скопируйте все файлы в каталог сборки')
    print(f'3. Запустите в нём {pbuild}')
    print( '4. Если всё хорошо, commit и push')

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist' :['arch'],
                 'cat'  : 'разработка',
                 'desc' : 'обновление Upnote',
                 'abbr' : 'updUpnote',
                 'help' :  True,  # показывать ли "(есть HELP)"
                 'zSugg':  False}

    self.tasks = None
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
