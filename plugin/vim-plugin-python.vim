if !has("python3")
  echo "vim has to be compiled with +python3 to run this"
  finish
endif

if exists('g:sample_python_plugin_loaded')
  finish
endif

let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

python3 << EOF
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
import plugin
EOF

let g:sample_python_plugin_loaded = 1

" This function calls the create_extract function in the python file.
function! Extract()
    python3 plugin.create_extract()
endfunction

" This allows the function to be called like :Extract rather than :Extract()
command! -nargs=0 Extract call Extract()
