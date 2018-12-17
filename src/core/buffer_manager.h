#pragma once

#include "buffer.h"
#include "file_buffer.h"
#include <memory>

namespace eim {
class BufferManager {
public:
    BufferManager() = default;
    virtual ~BufferManager() = default;

public:
    virtual BufferPtr GetBuffer(std::wstring name, bool create = true) = 0;
    virtual FileBufferPtr GetFileBuffer(std::string file_path, bool create = true) = 0;
};

using BufferManagerPtr = std::shared_ptr<BufferManager>;

BufferManagerPtr CreateBufferManager();
}; //namespace eim
