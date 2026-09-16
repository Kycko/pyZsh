# общие для нескольких скриптов строки

from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.stringFuncs as SF

separator     = '-'*25
cmdsAvailable = 'Доступные команды:'
addPkg        = 'Добавьте имя пакета'
ownHelp       =  SF.color('(есть HELP)','ylw',True)
userCancel    = '\nОтменено пользователем'

installRPMbuild = 'Установка rpm-build...'
oneSpec = f"В {G.dirs['work']['rbuild']['specs']} должен быть один spec-файл"
noFile  = SF.color('Ошибка чтения файла','red',True)

cache = {'fresh':SF.color('свежий' ,'grn',False),
         'old'  :SF.color('устарел','red',True)}

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
