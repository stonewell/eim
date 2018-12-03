#pragma once

#include <string>
#include "buffer.h"

namespace eim {

class FileBuffer : public virtual Buffer {
public:
    FileBuffer() = default;
    virtual ~FileBuffer() = default;

public:
    virtual bool LoadFromFile(const std::string & file_path) = 0;
    virtual bool SaveToFile(const std::string & file_path) = 0;
    virtual bool Save() = 0;

    virtual const std::string & GetFilePath() const = 0;
};

BufferPtr CreateFileBuffer(const std::string & file_path);

}; //namespace eim
