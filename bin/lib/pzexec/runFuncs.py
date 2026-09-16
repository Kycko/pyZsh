# функции запуска и остановки программ

from   pathlib    import Path
from   subprocess import Popen
from   sys        import exit as SYSEXIT
from   tempfile   import NamedTemporaryFile
import pzexec.strings         as S
from   zshconf.runFuncs import *
if not G.isArch: import pzexec.packages as PKG

# запуск команд, аргументы
def runWait(cmd:list): Popen(cmd).wait()
def installRPMbuild():
  # сперва проверяет, установлен ли уже rpm-build
  if PKG.RPM(False).query('rpm-build') is None:
    print(S.installRPMbuild)
    return not int(run(['dnf','install','rpm-build'],'rs'))
  else: return True
def meld(data:list,labels=[]):
  # data = список[], внутри 2 или 3 списка (содержимых файлов)
  # labels = заголовки (вкладок, файлов)
  def _createTmpFiles(data:list):
    files = []
    for sList in data:
      f = NamedTemporaryFile(mode='w',delete=False,suffix='.tmp')
      f.write('\n'.join(map(str,sList)))
      f.close()
      files.append(f.name)
    return files
  bin = G.sysBins['meld']
  if bin:
    try:
      tmpfiles = _createTmpFiles(data)
      if labels:
        for lbl,file in zip(labels,tmpfiles): cmd = ['meld','--label',lbl,file]
      else: cmd = ['meld'] + tmpfiles
      run(cmd)
    finally:
      for path in tmpfiles: Path(path).unlink(missing_ok=True)
  else: print(S.noMeldMSG) ; return False

# прочие мелкие
def raiseError(): raise ValueError('app forced ValueError!')

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
