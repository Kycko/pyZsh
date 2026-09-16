# глобальные переменные для скриптов из bin/exec

from sys import exit as SYSEXIT
from zshconf.globals import *

############## каталоги
# рабочие
dirs['work'].update({
  'local' :{'root':dirs['home']/'data/build'},
  'rbuild':{'root':dirs['home']/'rpmbuild'}
  })
dirs['work']['local']['patches'] = dirs['work']['local'] ['root']/'patches'

for dir in ['RPMS','SPECS']:
  dirs['work']['rbuild'][dir.lower()] = dirs['work']['rbuild']['root']/dir

# BTRFS
dirs['snaps'] = {'cur'   :Path('/mnt/@root'),
                 'broken':Path('/mnt/@root.broken'),
                 # здесь надо подставлять номер, поэтому без Path
                 'from'  :'/mnt/@snaps/$num$/snapshot'}

############## файлы
files.update({
  'mail'    :{
    'arch'  :dirs['home']/'data/cloud/myFiles/comp/sysconfig/linux/mail.txt',
    'red'   :dirs['home']/'data/cloud/sysconfig/mail.txt'
    },
  'mounts'  :Path('/proc/mounts'),
  'newPatch':dirs['work']['local']['patches']/'name.patch'
  })

gitFiles = {'ignore':{'file' : '.gitignore',
                      'lines':['*.asc',
                               '*.gem',
                               '*.tar.bz2',
                               '*.tar.gz',
                               '*.tar.lz',
                               '*.tar.xz',
                               '*.tgz',
                               '*.rpm',
                               '.directory']},
            'readme':{'file' : 'README.md'   ,
                      'lines':['[Стапель 8.0/7.3](ССЫЛКА)']}}

############## оформление вывода
# максимальная длина сообщений, показывающих прогресс (шаги)
maxStepLen = 23

colors['term'] = {'blk':'\033[30m', # black
                  'red':'\033[31m', # red
                  'grn':'\033[32m', # green
                  'ylw':'\033[33m', # yellow
                  'blu':'\033[34m', # blue
                  'mag':'\033[35m', # magenta
                  'cya':'\033[36m', # cyan
                  'wht':'\033[37m', # white
                  'udl':'\033[4m',  # underline
                  'bld':'\033[1m',  # bold
                  'rst':'\033[0m'}  # reset all colors

########### программы
for bin in ['btrfs','meld','patch']: sysBins[bin] = which(bin)

############## прочее
zshFlag = '--zsh-data'
# (task key) = с чего должен начинаться подпункт в Globals() скриптов
tk = '::'

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
