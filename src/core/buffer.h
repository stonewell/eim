#pragma once

#include <memory>

namespace eim {
class Buffer {
public:
    Buffer() = default;
    virtual ~Buffer() = default;

public:
    virtual void Insert(size_t offset, const wchar_t * data, size_t len) = 0;
    virtual void Delete(size_t offset, size_t len) = 0;

    virtual size_t GetLength() const = 0;

    virtual size_t GetLineCount() = 0;
    /*
     * get the line raw data, len=0 means return as much as there is. line_offset is raw data start in the line
     * return raw data real size. a line raw data may return in multiple pieces
     */
    virtual size_t GetLine(size_t index, wchar_t * & data, size_t len = 0, size_t line_offset = 0) = 0;
    virtual size_t GetLineLength(size_t index) const = 0;
    virtual size_t GetLineStartOffset(size_t index) const = 0;
};

using BufferPtr = std::shared_ptr<Buffer>;
}; //namespace eim
