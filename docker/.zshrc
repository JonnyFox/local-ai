[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

export PNPM_HOME="/root/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HO👨:"*) ;;
  *) export PATH="$PNPM_HO👨:$PATH" ;;
esac

export LS_OPTIONS='--color=auto'
eval "`dircolors`"
alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -l'
alias l='ls $LS_OPTIONS -lA'

# Some more alias to avoid making mistakes:
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias pnpx='pnpm dlx'
alias pnx='pnpm dlx'
alias nr='pnpm run'
alias ns='pnpm start'
alias pm='python manage.py'
alias pm-m='pm migrate'
alias pm-mm='pm makemigrations'
alias pm-ct='pm create_translations'
alias pm-ut='pm update_translations'
alias pm-ct-ut='pm-ct && pm-ut'
alias pm-t='pm test'
alias pm-tk='pm test --keepdb'
alias pm-s='pm shell_plus'