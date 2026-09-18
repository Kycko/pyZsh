from   os.path import commonpath
from   pathlib import Path
from   sys     import exit as SYSEXIT
import pzexec.fileFuncs    as FF
import pzexec.globalFuncs  as GF
import pzexec.globals      as G
import pzexec.listFuncs    as LF
import pzexec.output       as O
import pzexec.runFuncs     as RF
import pzexec.stringFuncs  as SF
import pzexec.strings      as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  # если аргументов нет, GF.getTask() выдаст ошибку
  db,fArgs = GF.getTask(args,SG.tasks)
  # любое отличие db и SG.tasks означает, что мы нашли подкоманду
  if db == SG.tasks: run(args)  # отвал, передаём всё как есть
  else:
    if   db['func']: db['func'](fArgs)
    elif db['cmd' ]: run(db['cmd'] + fArgs)
    else           : RF.raiseError()
def run (args:list):
  def _mail():
    def _input():
      def _askMail():
        mails = list(G.mails.values())
        for i,mail in enumerate(mails,start=1):
          print(f'{str(i).rjust(2)} : {mail}')
        print('99 : ввести другой вариант')

        num = ''
        while not num.isdigit():
          msg = 'Выберите почту для этого репозитория: '
          num = input(SF.color(msg,'grn',True))
        num = int(num)
        if num == 99:
          mail = ''
          while '@' not in mail: mail = input('Введите почту: ')
        else: mail = mails[num-1]

        return mail
      print(SF.color('Этот путь не найден в кеше','red',True))
      print()
      mail = _askMail()
      print()
      print(f'Текущий каталог: {cur}')
      nPath = ''
      while not nPath:
        nPath = input('Введите общий каталог для этой почты: ')
      FF.write_toFile(f'{nPath} {mail}',SG.mailFile,True)

      print()
      print(SF.color('Кеш почты обновлён:','grn',True))
      print(f'  Каталог : {nPath}')
      print(f'  Почта   : {mail}')
      print(S.separator)
      print()
      return mail
    # наверное, на всякий случай лучше перечитывать файл при каждом запуске
    cur = Path().resolve()
    if SG.mailFile.is_file():
      try:
        for line in FF.readFile(SG.mailFile):
          cPath,mail = line.split()
          if commonpath([str(cur),cPath]) == cPath: return mail
      except:
        print(SG.errMail)
        print(SF.color('Операция не выполнена','red',True))
        SYSEXIT()
    return _input()
  if args[0] == 'commit':
    credentials = ['-c', 'user.name=Anton Samartsev',
                   '-c',f'user.email={_mail()}']
  else: credentials = []

  RF.run([G.sysBins['git']] + credentials + args)

def back  (args:list):
  # успешное выполнение возвращает 0
  if RF.run([G.sysBins['git'],'checkout','HEAD~1'],'oer'):
    print(S.progress['steps']['status'][False])
    print('Это последний коммит?')
  else:
    print(SF.color('Вернулись','grn') + ' на один коммит назад.')
    switch  = SF.color('git branch s ','ylw')
    switch += SF.color('имя_ветки'    ,'udl')
    print(f'Для возврата переключите ветку ({switch}).')
def branch(args:list):
  print(S.separator)
  print(SG.repoBranches)
  RF.runWait([G.sysBins['git'],'branch'])
  print(S.separator)
  RF.raiseError()
def diff  (args:list):
  try:
    if len(args):
      if G.guiterm: cmd = ['difftool','--dir-diff','--tool=meld']
      else        : cmd = ['diff']
      run(cmd + args)
    else: print('Добавьте параметры (что будем сравнивать)')
  # ↓ чтобы после Ctrl+C не вылезал diff в терминале
  except KeyboardInterrupt: pass
