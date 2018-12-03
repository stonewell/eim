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
    virtual bool Load() = 0;

    virtual const std::string & GetFilePath() const = 0;
};

using FileBufferPtr = std::shared_ptr<FileBuffer>;

FileBufferPtr CreateFileBuffer(const std::string & file_path, BufferPtr buf);
FileBufferPtr CreateFileBuffer(const std::string & file_path);
FileBufferPtr CreateFileBuffer(BufferPtr buf);
FileBufferPtr CreateFileBuffer();

}; //namespace eim
