from   sys import exit    as SYSEXIT
import pzexec.fileFuncs   as FF
import pzexec.globals     as G
import pzexec.listFuncs   as LF
import pzexec.output      as O
import pzexec.runFuncs    as RF
import pzexec.stringFuncs as SF
import pzexec.strings     as S

# основные функции
# определяем здесь, чтобы использовать в Globals()
def main    (pkgs:list):
  def _run(task:str,pkgs:list):
    def _arch   (task:str,pkgs:list):
      if   task[1] == 'f':
        res = LF.rmBlanks(RF.run(['pkgfile','-l'] + pkgs,'t'))
        if res:
          for line in res: print(line)
        else: print(SF.color('Пакет не найден','red'))
      elif task[0] == 'l': RF.run(['yay','-Qii'] + pkgs)
      elif task[0] == 'r': RF.run(['yay','-Sii'] + pkgs)
      else               : RF.raiseError()
    def _pre    (task:str,pkgs:list):
      preList = SG.tasks['task'][task[1]]['pre']
      if 'getDeps'     in preList: pkgs = progress.getDeps(pkgs,'r')
      if 'getProvides' in preList: pkgs = progress.getDeps(pkgs,'p')
      return pkgs
    def _runType(task:str,pkg):
      progress.pkgStage(SG.tasks['task'][task[1]]['stage'],pkg.nevra)
      if   task[1] == 'i': pkg.showInfo()
      elif task[1] == 'c': pkg.showChangelog()
      elif task[1] == 'd': progress.showDeps(pkg,'r')
      elif task[1] == 'p': progress.showDeps(pkg,'p')
      elif task[1] == 'f': pkg.showFiles()

    if G.isArch: _arch(task,pkgs)
    else:
      print(S.separator)
      found = progress.checkPkgs(pkgs,task[0] == 'l')
      if task[1] != 'v':  # версии уже выведены на экран
        for pkg in _pre(task,found): _runType(task,pkg)
  task = pkgs.pop(0)
  try: SG.tasks['special'][task]['func'](pkgs)
  except KeyboardInterrupt: print(S.userCancel)
  except:
    if pkgs: _run(task,pkgs)
    else   : print(SF.color('Добавьте пакет(ы)','red'))
def autodiff(pkgs:list):
  def _query(pkgs:list,rpm:bool):
    stgKey = ('checkRepo','checkLocal')[rpm]
    progress.startStage(SG.stages['ad'][stgKey],'blu')
    found = progress.checkPkgs(pkgs,rpm,True)
    # не принимаем выхлоп getDeps: сохраняем изначальный список
    progress.getDeps(found,'pr')
    return found
  def _clean(found:dict):
    numbers = [pkg.initNum for pkg in found['inRepos']]
    db      = found['local']
    for i in range(len(db)-1,-1,-1):
      if db[i].initNum not in numbers: db.pop(i)
    return found
  def _prepareForMeld(found:dict):
    def _get(type:str,pkgs:list):
      def _getSorted (deps:list):
        final = []
        for dep in deps:
          final.append(f"{dep['name']} {dep['sign']} {dep['ver']}")
        return sorted(final)
      # type = r/p (requires & recommends / provides)
      tKey  = 'deps' if type == 'r' else 'provides'
      final = [SG.adStr['split'],
               SG.adStr[tKey],
               SG.adStr['split']]
      for pkg in pkgs:
        final.append(SG.adStr['pkgSplit'] + pkg.nevra)
        if type == 'r':
          for dType,deps in pkg.deps.items():
            final.append(SG.adStr[dType])
            final   += _getSorted(deps)
        else: final += _getSorted(pkg.provides)
        final.append('')
      return final
    final = {}  # {'local':[],'inRepos':[]}
    for pType,pkgs in found.items():
      final[pType] = _get('r',pkgs) + _get('p',pkgs)
      final[pType].append('')
    return final

  if not pkgs: pkgs = FF.getRPMs(True)
  if pkgs:
    f  = {'local': _query(pkgs,True)}
    f['inRepos'] = _query([pkg.name for pkg in f['local']],False)
    f = _prepareForMeld(_clean(f))
    progress.startStage(SG.stages['ad']['meld'],'blu')
    RF.meld([f['inRepos'],f['local']])
  else: print(SG.noPkgs)

