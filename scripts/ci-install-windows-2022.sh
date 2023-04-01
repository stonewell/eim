curl -L https://github.com/neovim/neovim/releases/download/${NVIM_TAG}/nvim-win64.zip -o nvim-win64.zip
unzip nvim-win64
mkdir -p ~/AppData/Local/nvim/pack/nvim-treesitter/start
mkdir -p ~/AppData/Local/nvim-data
cp -r $(NVIM_TREE_SITTER_PATH) ~/AppData/Local/nvim/pack/nvim-treesitter/start
