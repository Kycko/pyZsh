# общие функции обработки строк

from   sys import exit    as SYSEXIT
import pzexec.globalFuncs as GF
import pzexec.globals     as G

# в агрументах используем название colr
# чтобы не было путаницы с функцией color

# поиск
def findSub     (string:str,sub :str ,type='bool',fullText=False,lower=True,strip=''):
  # type может быть 'index' или 'bool'
  # если fullText=True, проверяется равенство строк (но после .trim() + можно задать lower=True)
  # если lower   =True, все строки будут сравниваться через .toLowerCase()
  # strip может быть '' / 'a' (для string) / 'b' (для sub) / 'ab'
  if 'a' in strip: string = string.strip()
  if 'b' in strip: sub    = sub   .strip()

  if fullText and len(string) != len(sub): return GF.getIB(type,-1)
  if lower:
    string = string.lower()
    sub    = sub   .lower()

  return GF.getIB(type,string.find(sub))
def checkSubList(string:str,subs:list,fullText=False,lower=True,strip=''):
  # возвращает True, если найдёт ЛЮБОЙ элемент subs в string
  for sub in subs:
    if findSub(string,sub,'bool',fullText,lower,strip): return True
  return False

# преобразование
def color       (string:str,colr:str,bold=False):
  colors          = G.colors['term']
  final           =   colors[colr]
  if bold: final +=   colors['bld']
  final          +=   str(string) # защита от TypeError
  final          +=   colors['rst']
  return final
def findToColor (string:str,sub :str,colr:str,bold=False):
  # подсвечивает все найденные sub
  return color(sub,colr,bold).join(string.split(sub))
def hlFirst     (string:str,colr:str,bold=False):
  # подсвечивает первую букву в string
  return color(string[0],colr,bold=bold) + string[1:]
def cutColors   (string:str): # вырезает из строки все цвета
  # можно использовать для правильного подсчёта длины строки
  for color in G.colors['term'].values():
    string = string.replace(color,'')
  return string
def alignColored(string:str,finalLen:int):
  # здесь ljust() не используем: он не учитывает цвета
  addLen = finalLen - len(cutColors(string))
  return string + ' '*addLen

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
