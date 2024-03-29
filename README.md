# eim
## Install
```
pip install git+https://github.com/stonewell/eim.git
```

## Editor Improved

- [ ] Piece Table with Tree
- [X] Treesitter
  - [x] Syntax Highlighting
  - [X] Auto indent
    - [X] aligned indent
  - [X] leverage nvim treesitter queries
- [ ] LSP
- [X] EditorConfig
  - [X] indent
  - [ ] code page
  - [X] tab size
  - [ ] save trim trail space and add new line
- [ ] Search Everything
- [x] Color Schema
- [ ] Format file
- [x] KeyBinding
- [x] PySide6
- [x] Keybinding with prefix key, built-in support by pyside6
- [ ] Flycheck
- [X] Status Line
- [X] Editing server/client

## TODO
- [X] ask for input
- [X] directory content plugin support path input
- [ ] show error message
- [X] syntax high light for multiple line string, comment
  - [X] syntax highlight deal with selected content, handled by QT, but need to refine the text/background color
  - [ ] considering re-impl selection with extra selection to keep syntax high light when lines selected
- [ ] file modified outside detect
- [X] prompt for save when quit/close
- [X] confirm for overwrite
- [ ] editing feature complete
  - [X] close buffer
  - [X] kill char
  - [X] kill line
  - [X] search
  - [X] regex search
  - [X] replace
  - [X] regex replace
  - [X] undo
  - [X] redo
  - [X] paste with history
  - [X] Search in files with ag/rg
    - [X] find file in project root
	- [X] search in project root
	- [ ] list item performance
  - [X] backspace back indent at line begin
    - [X] should align with indent
  - [X] search wrap
  - [X] goto line
- [X] detect language using file suffix, then use guesslang
- [X] force buffer lang
- [ ] recent files
- [X] guess indention of file
- [ ] guess new line style of file
- [ ] message buffer
- [X] quit should check all buffer status
- [ ] split editor pane
  - [X] switch pane command
  - [X] close pane
  - [X] close all other pane
  - [ ] update pane size when split/close
- [X] pub/sub should only handle own events
- [ ] content window should be global not belows to editor
