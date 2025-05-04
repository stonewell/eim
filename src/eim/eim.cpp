#include <iostream>
#include <string>

#include "platform_folders.h"
#include "spdlog/spdlog.h"

int main()
{
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
return 0;
}
