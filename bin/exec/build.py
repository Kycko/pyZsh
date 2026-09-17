import os
import select
import sys
from   datetime   import datetime
from   pathlib    import Path
from   pty        import openpty
from   re         import compile as reCompile
from   subprocess import Popen   as sprPopen
import pzexec.fileFuncs          as FF
import pzexec.globalFuncs        as GF
import pzexec.globals            as G
import pzexec.listFuncs          as LF
import pzexec.output             as O
import pzexec.runFuncs           as RF
import pzexec.stringFuncs        as SF
import pzexec.strings            as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main(args:list):
  def _printCancel(): print('(отменено)')
  def _pre(type:str,stage:dict):
    def _getDir(mode:str,file:Path):
      chkall    = mode == 'all'
      chkfilter = file.name in SG.copyFilter
      if   file.suffix ==   '.spec': return 'SPECS'
      elif chkall and not chkfilter: return 'SOURCES'
    if   type == 'clear'   :
      # в final добавляем объекты Path с полными путями
      final = {'all':[],'toClear':[]}
      for  dir in G.dirs['work']['rbuild']['root'].iterdir():
        if dir.is_dir():
          final['all'].append(dir)
          save    = stage['mode'] == 'save'
          inStage = dir.stem in stage['filter']
          if (save and not inStage) or (not save and inStage):
            for obj in dir.iterdir(): final['toClear'].append(obj)
      return True,final
    elif type == 'copy'    :
      final = {'data':{'SPECS'  :{'files':[],'color':'red'},
                       'SOURCES':{'files':[],'color':'ylw'}}}
      for  file in Path().iterdir():
        if file.is_file():
          dir = _getDir(stage['mode'],file)
          if dir is not None:
            final['data'][dir]['files'].append(file)

      status = len(final['data']['SPECS']['files']) == 1
      if not status: print(SG.oneSpec)
      return status,final
    elif type == 'dwnLog'  :
      import requests
      if fArgs:
        progress.startStep('Скачиваем лог')
        success = False
        URL     = fArgs[0]
        final   = []

        try:
          response = requests.get(URL,timeout=10)  # скачиваем
          response.raise_for_status() # проверка на ошибки (404, 500 и т. д.)
          final   = response.text.splitlines()  # делим на строки
          success = True
        except: pass
      else: print('Добавьте URL лога') ; _printCancel()

      progress.finishStep(success)
      if URL.startswith('https://'):
        print("Должна быть ссылка 'http://'") ; RF.raiseError()
      return success,{'URL':URL,'log':final}
    elif type == 'getSpec' :
      spec = FF.getSpec()
      if not spec: _printCancel()
      return bool(spec),{'spec':spec}
    elif type == 'rpmbuild': return RF.installRPMbuild(),None
    elif type == 'vDist'   :
      status = SG.vDist in SG.srpmOpts.keys()
      if not status:
        _printCancel()
        print(SF.color('Надо запустить из каталога 73/80','red',True))
      return status,SG.vDist
  def _run(type:str,data :dict):
    def _print         (type:str,data:dict):
      if   type == 'clear':
        final = {'clear'    :{'title':'Пустые     : ','color':'grn','list':[]},
                 'withFiles':{'title':'Есть файлы : ','color':'red','list':[]}}
        for dir in data['all']:
          lst = list(dir.iterdir())
          key = 'withFiles' if lst else 'clear'
          final[key]['list'].append(dir.stem)
        for d in final.values():
          fStr = d['title'] + str(sorted(d['list'])).replace("'",'')
          print(SF.color(fStr,d['color'],True))
      elif type == 'copy' :
        dest = data['dir'].rjust(data['len'])
        dest = SF.color(dest,data['color'],True)
        print(f"[{dest}] <- {data['file']}")
    def _buildRPM      (specfile:str):
      def _logName(specname:str):
        lDir = G.dirs['work']['local']['logs']
        if lDir.exists():
          timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
          file      = f'{timestamp}_{specname}.log'
          return lDir/file
        else: print(f'Не найден каталог {lDir}') ; sys.exit(1)
      def _output (process,master,lFile:str):
        errors       = []
        smthPackaged = False
        with open(lFile,'wb') as logFile:
          # открываем файл на запись
          # бинарный режим удобнее для сырых данных из pty
          try:
            lastPart   = '' # чтобы строки не обрезались
            ansiEscape = reCompile(r'\x1b\[[0-9;]*[a-zA-Z]')
            while True:
              r,_,_ = select.select([master],[],[],0.1)
              if r:
                try: data = os.read(master,4096)
                except OSError as e:
                  # Errno 5 — это нормальный сигнал о закрытии pty процессом
                  if e.errno == 5: break
                  raise
                if not data: break

                # выводим в консоль
                sys.stdout.buffer.write(data) ; sys.stdout.flush()

                # декодируем для вырезания цветов и поиска ошибок
                chunk = data.decode('utf-8',errors='ignore')
                chunk = ansiEscape.sub('',chunk)  # вырезаем цвета
                logFile.write(chunk.encode('utf-8'))
                logFile.flush()

                nChunk = lastPart + chunk
                for line in nChunk.splitlines():
                  res = _findErrors(line,errors)
                  if res: smthPackaged = res
                lastPart = chunk.split('\n').pop()
              if process.poll() is not None:
                # даём короткую паузу, чтобы успеть вычитать хвост буфера
                r,_,_ = select.select([master],[],[],0.05)
                if not r: break
          finally: os.close(master)
        return errors,smthPackaged
      def _rmDebug(logFile:str):
        def _output(string:str,finWrite:list):
          print(string)
          finWrite.append(SF.cutColors(string))
        final = []
        for file in FF.getRPMs():
          if SF.checkSubList(str(file),['debuginfo','debugsource']):
            final.append(file)

        finWrite = []
        if final:
          RF.run(['rm','-f'] + final)
          msg = f'Удалёно пакетов debug: {len(final)}'
          _output('' ,finWrite)
          _output(msg,finWrite)

        FF.write_toFile(finWrite,logFile,True)

      logFile = _logName(specfile.stem)
      if logFile:
        master,slave = openpty()
        # тут особый процесс с одновременным выводом на экран
        # и парсингом вывода, поэтому без RF.run()
        process = sprPopen(['rpmbuild','-bb',str(specfile)],
                            stdout    = slave,
                            stderr    = slave,
                            close_fds = True)
        os.close(slave)
        errors,smthPackaged = _output(process,master,logFile)
        # ↓ ждём окончательного завершения, чтобы получить returncode
        process.wait()

        _rmDebug(logFile)
        addHeader = 'Сборка успешна' if smthPackaged else 'Не собрано'
        _printLogErrors(str(logFile),errors,True,smthPackaged,addHeader)
      return False,data
    def _findErrors    (line:str,errors:list):
      for err in SG.errors:
        if SF.findSub(line,err):
          errors.append(line.strip())
          return  # чтобы не добавлялся дубль по другой ошибке
      # значит сборка успешна
      if line.startswith(f"Записан: {G.dirs['work']['rbuild']['rpms']}"):
        return True
    def _printLogErrors(logFile :str,errors:list,write=False,success:bool=None,addHeader=''):
      def _output   (string:str,finWrite:list):
        print(string)
        finWrite.append(SF.cutColors(string))
      def _separator(length:int,finWrite:list):
        _output(SF.color('-'*length,logColor),finWrite)

      if success is None: logColor = 'red' if errors  else 'grn'
      else              : logColor = 'grn' if success else 'red'

      finWrite = []
      _output('',finWrite)
      if  addHeader: _output(SF.color(addHeader,logColor,True),finWrite)
      if not errors: _output(SF.color('Без ошибок','grn',True),finWrite)

      if errors:
        sepLen = len(logFile) + 5
        _separator(sepLen,finWrite)
        _output(SF.color('Найденные проблемы:',logColor,True),finWrite)
        # выведем последние 50, чтобы не спамить
        for err in errors[-50:]:
          _output(SF.color(' --> ',logColor,True) + err,finWrite)
        _separator(sepLen,finWrite)
      if write: FF.write_toFile(finWrite,logFile,True)

    if   type == 'clear'  :
      # всё одной командой, для оптимизации
      RF.run(['rm','-rf'] + data['toClear'])
      _print(type,data)
      return True,data
    elif type == 'copy'   :
      maxLen = LF.getMaxLen(list(data['data'].keys()))
      for dir,vars in data['data'].items():
        toDir = G.dirs['work']['rbuild'][dir.lower()]
        for file in vars['files']:
          RF.run(['cp',f'./{file}',toDir])
          fData = {'file' :file,
                   'dir'  :dir,
                   'color':vars['color'],
                   'len'  :maxLen}
          _print(stage['type'],fData)
      return True,data
    elif type == 'srpm'   : # запускаем в shell=True из-за --define 'dist .el7'
      spec = data['spec']
      if spec:
        cmd = f'rpmbuild {SG.srpmOpts[SG.vDist]} {SG.fetchOpt} -bs {spec}'
        # успешная загрузка возвращает 0, неудачная 1
        spec = not RF.run(cmd,'hr')
        print(S.separator)
        if spec: print(SF.color('собрано','grn',True))
        else   : print(S.progress['steps']['status'][spec])
      return bool(spec),spec
    elif type == 'rpm'    : return _buildRPM(data['spec'])
    elif type == 'analyze':
      errors = []
      for line in data['log']: _findErrors(line,errors)
      _printLogErrors(data['URL'],errors)
      return True,{}
    elif type == 'remote' :
      def _cancel    (): _printCancel() ; RF.raiseError()
      def _stapel    ():
        if   SG.vDist == '73': return 'stapel'
        elif SG.vDist == '80': return 'stapel80'
        else:
          _printCancel()
          print(SG.wrongRemoteDir)
          RF.raiseError()
      def _tasknum   ():
        try:
          final = fArgs.pop(0)
          if len(final) == 6 and final.isdigit(): return final
          else: _cancel()
        except: print('Не указан номер задачи') ; _cancel()
      def _branch    ():
        return RF.run([G.sysBins['git'],'branch','--show-current'],'et')[0]
      def _pkg       ():
        pkg = Path().resolve().parent.stem
        if pkg: return pkg
        else  : _cancel()
      def _repo      (pkg:str,branch:str):
        final = f'git+git://osgit.red-soft.biz/rpms/{pkg}.git#'

        try   : final += fArgs.pop(0)
        except:
          fCMD = [G.sysBins['git'],'rev-parse',branch]
          if RF.run(fCMD,'et')[0]: final += RF.run(fCMD,'t')[0]
          else:
            ktag = SF.color(branch,'blue',True)
            _printCancel()
            print(f'Нет ветки {ktag} в текущем каталоге')
            return False
        return final
      def _askName   (rName:str):
        print(f'Имя репозитория: {rName}')
        noplus = SF.color("не может быть символа '+'",'red',True)
        print(f'В имени репозитория {noplus}!')
        return input('Введите требуемое имя (как в OSgit): ')
      def _printType ():
        final = stage['task'][0][2:]
        color = 'blk' if final == 'scratch' else 'red'
        return SF.color(final,color,True)
      def _printTests():
        if '--test' in stage['task']:
          return     SF.color('да' ,'grn',True)
        else: return SF.color('нет','red',True)

      if 'r' in stage['mod']: tasknum = _tasknum()
      stapel = _stapel()
      branch = _branch()
      pkg    = _pkg   ()

      if '+' in pkg:
        pkg = _askName(pkg)
        print()
        print(S.separator)

      if 's' in stage['src']:
        pkgfile = FF.getPkg('.src.rpm')
        if pkgfile is None: _cancel()
        # getPkg() может вернуть None
        else: repo = str(pkgfile)
      else: repo = _repo(pkg,branch)

      if repo:
        final = ['koji','-p',stapel,'build','--nowait'] + stage['task']
        if 'r' in stage['mod']: final.append(tasknum)
        final += [branch,repo]

        print('Подтвердите параметры задачи:')
        print('  Название репозитория : ' + pkg)
        print('  Стапель              : ' + stapel)
        print('  Тип                  : ' + _printType())
        if '--scratch' in stage['task']:
          print('  С тестами            : ' + _printTests())
        print('  Сборочный тег        : ' + branch)

        if 's' in stage['src']:
          print('  Пакет                : ' + Path(repo).name)
        else: print('  Тег/коммит           : ' + repo.split('#')[1])

        print()
        if input('Отправляем? ').lower() == 'y': print(); RF.run(final)
        # print(f'DEBUG: {final}')
      return True,data

  db,fArgs = GF.getTask(args,SG.tasks)
  goNext   = True # показывает, можно ли продолжать выполнение
  data     = None
  for stage in db['stages']:
    progress.startStage(SG.stages[stage['type']]['title'],'ylw')
    for type in stage['pre']:
      if   goNext: goNext,data = _pre(type,stage)
    if     goNext: goNext,data = _run(stage['type'],data)
    if not goNext: return # просто останавливаем скрипт

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    def _underline(string:str ): return SF.color(string,'udl')
    def _sumDesc  (keys  :list):
      final = ''
      for key in keys:
        if final: final += ' + '
        final += self.stages[key]['desc']
      return final
    def _remote   ():
      def _collect():
        def _sDesc(string:str,color:str,bold=False):
          start,mid = string.split('[')
          mid  ,end = string.split(']')
          mid       = _underline(mid)
          return SF.color(start+mid+end,color,bold)
        cTag    = SF.color('тег'         ,'ylw',True)
        cCommit = SF.color('коммит'      ,'ylw',True)
        fromGit =   _sDesc('из OS[g]it'  ,'ylw')
        srcrpm  =   _sDesc('из [s]rc.rpm','red',True)

        strings = {
          'tags'   :{'tag'      :f'[+{cTag}]',
                     'tagcommit':f'[+{cTag}/{cCommit}]'},
          'release': SF.color('номер_задачи','red',True)
          }

        srcs  = {'g':{'desc':fromGit,'src':''},
                 's':{'desc':srcrpm ,'src':'s'}}
        tasks = {'n':{'desc':'черновая, без тестов',
                      'type':['--scratch'],
                      'mod' :''},
                 't':{'desc':'черновая, с тестами',
                      'type':['--scratch','--test'],
                      'mod' :''},
                 'r':{'desc':SF.color('релизная','grn',True),
                      'type':['--release','--tracker-id'],
                      'mod' :'r'}}
        abbrs = {'gn':strings['tags']['tagcommit'],
                 'gt':strings['tags']['tagcommit'],
                 'gr':f"{strings['release']} {strings['tags']['tag']}",
                 'sn':'',
                 'st':'',
                 'sr':strings['release']}

        final = {}
        for   s,src  in srcs .items():
          for t,task in tasks.items():
            key  = s+t
            final['::'+key] = {
              '_pre'  :[],'_post':[],
              'abbr'  :f'{key} {abbrs[key]}',
              'zsh'   :key,
              'sep'   :':',
              'desc'  :f"{src['desc']}, {task['desc']}",
              'help'  :False,
              'stages':[{'type':'remote',
                         'pre' :[],
                         'task':task['type'],
                         'mod' :task['mod'],
                         'src' :src ['src']}]
              }

        return final
      final = {'_pre':[S.cmdsAvailable],'_post':[],
               'abbr':'remote','zsh':'remote','sep':':',
               'desc':_sumDesc(['remote']),
               'help':True}
      final.update(_collect())
      self.tasks['::remote'] = final

    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist' :['red'],
                 'cat'  : 'разработка',
                 'desc' : 'всё, что нужно для сборки',
                 'abbr' : 'build',
                 'help' :  True,  # показывать ли "(есть HELP)"
                 'zSugg':  True}

    self.errors = [
      'C compiler cannot create executables',
      'cannot find package',
      'could not find',
      'could not link test program',
      'dependencies are missing:',
      'error:',
      'fatal error',
      'no job control',
      'no module named',
      'no such file or directory',
      'no theme named',
      # ↓ разбито на разные строки, но надо именно про g++
      'unable to','g++ in your PATH',
      'unrecognized options:',
      'you probably have to install',
      'ошибка:'
      ]

    rbuild = '~/rpmbuild'

    self.stages = {
      'clear'  :{'title':'----- Очистка ' + rbuild,
                 'desc' :SF.color(f'очистка {rbuild}/','red',True)},
      'copy'   :{'title':'----- Копирование файлов в ' + rbuild,
                 'desc' :SF.color('копирование в него','cya',True)},
      'srpm'   :{'title':'----- Сборка src.rpm',
                 'desc' :SF.color('сборка src.rpm','ylw',True)},
      'rpm'    :{'title':'----- Сборка двоичного rpm',
                 'desc' :SF.color('сборка двоичного rpm','grn',True)},
      'analyze':{'title':'----- Поиск ошибок в логе',
                 'desc' :SF.color('поиск ошибок в логе','mag')},
      'remote' :{'title':'----- Отправка сборки на сервер',
                 'desc' :SF.color('отправка в стапель','cya',True)}
      }

    rpmbuilddir = SF.color(f'{rbuild}/','ylw')
    dBuild      = SF.color('BUILD'     ,'red',True)
    dBuildroot  = SF.color('BUILDROOT' ,'red',True)
    dSources    = SF.color('SOURCES'   ,'blu',True)
    dSpecs      = SF.color('SPECS'     ,'blu',True)

    self.tasks  = {
      '_pre'     :[S.cmdsAvailable],'_post':[],
      'func'     :None,'cmd':None,
      '::clear'  :{
        '_pre'   :[S.cmdsAvailable],'_post':[],
        'abbr'   :'clear','zsh':'clear','sep':':',
        'desc'   :_sumDesc(['clear']),
        'help'   :True,
        '::all'  :{
          '_pre'  :[],'_post':[],
          'abbr'  : 'all','zsh':'all','sep':':',
          'desc'  :f"очистить {_underline('всё')} в {rpmbuilddir}",
          'help'  :False,
          'stages':[{'type':'clear','pre':['clear'],'mode':'save','filter':[]}]
          },
        '::bb'   :{
          '_pre'  :[],'_post':[],
          'abbr'  : 'bb','zsh':'bb','sep':':',
          'desc'  :f"очистить {_underline('только')} {dBuild} и {dBuildroot}",
          'help'  :False,
          'stages':[{'type':'clear','pre':['clear'],'mode':'rm','filter':['BUILD','BUILDROOT']}]
          },
        '::ss'   :{
          '_pre'  :[],'_post':[],
          'abbr'  : 'ss','zsh':'ss','sep':':',
          'desc'  :f"очистить всё, {_underline('кроме')} {dSources} и {dSpecs}",
          'help'  :False,
          'stages':[{'type':'clear','pre':['clear'],'mode':'save','filter':['SOURCES','SPECS']}]
          }
        },
      '::copy'   :{
        '_pre'   :[S.cmdsAvailable],'_post':[],
        'abbr'   :'copy','zsh':'copy','sep':':',
        'desc'   :_sumDesc(['clear','copy']),
        'help'   :True,
        '::all'  :{
          '_pre'  :[],'_post':[],
          'abbr'  :'all','zsh':'all','sep':':',
          'desc'  :'скопировать ' + _underline('всё'),
          'help'  :False,
          'stages':[{'type':'clear','pre':['clear'],'mode':'save','filter':[]},
                    {'type':'copy' ,'pre':['copy' ],'mode':'all'}]
          },
        '::spec' :{
          '_pre'  :[],'_post':[],
          'abbr'  :'spec','zsh':'spec','sep':':',
          'desc'  :'скопировать только '+SF.color('spec','red',True),
          'help'  :False,
          'stages':[{'type':'clear','pre':['clear'],'mode':'save','filter':['SOURCES']},
                    {'type':'copy' ,'pre':['copy' ],'mode':'spec'}]
          }
        },
      '::srpm'   :{
        '_pre'   :[],'_post':[],
        'abbr'   :'srpm','zsh':'srpm','sep':':',
        'desc'   :_sumDesc(['clear','copy','srpm']),
        'help'   :False,
        'stages' :[{'type':'clear','pre':['vDist','clear'],'mode':'save','filter':[]},
                   {'type':'copy' ,'pre':['copy']         ,'mode':'all'},
                   {'type':'srpm' ,'pre':['rpmbuild','getSpec']}]
        },
      '::rpm'    :{
        '_pre'   :[],'_post':[],
        'abbr'   :'rpm','zsh':'rpm','sep':':',
        'desc'   :_sumDesc(['rpm','analyze']),
        'help'   :False,
        'stages' :[{'type':'rpm','pre':['rpmbuild','getSpec']}]
        },
      '::analyze':{
        '_pre'   :[],'_post':[],
        'abbr'   :'analyze','zsh':'analyze','sep':':',
        'desc'   :_sumDesc(['analyze']),
        'help'   :False,
        'stages' :[{'type':'analyze','pre':['dwnLog']}]
        }
      }
    _remote()

    self.copyFilter = ['.git',
                       '.gitignore',
                       'README.md',
                       'sources.toml']
    self.srpmOpts   = {'73':"--define 'dist .el7'",
                       '80':''}

    self.vDist          =  Path().resolve().stem
    self.fetchOpt       = '--undefine=_disable_source_fetch'
    self.wrongRemoteDir = 'Для запуска перейдите в каталог нужной сборки (73/80)'
    self.wrongRemoteDir =  SF.color(self.wrongRemoteDir,'red',True)

    self.oneSpec = 'В текущем каталоге должен быть только один spec-файл!'
    self.oneSpec =  SF.color(self.oneSpec,'red',True)
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/

class Help(O.Help): pass  # здесь стандартный
progress = O.Progress()

# защита от запуска модуля
if __name__ == '__main__':
  print   ("This is module, please don't execute.")
  sys.exit()
