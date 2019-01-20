" vim: ts=4 sw=4 et

function! PostProcessingPytropos(entry)
    " Pytropos uses 0-indexed columns, and Neovim uses 1-indexed
    let a:entry.col += 1

    if a:entry.text =~# '^E'  ||  a:entry.text =~# '^SyntaxError'
        let a:entry.type = 'E'
    elseif a:entry.text =~# '^W'
        let a:entry.type = 'W'
    elseif a:entry.text =~# '^F'
        let a:entry.type = 'F'
    else
        let a:entry.type = 'A'
    endif
endfunction

let g:neomake_python_pytropos_maker = {
   \ 'exe': 'paver',
   \ 'args': ['run'],
   \ 'errorformat':
     \ '%f:%l:%c: %m',
  \ 'postprocess': [
     \ function('PostProcessingPytropos'),
     \ ]
  \ }

let g:neomake_python_enabled_makers = ['pytropos']
