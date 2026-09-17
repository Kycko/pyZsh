# всё важное, что должно выполняться в самом конце

from   datetime import datetime,timedelta
from   sys      import exit as SYSEXIT
import zshconf.fileFuncs    as FF
import zshconf.globals      as G

def _export  (db:dict,key:str):
  for var,value in db.items(): print(f'{key} {var}="{value}"')
def _updCache(timeout:int,task:str):
  # timeout = минимальное количество ЧАСОВ,
  # которое должно пройти с предыдущего обновления
  # более часто не обновляем, но при необходимости можем сделать это вручную
  def _check():
    # здесь такая логика, чтобы обновление стартовало, если кеша ещё не существует
    # ↓ не выдаёт ошибок, даже если нет родительских каталогов
    try:
      file   = G.files['cache']['updTime'][task]
      parsed = FF.readFile(file)[0].strip().split()
      pTime  = parsed.pop(0)

      if parsed:
        fresh = parsed.pop(0) == 'True'
        if not fresh: return True
      else: fresh = True

      if fresh:
        pTime = datetime.fromtimestamp(float(pTime))
        if datetime.now() - pTime < timedelta(hours=timeout): fresh = False

      return fresh
    except: return True
  # 'ty' важен, чтобы не ждать завершения
  if _check(): print(f"{G.aliases['updCache']} {task} ty &!")
def _myBins  ():
  for name,props in G.myBins.items():
    init = G.files['binInit']
    file = props['file'].name
    print(name + '() {')
    print(f'python3 {init} {file} "$@"')
    print('}')

_export(G.exports,'export')
_export(G.aliases,'alias')

# мои скрипты выдаём в виде функций, а не алиасов
# иначе не будут работать автодополнения
_myBins()

# запускаем обновление моих кешей в фоне
# отдельными процессами, не дожидаясь их завершения
# для DNF 4 часа, чтобы почаще прогревать
if not G.isArch: _updCache(4,'dnf')
if not G.inVirt: _updCache(4,'pyZsh')

# clear в TTY обновляет цвета всего экрана
# в guiterm этого не делаем, чтобы не сбрасывать экран при подключении по SSH
if G.firstShell and not G.guiterm: print('clear')
print('fastfetch')

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