# классы
class Globals():  # глобальные (для этого скрипта) переменные
  def __init__(self):
    # доступность скрипта + описание для bin/exec/help
    self.dist = {'dist':['arch','red'],
                 'cat' : 'пакеты в ОС',
                 'desc': 'информация о пакетах',
                 'abbr': 'info',
                 'help':  True} # показывать ли "(есть HELP)"

    self.stages = {'ad':{'checkLocal':'----- Проверяем указанные пакеты',
                         'checkRepo' :'----- Ищем в репозиториях',
                         'meld'      :'----- Запускаем meld'}}
    self.adStr  = {'split'   :'#'*50,
                   'deps'    :'#'*18 + ' Зависимости ' + '#'*19,
                   'provides':'#'*20 + ' Provides '    + '#'*20,
                   'pkgSplit':'#'*13 + ' ПАКЕТ: ',
                   'hard'    :'###### жёсткие',
                   'soft'    :'###### мягкие'}

    self.noPkgs  = SF.color('rpmbuild/RPMS','red')
    self.noPkgs += ' пуст; можете указать пакеты при запуске '
    self.noPkgs += SF.color('info ad','blu',True)

    self.tasks = {
      'repo':{'l':{'abbr' :'local',
                   'desc' :'установленный пакет',
                   'zsh'  :'локального пакета'},
              'r':{'abbr' :'repo',
                   'desc' :'репозитории',
                   'zsh'  :'пакета из репозитория'}},
      'task':{'i':{'abbr' :'info',
                   'desc' :'общая информация',
                   'stage':'----- Общая информация о пакете',
                   'pre'  :[]},
              'f':{'abbr' :'files',
                   'desc' :'список файлов',
                   'stage':'----- Файлы пакета',
                   'pre'  :[]}}
      }
    if not G.isArch:
      rpmStr    = SF.color('.rpm','red',True)
      adDesc    = f'сравнение множества локальных {rpmStr} с репозиториями'
      lDescMain = f'установленный пакет или файл {rpmStr} на диске'

      self.tasks['special'] = {'ad':{'abbr1':'auto',
                                     'abbr2':'diff',
                                     'desc' : adDesc,
                                     'func' : autodiff}}
      self.tasks['repo']['l']['desc'] = lDescMain
      self.tasks['task'].update({
        'c' :{'abbr' :'changelog',
              'desc' :'changelog',
              'stage':'----- Changelog пакета',
              'pre'  :[]},
        'd' :{'abbr' :'dependencies',
              'desc' :'зависимости',
              'stage':'----- Зависимости пакета',
              'pre'  :['getDeps']},
        'p' :{'abbr' : 'provides',
              'desc' : 'provides',
              'stage': '----- Provides пакета',
              'pre'  :['getProvides']},
        'v' :{'abbr' :'version',
              'desc' :'версия',
              'pre'  :[]}
        })

    pkgStr  = SF.color('пакет(ы)'  ,'udl')
    taskStr = SF.color('Задача'    ,'udl')
    repoStr = SF.color('База'      ,'ylw',True)
    typeStr = SF.color('Тип данных','grn',True)

    self.help = {
      'base':[
        f'Запуск: info {taskStr.lower()} {pkgStr}',
        '',
        f"{taskStr} = {repoStr.lower()} + {typeStr.lower()} (например, 'ri')"
        ],
      'repo':f'  {repoStr}:',
      'task':f'  {typeStr}:'
      }
SG  = Globals()   # SG = script globals; надо здесь, иначе ошибка :/

class Help(O.Help):
  def printMain(self):
    def _hlSpecial(num:int):
      return SF.hlFirst(data[f'abbr{num}'],'blu',True)
    # шапка
    for line in SG.help['base']: print(line)
    # особые задачи
    if 'special' in SG.tasks.keys():
      print('  Особые:')
      for key,data in SG.tasks['special'].items():
        colored = _hlSpecial(1) + _hlSpecial(2)
        print(f"    {key} [{colored}] - {data['desc']}")
    # основной список задач
    for type in ('repo','task'):
      maxLen = LF.getMaxLen([d['abbr'] for d in SG.tasks[type].values()])
      print(SG.help[type])
      for r,rData in SG.tasks[type].items():
        abbr = SF.hlFirst(rData['abbr'].ljust(maxLen),'blu',True)
        print(f"    {r} [{abbr}] - {rData['desc']}")
  def printZSH (self):
    def _autoget():
      # автоматически собираем комбинации local/repo + задача
      def _getMaxLengths():
        final = {}
        for key in ('repo','task'):
          fList      = [item['abbr'] for item in SG.tasks[key].values()]
          final[key] = LF.getMaxLen(fList)
        return final
      abbrLengths = _getMaxLengths()
      final       = {}

      for r,repo in SG.tasks['repo'].items():
        # сперва выравниваем
        rAbbr = repo['abbr'].ljust(abbrLengths['repo'])
        for t,task in SG.tasks['task'].items():
          tAbbr      = task['abbr'].ljust(abbrLengths['task'])
          final[r+t] = {'desc':f"{task['desc']} {repo['zsh']}",
                        'zsh' :f'[{rAbbr} {tAbbr}]'}
      return final,abbrLengths['repo']+abbrLengths['task']+1
    raw,abbrLen = _autoget()
    # особые задачи
    if   'special' in SG.tasks.keys():
      for key,data in SG.tasks['special'].items():
        abbr = data['abbr1'] + data['abbr2']
        print(f"{key}:[{abbr.ljust(abbrLen)}] {data['desc']}")
    # основной список задач
    for   r in SG.tasks['repo'].keys():
      for t in SG.tasks['task'].keys():
        mKey = r+t
        print(f"{mKey}:{raw[mKey]['zsh']} {raw[mKey]['desc']}")
progress = O.Progress()

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
