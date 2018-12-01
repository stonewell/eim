#pragma once

#include <string>
#include "buffer.h"

namespace eim {

class FileBuffer : public virtual Buffer {
public:
    FileBuffer() = default;
    virtual ~FileBuffer() = default;

public:
    virtual bool LoadFromFile(const std::string & file_path);
};

}; //namespace eim
