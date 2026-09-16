# отдельная библиотека для комплексной проверки spec-файлов

from   sys                  import exit as SYSEXIT
import pyzsh.output                     as O
from   pyzsh.specCheck.file import File

# основная функция, запускаемая командой spec check
def main(paths:list):
  def _read(paths:list):
    final = []
    for i,path in enumerate(paths,start=1):
      counter = i if len(paths) > 1 else None
      O.Progress().startStep('читаем файл',counter)
      fObj = File(path)
      if O.Progress().finishStep(bool(fObj.raw),path):
        fObj.initNum = counter  # сохраняем номер, чтобы не было путаницы
        final.append(fObj)
    return final
  files = _read(paths)  # список[] объектов File()
  for file in files: file.parse()
  for file in files:
    if file.errors: file.printFinal()

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
