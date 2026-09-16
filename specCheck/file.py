# класс File с основной логикой обработки specCheck

from   sys import exit         as SYSEXIT
import pyzsh.globalFuncs       as GF
import pyzsh.output            as O
import pyzsh.specCheck.globals as SG  # script globals

class File():
  def __init__(self,filepath:str):
    self.filepath = filepath
    self.prg      = O.Progress()
    self.db       = {}  # данные файла (что найдёт парсер)
    self.errors   = []  # хранилище всех ошибок

    try   : self.raw = GF.readFile(filepath)  # список[] строк
    except: self.raw = None
  def parse   (self):
    def _preCheck    ():  # проверяем только наличие шапки и её полноту
      pass
    def _parseSection(section:str):
      def _find(rq:dict): # rq{} = request
        def _checkPair(line:str,rq:dict):
          def _subCheck(string:str,splitter:str):
            splitted = string.split(splitter)
            # в списке один элемент, если разделение не произошло
            if len(splitted) > 1:
              if   key == 'pre' : return splitter.join(splitted[1:])
              elif key == 'post': return splitted[0]
          final = line
          for key,splitter in rq['search'].items():
            final = _subCheck(final,splitter)
            if final is None: return None
          return final
        for line in self.raw:
          res = _checkPair(line,rq)
          if res is not None: return res
      self.db[section] = {}
      for key,data in SG.parser[section].items():
        self.db[section][key] = _find(data)
    def _checkParser ():
      final = []
      for   mKey,mData in SG.parser.items():
        for sKey,sData in mData.items():
          if sData['mandatory'] and self.db[mKey][sKey] is None:
            final.append([mKey,sKey])
      if final:
        self.errors.append(SG.errorMsg['parser']) # заголовок
        for pair in final: self.errors.append('   ' + ' : '.join(pair))

    self.prg.startStep('парсим файл',self.initNum)
    _preCheck()
    if not self.errors: # могут быть ошибки после _preCheck()
      for section in SG.parser.keys(): _parseSection(section)

    _checkParser()
    self.prg.finishStep(not self.errors)

  def printFinal(self):
    self.prg.pkgStage('----- Ошибки в файле',self.filepath,'red')
    for error in self.errors:
      print(error)
    return

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
