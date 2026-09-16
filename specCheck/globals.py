# глобальные переменные для specCheck

from sys import exit as SYSEXIT

errorMsg = {'header':'Шапка с лицензией не найдена или не соответствует шаблону',
            'parser':'Не найдено парсером:'}

# для проверки того, что вся шапка указана и она правильная
header = [
  '# spec file for package *****',
  '# rules v.1.0',
  '#',
  '# Copyright (c) ***** RED SOFT',
  '# The license for this file, and modifications and additions to the',
  '# file, is the same license as for the pristine package',
  '# itself (unless the license for the pristine package is not an',
  '# Open Source License, in which case the license is the MIT License).',
  '#',
  '# Copyright (c) ***** РЕД СОФТ',
  '# Лицензия на этот файл, а также на изменения и дополнения к файлу,',
  '# является той же, что и для самого пакета (за исключением случаев,',
  '# когда лицензия на пакет не является лицензией с открытым исходным',
  '# кодом, в этом случае лицензией является лицензия MIT).'
  ]

parser = {
  'header':{
    'pkg'   :{'mandatory':True,'search':{'pre':'spec file for package '}},
    'enYear':{'mandatory':True,'search':{'pre':'Copyright (c) ','post':' RED SOFT'}},
    'ruYear':{'mandatory':True,'search':{'pre':'Copyright (c) ','post':' РЕД СОФТ'}}
    }
  }

# защита от запуска модуля
if __name__ == '__main__':
  print  ("This is module, please don't execute.")
  SYSEXIT()
