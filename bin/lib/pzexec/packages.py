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
import pzexec.listFuncs           as LF
import pzexec.runFuncs            as RF
import pzexec.stringFuncs         as SF
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
  def showInfo (self):
    def _color(string:str): return SF.color(string,'ylw')
    s = S.pkginfo
    leftLen = LF.getMaxLen([attr for attr in s.values()])
    epoch   = self.epoch if self.epoch else S.noEpoch
    final   = (_color(s['name'     ].ljust(leftLen))+' : '+self.name,
               _color(s['epoch'    ].ljust(leftLen))+' : '+epoch,
               _color(s['version'  ].ljust(leftLen))+' : '+self.version,
               _color(s['release'  ].ljust(leftLen))+' : '+self.release,
               _color(s['arch'     ].ljust(leftLen))+' : '+self.arch,
               _color(s['URL'      ].ljust(leftLen))+' : '+self.URL,
               _color(s['buildtime'].ljust(leftLen))+' : '+self.buildtime,
               _color(s['summary'  ].ljust(leftLen))+' : '+self.summary,
               '',
               _color(s['desc'])+':',
               self.desc)
    for line in final: print(line)
  def showFiles(self):
    for path in self.getFiles(): print(path)
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

  # основные функции
  def showChangelog(self):
    # никак не смог получить changelog через библиотеку dnf :/
    # без sudo почему-то НЕ ВСЕГДА показывает список изменений
    final = RF.run(['dnf','repoquery','-q','--changelogs',self.nevra],'st')
    # убираем ненужное сообщение 'Chengelog for...'
    if final[0].startswith('Changelog for'): final.pop(0)
    while final and not final[-1]: final = final[:-1]
    for line in final: print(line)
  def getDeps      (self,type:str):
    # type = r/p/rp (requires & recommends / provides)
    def _depFormat(dep):
      def _getSign(sign):
        # не понял, как это работает, но его надо складывать по битам
        if sign:
          # здесь всегда есть пробелы по бокам, которые нам не нужны
          # поэтому делаем .strip()
          signs = {'EQ':'=','GT':'>','LT':'<'}
          return signs.get(sign,sign).strip()
        else: return sign
      # sign = знак типа <, >, =, <= и т. д.
      return {'name':dep.name,
              'sign':_getSign(dep.relation),
              'ver' :dep.version}
    final = False # для удобства возвращаем статус поиска
    if 'r' in type:
      self.deps = {
        'hard':[_depFormat(dep) for dep in self.api.requires  ],
        'soft':[_depFormat(dep) for dep in self.api.recommends]
        }
      if self.deps['hard'] or self.deps['soft']: final = True
    if 'p' in type:
      self.provides = [_depFormat(dep) for dep in self.api.provides]
      if self.provides: final = True
    return final
  def getFiles     (self): return sorted(self.api.files)
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

  # основные функции
  def showChangelog(self):
    # это СПИСКИ для каждой записи
    times = self.api[rpm.RPMTAG_CHANGELOGTIME]
    names = self.api[rpm.RPMTAG_CHANGELOGNAME]
    texts = self.api[rpm.RPMTAG_CHANGELOGTEXT]

    # RPM выводит записи от новых к старым
    for  i,item in enumerate(texts):
      if i: print() # пустая строка между записями
      # Преобразуем timestamp в формат: "Ср окт 23 2024" (или "Wed Oct 23 2024")
      # Формат %a %b %d %Y наиболее близок к стандартному выводу rpm
      dateStr = datetime.fromtimestamp(times[i]).strftime('%a %b %d %Y')
      print(f'* {dateStr} {names[i]}')
      print(item)
  def getDeps      (self,type:str):
    # type = r/p/rp (requires & recommends / provides)
    def _get(type:str):
      def _getVarNames(type:str):
        if   type == 'hard':
          return {'name':rpm.RPMTAG_REQUIRENAME,
                  'sign':rpm.RPMTAG_REQUIREFLAGS,
                  'ver' :rpm.RPMTAG_REQUIREVERSION}
        elif type == 'soft':
          return {'name':rpm.RPMTAG_RECOMMENDNAME,
                  'sign':rpm.RPMTAG_RECOMMENDFLAGS,
                  'ver' :rpm.RPMTAG_RECOMMENDVERSION}
        elif type == 'provides':
          return {'name':rpm.RPMTAG_PROVIDENAME,
                  'sign':rpm.RPMTAG_PROVIDEFLAGS,
                  'ver' :rpm.RPMTAG_PROVIDEVERSION}
      def _getSign    (sign):
        # не понял, как это работает, но его надо складывать по битам
        signs = {rpm.RPMSENSE_LESS   :'<',
                 rpm.RPMSENSE_GREATER:'>',
                 rpm.RPMSENSE_EQUAL  :'='}
        final = ''
        for mask,char in signs.items():
          if sign & mask: final += char
        return final

      final    = []
      vars     = _getVarNames(type)
      names    = [dep for dep in self.api[vars['name']]]
      # signs = знаки зависимостей (например, '>=')
      signs    = [sgn for sgn in self.api[vars['sign']]]
      versions = [ver for ver in self.api[vars['ver' ]]]

      for i,name in enumerate(names):
        # rpmlib = внутренние зависимости RPM, нам они не нужны
        if not name.startswith('rpmlib('):
          final.append({'name':name,
                        'sign':_getSign(signs[i]),
                        'ver' :versions[i]})
      return LF.rmDoubles(final)
    final = False # для удобства возвращаем статус поиска
    if 'r' in type:
      self.deps = {key:_get(key) for key in ('hard','soft')}
      if self.deps['hard'] or self.deps['soft']: final = True
    if 'p' in type:
      self.provides = _get('provides')
      if self.provides: final = True
    return final
  def getFiles     (self):
    return sorted([file for file in self.api[rpm.RPMTAG_FILENAMES]])

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
