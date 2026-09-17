# общие для нескольких скриптов функции вывода на экран разной информации

# НЕ МЕНЯТЬ ПОРЯДОК во избежание частичных импортов
from   sys import exit    as SYSEXIT
import pzexec.fileFuncs   as FF
import pzexec.globals     as G
import pzexec.runFuncs    as RF
import pzexec.strings     as S
import pzexec.stringFuncs as SF
import pzexec.listFuncs   as LF
if not G.isArch: import pzexec.packages as PKG

# шаблон, реализация try-except
class Help():
  # init + обёртки (реализация try-except)
  def __init__ (self,appFunc,taskdb:dict,args:list,debug:bool):
    # appFunc = какую функцию запустить, если все проверки пройдут
    self.db   = taskdb
    self.args = args
    try:
      # remove() выдаст ValueError, если флаг отсутствует
      args.remove(G.zshFlag) ; self.printZSH()
    except:
      self.debug = debug
      with self: appFunc(args)
  def __enter__(self): return self
  def __exit__ (self,type,val,tb):
    if type:  # если произошла ошибка
      self.printMain()
      if self.debug: print() ; print(S.separator) ; print()
      return not self.debug # 'return True' подавляет ошибку

  # вывод основной справки и дополнений zsh
  def getTask    (self):
    cur = self.db
    try:
      for arg in self.args: cur = cur[G.tk + arg]
    except: pass
    return cur
  def printMain  (self):
    # в Globals() обозначаем:
    #   аргументы-подпункты должны начинаться с G.tk (например, '::revert')
    #   сообщения перед/после списка: '_pre':[]/'_post':[]
    #   разделитель abbr и desc: 'sep'
    def _getLeftLen(db  :dict):
      found = []
      for  tKey,tData in db.items():
        if tKey.startswith(G.tk): found.append(tData['abbr'])
      return LF.getMaxLen(found)
    def _getLine   (data:dict,leftLen:int):
      left  = SF.alignColored(data['abbr'],leftLen)
      final = f"  {left} {data['sep']} {data['desc']}"
      if data['help']: final += f' {S.ownHelp}'
      return final

    db      = self.getTask()
    leftLen = _getLeftLen(db)
    for line in db['_pre']: print(line)
    for  tKey,tData in db.items():
      if tKey.startswith(G.tk): print(_getLine(tData,leftLen))
    for line in db['_post']: print(line)
  def printZSH   (self):
    printed = False
    db = self.getTask()
    for  k,d in db.items():
      if k.startswith(G.tk):
        printed = True
        print(f"{d['zsh']}:{d['desc']}")
    if not printed and 'zSugg' in db.keys(): print(db['zSugg'])
  def zshPackages(self,local:bool):
    def _local():
      if G.isArch: cmd = ['pacman','-Qq']
      else       : cmd = ['rpm','-qa','--qf','%{NAME}\n']

      try   : final = RF.run(cmd,'t')
      except: final = []

      return final
    def _repos():
      file = G.files['cache']['pkglist']

      if file.is_file(): final = FF.readFile(file)
      # фоллбэк на случай отсутствия файла кеша
      elif G.isArch: final = RF.run(['pacman','-Slq'],'t')
      else:
        final = []
        for  pkg in PKG.DNF().api.sack.query().available().latest():
          if pkg.arch in ('x86_64','noarch') and pkg.name not in final:
            final.append(pkg.name)
      return final

    # функция печатает пакеты для дополнения zsh
    # local = установленные либо все из репозиториев
    final = _local() if local else _repos()
    for line in final: print(line)

