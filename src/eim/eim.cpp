#include <iostream>
#include <string>

#include "CLI/CLI.hpp"
#include "platform_folders.h"
#include "spdlog/spdlog.h"
#include "toml++/toml.hpp"

#include <sstream>

template <typename T> std::string to_string(T v) {
  std::stringstream ss;
  ss << v;

  return ss.str();
}

int main(int argc, char **argv) {
  CLI::App app{"App description"};
  argv = app.ensure_utf8(argv);

  std::string filename = "default";
  app.add_option("-f,--file", filename, "A help string");

  CLI11_PARSE(app, argc, argv);

  std::cout << "Config: " << sago::getConfigHome() << "\n";
  std::cout << "Data: " << sago::getDataHome() << "\n";
  std::cout << "State: " << sago::getStateDir() << "\n";
  std::cout << "Cache: " << sago::getCacheDir() << "\n";
  std::cout << "Documents: " << sago::getDocumentsFolder() << "\n";
  std::cout << "Desktop: " << sago::getDesktopFolder() << "\n";
  std::cout << "Pictures: " << sago::getPicturesFolder() << "\n";
  std::cout << "Music: " << sago::getMusicFolder() << "\n";
  std::cout << "Video: " << sago::getVideoFolder() << "\n";
  std::cout << "Download: " << sago::getDownloadFolder() << "\n";
  std::cout << "Save Games 1: " << sago::getSaveGamesFolder1() << "\n";
  std::cout << "Save Games 2: " << sago::getSaveGamesFolder2() << "\n";

  spdlog::info("Welcome to spdlog!");
  spdlog::error("Some error message with arg: {}", sago::getConfigHome());

  auto v = R"([a]
        b = [
        {c = 42},
        {c = 54}
        ])";

  const auto toml_v = toml::parse(v);

  const auto a = toml_v["a"]["b"];
  spdlog::info("{}", to_string(a));

  spdlog::info("option f={},{}", filename,
               to_string(toml::json_formatter(*a.node())));
  spdlog::info("option f={},{}", filename,
               to_string(toml::yaml_formatter(*a.node())));
  return 0;
}
