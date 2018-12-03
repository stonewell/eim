#pragma once

#include <memory>

namespace eim {

struct LinePosition {
    size_t line;
    size_t offset;
};

class Buffer {
public:
    Buffer() = default;
    virtual ~Buffer() = default;

public:
    virtual void Insert(size_t offset, const wchar_t * data, size_t len) = 0;
    virtual void Delete(size_t offset, size_t len) = 0;

    virtual size_t GetLength() = 0;

    virtual size_t GetLineCount() = 0;
    /*
     * get the line raw data start from the line position, len=0 means return as much as there is.
     * return raw data real size. a line raw data may return in multiple pieces
     */
    virtual size_t GetLineData(const LinePosition & line_pos, const wchar_t * & data, size_t len = 0) = 0;
    virtual size_t GetLineLength(size_t index) = 0;
    virtual size_t GetLineStartOffset(size_t index) = 0;

    virtual size_t LinePositionToDocPos(const LinePosition & line_pos) = 0;
    virtual LinePosition DocPosToLinePosition(size_t offset) = 0;
};

using BufferPtr = std::shared_ptr<Buffer>;

BufferPtr CreateBuffer();

}; //namespace eim
