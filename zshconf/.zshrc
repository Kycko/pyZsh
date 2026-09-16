# эта сложная конструкция вычисляет абсолютный путь
dir="${${(%):-%x}:A:h}"

# запускаем zsh-часть
for zFile in "${dir}"/zsh/*.zsh ; do source ${zFile} ; done
# запускаем python-часть
eval "$(python3 "${dir}/init.py")"

# удаляем переменные, чтобы не засорять окружение
unset dir zFile