def files (args:list):
  def _partial(gitignoreAdd:list,file:str,lines:list):
    init = FF.readFile(file)
    for line in lines:
      if not LF.inclStr(init,line,lower=False):
        gitignoreAdd.append(line)
    FF.write_toFile(gitignoreAdd,file,True)
  fPrint       = {} # f = final
  gitignoreAdd = []
  skipped      = False
  curFiles     = [file.name for file in Path().iterdir()]

  for k,f in G.gitFiles.items():
    skip = f['file'] in curFiles
    fPrint[f['file']] = ('new','skip')[skip]
    if skip:
      skipped = True
      if k == 'ignore': _partial(gitignoreAdd,**f)
    else: FF.write_toFile(**f)

  fLen = (6,14)[skipped]
  for file,key in fPrint.items():
    st   = SG.fStrings[key]
    fStr = ' '*(fLen-len(SF.cutColors(st))) + st
    print(f'[{fStr}] {file}')

    if file == G.gitFiles['ignore']['file']:
      for line in gitignoreAdd:
        print(f"  -->[{SG.fStrings['add']}] {line}")
      if gitignoreAdd: print(S.separator + '--')

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    def _colorfile(fKey:str):
      return SF.color(G.gitFiles[fKey]['file'],'blu',True)
    def _hlFirst(string:str): return SF.hlFirst(string,'blu',True)

    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist' :['arch','red'],
                 'cat'  : 'разработка',
                 'desc' : 'git',
                 'abbr' : 'git',
                 'help' :  True,  # показывать ли "(есть HELP)"
                 'zSugg':  False}

    self.repoBranches = 'Ветки в текущем репозитории:'

    self.mailFile = G.files['cache']['gitmail']
    self.errMail  = f'Файл {self.mailFile} найден, но повреждён'
    self.errMail  = SF.color(self.errMail,'red',True)

    self.fStrings = {'skip':SF.color('уже существует','red',True),
                     'new' :SF.color('создан'        ,'grn',True),
                     'add' :SF.color('добавлено'     ,'grn',True)}

    # описания для help'а
    otherCMD = 'Если ввести другие команды, будет запущен обычный git'
    gCommit  =  SF.color('или указанного','red')
    gBack    = 'вернуться на один коммит назад '
    gBack   +=  SF.color('без изменения текущей ветки','grn')
    filesStr = f"{_colorfile('ignore')} и {_colorfile('readme')}"

    d = {'files' :f'создать в ТЕКУЩЕМ каталоге {filesStr}',
         'revert': 'удалить последний коммит, сохранив текущие файлы',
         'reset' : 'сбросить всё (вернуть репозиторий к последнему коммиту)',
         'bName' :  SF.color('имя_ветки'  ,'ylw'),
         'commit':  SF.color('хеш_коммита','red'),
         'bTree' :f"{_hlFirst('tree')}   (создать из текущего [{gCommit}] коммита)"}

    # в этом скрипте дополнения zsh НЕ делаем
    # (не получается комбинировать со стандартными)
    self.tasks = {
      '_pre'    : [S.cmdsAvailable],
      '_post'   : [S.separator,otherCMD],
      'func'    :  None,
      'cmd'     :  None,
      '::addall':{'_pre' :[],'_post':[],
                  'abbr' :'[ga] ' + SF.color('addall','ylw',True),
                  'sep'  :'=',
                  'desc' :'git add --all',
                  'help' :False,
                  'func' :None,
                  'cmd'  :['add','--all']},
      '::amend' :{'_pre' :[S.cmdsAvailable],
                  '_post':[],
                  'abbr' :'amend',
                  'sep'  :':',
                  'desc' :'изменить последний коммит',
                  'help' :True,
                  'func' :None,
                  'cmd'  :None,
                  '::n'  :{'_pre' :[],'_post':[],
                           'abbr' :'n',
                           'sep'  :':',
                           'desc' :'не менять сообщение',
                           'help' :False,
                           'func' :None,
                           'cmd'  :['commit','--amend','--no-edit']},
                  '::m'  :{'_pre' :[],'_post':[],
                           'abbr' :'m ' + SF.color("'сообщение'",'ylw',True),
                           'sep'  :':',
                           'desc' :'изменить сообщение',
                           'help' :False,
                           'func' :None,
                           'cmd'  :['commit','--amend','-m']}},
      '::back'  :{'_pre' :[],'_post':[],
                  'abbr' :'back',
                  'sep'  :':',
                  'desc' :gBack,
                  'help' :False,
                  'func' :back,
                  'cmd'  :None},
      '::branch':{'_pre' :[S.addOpt],
                  '_post':[],
                  'abbr' :'branch',
                  'sep'  :':',
                  'desc' :'ветки',
                  'help' :True,
                  'func' :branch,
                  'cmd'  :None,
                  '::s'  :{'_pre' :[],'_post':[],
                           'abbr' :f"s + {d['bName']}",
                           'sep'  :':',
                           'desc' :_hlFirst('switch (переключить)'),
                           'help' :False,
                           'func' :None,
                           'cmd'  :['checkout']},
                  '::b'  :{'_pre' :[],'_post':[],
                           'abbr' :f"b + {d['bName']}",
                           'sep'  :':',
                           'desc' :_hlFirst('blank  (создать пустую)'),
                           'help' :False,
                           'func' :None,
                           'cmd'  :['checkout','--orphan']},
                  '::t'  :{'_pre' :[],'_post':[],
                           'abbr' :f"t + {d['bName']} [+{d['commit']}]",
                           'sep'  :':',
                           'desc' :d['bTree'],
                           'help' :False,
                           'func' :None,
                           'cmd'  :['checkout','-b']}},
      '::commit':{'_pre' :[],'_post':[],
                  'abbr' :'[gc] ' + SF.color("commit 'сообщение'",'ylw',True),
                  'sep'  :'=',
                  'desc' :"git commit -m 'сообщение'",
                  'help' :False,
                  'func' :None,
                  'cmd'  :['commit','-m']},
      '::diff'  :{'_pre' :[],'_post':[],
                  'abbr' :'diff',
                  'sep'  :':',
                  'desc' :'сравнение (всегда запускает difftool)',
                  'help' :True,
                  'func' :diff,
                  'cmd'  :None},
      '::files' :{'_pre' :[],'_post':[],
                  'abbr' :SF.color('files','grn',True),
                  'sep'  :':',
                  'desc' :d['files'],
                  'help' :False,
                  'func' :files,
                  'cmd'  :None},
      '::revert':{'_pre' :[],'_post':[],
                  'abbr' :'revert',
                  'sep'  :':',
                  'desc' :d['revert'],
                  'help' :False,
                  'func' :None,
                  'cmd'  :['reset','HEAD~1']},
      '::reset' :{'_pre' :[],'_post':[],
                  'abbr' :SF.color('reset','red',True),
                  'sep'  :':',
                  'desc' :d['reset'],
                  'help' :False,
                  'func' :None,
                  'cmd'  :['reset','--hard','HEAD']}
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/
class Help(O.Help): pass  # здесь стандартный

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