# отрисовка текущего действия и статуса (OK/FAILED)
class Progress():
  def __init__(self):
    self.counterLen = 0 # доп. длина сообщений в шагах (для счётчика)
  #### основные этапы выполнения
  def startStage(self,title:str,color:str,bold=True):
    print() ; print(SF.color(title,color,bold))
  def pkgStage  (self,title:str,pkg  :str,titleColor='blu'):
    fTitle = SF.color(title,titleColor,True)
    fPkg   = SF.color(pkg  ,'ylw',True)
    print() ; print(f'{fTitle}: {fPkg}')
  #### шаги (действия внутри основных этапов)
  def startStep      (self,string:str ,counter:int=None):
    def _align(txt:str):
      length = len(SF.cutColors(txt))
      max    = G.maxStepLen + self.counterLen
      for i in range(length,max): txt += '.'
      return txt
    if counter: string += f' [{counter}]'
    print(_align(string),end='',flush=True)
  def finishStep     (self,status:bool,tip=''):
    # для сокращения кода возвращаем этот же статус
    # tip = любой текст, будет выведен в скобках
    final = S.progress['steps']['status'][status]
    if tip: final += f' ({tip})'
    print(final)
    return status
  def finishStepCount(self,count :int ,savePos=False):
    # выводит одну финальную цифру
    # для сокращения кода возвращаем эту же цифру
    # savePos нужен для счётчика, возвращать каретку к началу числа
    end   = ''    if savePos else '\n'
    color = 'blu' if count   else 'red'
    print(SF.color(str(count),color,True),end=end,flush=True)
    if savePos: print('\b' * len(str(count)), end='')
    return count

  #### специфические действия, но нужные для нескольких скриптов
  def checkPkgs(self,pkgs:list,rpm:bool,onlyFile=False):
    # запускает проверку множества пакетов
    # onlyFile нужен для rpm=True:
    #   он отключает поиск установленных, берём только файлы .rpm с диска
    def _checkPkg(pkg:str,counter:int):
      # ВСЕГДА запускаем через checkPkgs, поэтому эта функция спрятана внутрь
      self.startStep(S.progress['steps']['pkg']['check'],counter)
      found = self.pkgDB.query(pkg)
      if found: tip = SF.findToColor(found.nevra,pkg,'ylw',True)
      else    : tip = ''

      if self.finishStep(bool(found),tip):
        # сохраняем номер на будущее, чтобы у пользователя не было путаницы
        found.initNum = counter
        return found
    if len(pkgs) > 1:
      self.counterLen = len(str(len(pkgs))) + 3 # +3: пробел и две скобки []
    self.startStep(S.progress['steps']['upd'])
    final = []
    self.pkgDB = PKG.RPM(onlyFile) if rpm else PKG.DNF()
    if self.finishStep(self.pkgDB.dbLoaded):
      for i,pkg in enumerate(pkgs,start=1):
        counter = i if len(pkgs) > 1 else None
        found   = _checkPkg(pkg,counter)
        if found: final.append(found)
      # возвращаем всегда список ОБЪЕКТОВ пакетов
      return final

  ### зависимости
  def hardSoftDepHeader(self,type:str ,count:int):
    def _printSeparator(): print('-'*sepLen)
    tObj     = S.tableHeaders['deps'][type]
    # sep = separator
    sepLen   = len(SF.cutColors(tObj)) + len(str(count)) + 7
    countStr = SF.color(str(count),'blu' if count else 'red',True)

    _printSeparator()
    print(f'| {tObj} | {countStr} |')
    if not count: _printSeparator()
    return sepLen # возвращаем для выравнивания остальной таблицы
  def getDeps          (self,pkgs:list,type:str):
    # pkgs = список[] объектов DNF/RPMpackage
    # type = r/p/rp (requires & recommends / provides)
    # функция возвращает ТОЛЬКО пакеты хотя бы с одной зависимостью
    def _counter(type:str,pkg):
      final = 0
      if 'r' in type:
        final += len(pkg.deps['hard']) + len(pkg.deps['soft'])
      if 'p' in type: final += len(pkg.provides)
      return final
    final = []
    mKey  = ('provs','deps')['r' in type]
    msg   = S.progress['steps']['pkg'][mKey]
    for pkg in pkgs:
      self.startStep(msg,pkg.initNum)
      if pkg.getDeps(type): final.append(pkg)
      self.finishStepCount(_counter(type,pkg))
    return final
  def showDeps         (self,pkg ,type:str):
    # pkg = ОДИН объект DNF/RPMpackage
    # type = r/p/rp (requires & recommends / provides)
    def _output(deps:dict,hKey:str,minLen=0):
      # hKey = header key
      if deps:  # без этого будет выводить пустые мягкие зависимости
        final = []
        for dep in deps:
          final.append([dep['name'], f"{dep['sign']} {dep['ver']}"])
        # ↓ вроде как сортирует по элементам первого столбца
        final.sort(key=lambda x:x[0])
        showTable(S.tableHeaders['deps'][hKey],final,minLen)
    if 'r' in type:
      for hardsoft,deps in pkg.deps.items():
        sepLen = self.hardSoftDepHeader(hardsoft,len(deps))
        _output(deps,'deps',sepLen)
    if 'p' in type: _output(pkg.provides,'provides')
  def whoRequires      (self,pkgs:list):
    # pkgs = список[] объектов DNF/RPMpackage
    final = []
    for pkg in pkgs:
      self.startStep(S.progress['steps']['pkg']['wReq'],pkg.initNum)
      self.pkgDB.whoRequires(pkg)
      count = len(pkg.whoRequires['hard'])+len(pkg.whoRequires['soft'])
      if self.finishStepCount(count): final.append(pkg)
    return final
  def show_whoRequires (self,pkgs:list):
    def _output(deps:dict,minLen=0):
      if deps:  # без этого будет выводить пустые
        final = []
        for pkg,depList in deps.items():
          for i,dep in enumerate(depList):
            line = [S.samePkg if i else pkg]  # pkg = NEVRA
            line .append(dep['name'])
            line .append(f"{dep['sign']} {dep['ver']}")
            final.append(line)
        showTable(S.tableHeaders['whoRequires'],final,minLen)
    for pkg in pkgs:
      self.pkgStage(S.progress['stages']['whoRequires'],pkg.nevra)
      for hardsoft,deps in pkg.whoRequires.items():
        sepLen = self.hardSoftDepHeader(hardsoft,len(deps))
        _output(deps,sepLen)

def showTable(header:list,data:list,minLen=None):
  # цвета везде нужны разные, поэтому ЗДЕСЬ НИЧЕГО НЕ КРАСИМ
  # другие функции и скрипты сами должны добавлять цвет
  # а эта функция только считает длины строк и выводит красивую таблицу
  # header[] = список заголовков (для каждого столбца)
  # data[[]] = список строк, в каждой строке список по столбцам
  # minLen   = [опционально] минимальная длина строки для выравнивания
  # вырезаем все цвета для правильного подсчёта длин
  def _getLengths    (header:list,data:list,minLen:int):
    lengths = [len(SF.cutColors(item)) for item in header]
    for line in data:
      for i,cell in enumerate(line):
        fLen = len(SF.cutColors(cell))
        if fLen > lengths[i]: lengths[i] = fLen

    total = sum(lengths) + 3*len(lengths) + 1
    if total < minLen:
      lengths[0] += minLen-total
      total       = minLen
    return lengths,total
  def _printSeparator(): print('-'*lenTotal)
  def _printLine     (line:list):
    final = '| '
    for i,cell in enumerate(line):
      final += SF.alignColored(cell,lenCols[i]) + ' | '
    print(final[:-1]) # лишний пробел

  # lenCols = список[] по столбцам
  lenCols,lenTotal = _getLengths(header,data,minLen)
  _printSeparator()
  _printLine(header)
  _printSeparator()
  for line in data: _printLine(line)
  _printSeparator()

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
