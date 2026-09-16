# запросы к базам DNF и RPM (для репозиториев и локальных пакетов)

# Функции и свойства в классах DNF/RPM ДОЛЖНЫ ИМЕТЬ ОДИНАКОВЫЕ ИМЕНА
# И ВОЗВРАЩАТЬ ОДИНАКОВЫЕ ОБЪЕКТЫ для удобства обработки
# self.api = главный объект, из которого будем доставать инфу

import rpm
from   dnf         import Base    as dnfBase
from   dnf.subject import Subject as DNFsubject
from   datetime    import datetime
from   pathlib     import Path
from   sys         import exit    as SYSEXIT
import pzexec.strings             as S

class DNF():
  def __init__(self):
    # сюда больше ничего не добавляем
    # этот минимальный алгоритм используется для "прогрева" кеша
    try:
      self.api = dnfBase()
      self.api.read_all_repos()
      self.api.fill_sack()
      self.dbLoaded = True  # для проверки, что try выполнился
    except Exception: self.dbLoaded = False

  # найти пакет через DNF
  def query(self,pkg:str,filterArch=True):
    # DNFsubject парсит NEVRA, выдаёт несколько вариантов
    parsed = DNFsubject(pkg)
    if parsed:
      query = parsed.get_best_query(self.api.sack).available().latest()
      pkgs  = list(query)
      if pkgs:
        final = pkgs[0]
        if filterArch:
          final = next((p for p in pkgs if p.arch == self.api.conf.arch),final)
        # возвращаем ОДИН объект пакета
        return DNFpackage(final)
class RPM():
  def __init__(self,onlyFile:bool):
    self.api      = rpm.TransactionSet()
    self.onlyFile = onlyFile
    self.dbLoaded = True
  def query   (self,pkg:str): # найти пакет через RPM
    # pkg может быть просто именем установленного пакета либо путём к файлу .rpm
    def _readFile(path:str):  # возвращает объект файла .rpm
      try:
        with open(path,'rb') as file: return self.api.hdrFromFdno(file.fileno())
      except Exception: print(S.noFile)
    def _getPkg  (pkg :str):  # возвращает объект установленного пакета
      mi = self.api.dbMatch('name',pkg)
      # берём первое совпадение из итератора; если пакет не найден, вернётся None
      if len(mi): return next(mi)

    if Path(pkg).exists() and pkg.endswith('.rpm'):
      found = _readFile(pkg)
    elif not self.onlyFile: found = _getPkg(pkg)
    else: return None

    if found: return RPMpackage(found)

# несколько общих функций для DNF/RPMpackage
# O.Progress.checkPkgs() добавляет ещё свойство self.initNum
# self.initNum = номер пакета в шагах прогресса
class PKGtemplate:
  def __init__ (self):
    self.buildtime = datetime.fromtimestamp(self.buildtime).strftime('%d.%m.%Y')
    self.EVR = f'{self.version}-{self.release}'
    if self.epoch is None: self.epoch = ''
    else:
      self.epoch = str(self.epoch)
      self.EVR   =  f'{self.epoch}:{self.EVR}'
class DNFpackage(PKGtemplate):
  def __init__(self,pkgObj):
    self.api       = pkgObj
    self.nevra     = str(pkgObj)
    self.name      = pkgObj.name
    self.epoch     = pkgObj.epoch
    self.version   = pkgObj.version
    self.release   = pkgObj.release
    self.arch      = pkgObj.arch
    self.URL       = '' if pkgObj.url is None else pkgObj.url
    self.summary   = pkgObj.summary
    self.desc      = pkgObj.description
    self.buildtime = pkgObj.buildtime
    super().__init__()
class RPMpackage(PKGtemplate):
  def __init__(self,RPMheader):
    self.api = RPMheader
    # [] опускают эпоху, иначе там будет (none)
    format         = '%{NAME}-[%{EPOCH}:]%{VERSION}-%{RELEASE}.%{ARCH}'
    tempURL        = self.api[rpm.RPMTAG_URL]

    self.nevra     = self.api.sprintf(format)
    self.name      = self.api[rpm.RPMTAG_NAME]
    self.epoch     = self.api[rpm.RPMTAG_EPOCH]
    self.version   = self.api[rpm.RPMTAG_VERSION]
    self.release   = self.api[rpm.RPMTAG_RELEASE]
    self.arch      = self.api[rpm.RPMTAG_ARCH]
    self.URL       = '' if tempURL is None else tempURL
    self.summary   = self.api[rpm.RPMTAG_SUMMARY]
    self.desc      = self.api[rpm.RPMTAG_DESCRIPTION]
    self.buildtime = self.api[rpm.RPMTAG_BUILDTIME]
    super().__init__()

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
