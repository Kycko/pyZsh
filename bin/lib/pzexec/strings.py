# общие для нескольких скриптов строки

from   sys import exit    as SYSEXIT
import pzexec.globals     as G
import pzexec.stringFuncs as SF

separator     = '-'*25
cmdsAvailable = 'Доступные команды:'
addOpt        = 'Добавьте одну из этих опций:'
addPkg        = 'Добавьте имя пакета'
ownHelp       =  SF.color('(есть HELP)','ylw',True)
userCancel    = '\nОтменено пользователем'

installRPMbuild = 'Установка rpm-build...'
oneSpec   = f"В {G.dirs['work']['rbuild']['specs']} должен быть один spec-файл"
noFile    = SF.color('Ошибка чтения файла','red',True)
noMeldMSG = SF.color('Meld не установлен','red',False)

cache = {'fresh':SF.color('свежий' ,'grn',False),
         'old'  :SF.color('устарел','red',True)}

progress = {
  'steps':{'status':{True   : SF.color('OK'    ,'grn',True),
                     False  : SF.color('FAILED','red',True)},
           'pkg'   :{'deps' :'собираем зависимости',
                     'provs':'собираем provides',
                     'wReq' :'кому пакет нужен?',
                     'check':'ищем пакет'},
           'upd'   : 'получаем метаданные'}
  }

tableHeaders = {
  # ↓ для O.Progress.showDeps()
  'deps':{'hard'    :SF.color('жёсткие зависимости','red',True),
          'soft'    :SF.color('мягкие зависимости' ,'grn',True),
          'deps'    :['зависимость','версия'],
          'provides':['provide'    ,'версия']}
  }

pkginfo = {'name'     :'Имя',
           'epoch'    :'Эпоха',
           'version'  :'Версия',
           'release'  :'Релиз',
           'arch'     :'Архитектура',
           'URL'      :'URL',
           'buildtime':'Дата сборки',
           'summary'  :'Summary',
           'desc'     :'Описание'}
noEpoch = SF.color('не задана','red',True)

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
