# файл для создания "приветствий" терминала

# статус git'а
function +vi-git-aheadbehind() {
  local -f _pzGitMisc() { hook_com[misc]+="%f:%F{${1}}${2}" }

  local ahead behind
  ahead=$(command  git rev-list --count @{u}..HEAD 2>/dev/null)
  behind=$(command git rev-list --count HEAD..@{u} 2>/dev/null)

  if (( ! ahead && ! behind ))
    then _pzGitMisc "green" "0"
    else
      (( ahead  > 0 )) && _pzGitMisc "red" "+${ahead}"
      (( behind > 0 )) && _pzGitMisc "red" "-${behind}"
  fi
}

update_git_prompt() {
  vcs_info  # иначе статус git не будет обновляться

  if [[ -n ${vcs_info_msg_0_} ]]
    then
      local STATUS=$(command git status --porcelain 2> /dev/null | tail -n1)
      if [[ -n $STATUS ]]
        then local gitcolor='red'
        else local gitcolor='green'
      fi
      _pzvar="%F{${gitcolor}}${vcs_info_msg_0_}"

      # Раскрываем шаблон из Python в рабочую переменную промпта
      eval '_pzPromptGit="'${_pzPromptBlock}'"'
    else _pzPromptGit=''  # не в репозитории
  fi
}

update_path_prompt() {
  local curDir="${PWD}"
  local suffix=""
  local _pzvar=""
  # флаг, нашли ли мы совпадение в массиве замен
  local matched=0

  # перебираем все ключи (полные пути)
  for fullPath in ${(k)_pzPathDirs}; do
    # проверяем, начинается ли текущий путь с fullPath
    if [[ "${curDir}" == "${fullPath}"* ]]; then
      # получаем сокращённое имя
      local sName="${_pzPathDirs[${fullPath}]}"
      # отрезаем совпавшую часть пути, оставляя хвост подпапок
      suffix="${curDir#$fullPath}"
      # Формируем итоговую подстановку
      _pzvar="${sName}${suffix}"
      matched=1
      break # Выходим из цикла после первого совпадения
    fi
  done

  # если совпадений не найдено
  if [[ ${matched} -eq 0 ]] ; then _pzvar="%~" ; fi

  # Раскрываем шаблон из Python в рабочую переменную промпта
  eval '_pzPromptDir="'${_pzPromptBlock}'"'
}

autoload -Uz vcs_info
zstyle ':vcs_info:*' enable         git
zstyle ':vcs_info:*' actionformats '%b%m'
zstyle ':vcs_info:*' formats       '%b%m'
zstyle ':vcs_info:git*+set-message:*' hooks git-aheadbehind
# ↓ важно, иначе запускается алиас
zstyle ':vcs_info:git:*' command git

# Регистрируем хук precmd в Zsh
autoload -Uz add-zsh-hook
add-zsh-hook precmd update_git_prompt
add-zsh-hook precmd update_path_prompt
