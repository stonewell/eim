# eim
## Editor Improved

- [ ] Piece Table with Tree
- [X] Treesitter
  - [x] Syntax Highlighting
  - [X] Auto indent
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

## TODO
- [ ] ask for input
- [X] directory content plugin support path input
- [ ] show error message
- [X] syntax high light for multiple line string, comment
  - [X] syntax highlight deal with selected content, handled by QT, but need to refine the text/background color
  - [ ] considering re-impl selection with extra selection to keep syntax high light when lines selected
- [ ] file modified outside detect
- [ ] prompt for save when quit/close
- [ ] editing feature complete
  - [X] close buffer
  - [X] kill char
  - [X] kill line
  - [X] search
  - [X] regex search
  - [ ] replace
  - [ ] regex replace
  - [X] undo
  - [X] redo
  - [X] paste with history
  - [ ] Search in files with ag/rg
  - [X] backspace back indent at line begin
  - [X] search wrap
- [X] detect language using file suffix, then use guesslang
- [X] force buffer lang
- [ ] recent files
- [ ] guess indention of file
- [ ] guess new line style of file
- [ ] message buffer
