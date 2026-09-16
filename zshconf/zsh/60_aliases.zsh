# универсальная обертка для less
# в РО по умолчанию берём формат spec-файлов
# в Арче это не нужно

less_wrapper() {
  local base=()

  # [[ -t 0 ]] = если открываем файл напрямую (stdin — терминал)
  if [[ "$_pzIsArch" == "True" ]] || [[ -t 0 ]]
    then base=("$@")
    else base=(--syntax=spec)
  fi

  highlight --out-format=xterm256 --style=pablo --quiet --force --line-numbers "${base[@]}" | command less -R
}
