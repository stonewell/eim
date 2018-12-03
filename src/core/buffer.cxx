#include "buffer.h"
#include "file_buffer.h"

#include <vector>
#include <iostream>

namespace eim {
namespace impl {

class BufferImpl : public virtual Buffer {
public:
    BufferImpl() {};
    virtual ~BufferImpl() {}

public:
    virtual void Insert(size_t offset, const wchar_t * data, size_t len);
    virtual void Delete(size_t offset, size_t len);

    virtual size_t GetLength();

    virtual size_t GetLineCount() {
        return m_Lines.size();
    }

    virtual size_t GetLineData(const LinePosition & line_pos, const wchar_t * & data, size_t len);
    virtual size_t GetLineLength(size_t index);
    virtual size_t GetLineStartOffset(size_t index);

    virtual size_t LinePositionToDocPos(const LinePosition & line_pos);
    virtual LinePosition DocPosToLinePosition(size_t offset);
private:
    using LineVector = std::vector<std::wstring>;

    LineVector m_Lines;

    size_t GetLengthToLine(size_t index);
    size_t GetLineLastPos(size_t index);
};

size_t BufferImpl::GetLineLastPos(size_t index) {
    const auto & line = m_Lines[index];

    if (line.size() == 0)
        return 0;

    auto pos = line.find_last_not_of(L"\r\n");

    return pos == line.npos ? line.size() : pos + 1;
}

size_t BufferImpl::LinePositionToDocPos(const LinePosition & line_pos) {
    size_t line_count = GetLineCount();

    if (line_count == 0)
        return 0;

    size_t last_line = line_pos.line >= line_count ? line_count - 1 : line_pos.line;

    size_t doc_pos = 0;

    for(size_t i=0;i < last_line;i++) {
        doc_pos += m_Lines[i].size();
    }

    return doc_pos + (line_pos.offset >= m_Lines[last_line].size() ? GetLineLastPos(last_line) : line_pos.offset);
}

LinePosition BufferImpl::DocPosToLinePosition(size_t offset) {
    size_t line_count = GetLineCount();

    if (line_count == 0) {
        return {0, 0};
    }

    size_t last_line = line_count;
    size_t doc_pos = 0, last_doc_pos = 0;

    for(size_t i=0;i < line_count; i++) {
        if (offset < doc_pos) {
            last_line = i;
            break;
        }

        last_doc_pos = doc_pos;
        doc_pos += m_Lines[i].size();
    }

    if (last_line == line_count) {
        return {last_line - 1, GetLineLastPos(last_line - 1)};
    }

    return {last_line - 1, offset - last_doc_pos };
}

size_t BufferImpl::GetLengthToLine(size_t index) {
    return LinePositionToDocPos({index, 0});
}

void BufferImpl::Insert(size_t offset, const wchar_t * data, size_t len) {
    auto line_pos = DocPosToLinePosition(offset);

    size_t begin = 0, end = 0;

    LineVector::iterator it = m_Lines.begin() + line_pos.line;
    bool first = true;

    while(end < len) {
        if (data[end] == L'\r' || data[end] == L'\n') {
            if (data[end] == L'\r' && end + 1 < len && data[end + 1] == '\n') {
                end++;
            }

            if (first && it != m_Lines.end()) {
                if (line_pos.offset < it->size()) {
                    LineVector::iterator new_it = m_Lines.insert(it + 1, it->substr(line_pos.offset));
                    *it = it->substr(0, line_pos.offset);
                    it = new_it;
                }

                it->append(&data[begin], end - begin + 1);
            } else {
                it = m_Lines.insert(it, std::wstring(&data[begin], end - begin + 1));
            }

            first = false;
            it++;
            begin = end + 1;
        }

        end++;
    }

    if (begin < end) {
        if (first && it != m_Lines.end()) {
            if (line_pos.offset < it->size()) {
                LineVector::iterator new_it = m_Lines.insert(it + 1, it->substr(line_pos.offset));
                *it = it->substr(0, line_pos.offset);
                it = new_it;
            }

            it->append(&data[begin], end - begin);
        } else {
            it = m_Lines.insert(it, std::wstring(&data[begin], end - begin));
        }
    }

    //check if last line end with \r\n, if so add new empty line without \r\n
    if (it == m_Lines.end())
        it--;

    if (it == m_Lines.end() - 1
        && (it->back() == L'\r' || it->back() == L'\n')) {
        m_Lines.push_back(std::wstring(L""));
    }
}

void BufferImpl::Delete(size_t offset, size_t len) {
    (void)offset;
    (void)len;
}

size_t BufferImpl::GetLength() {
    return GetLengthToLine(GetLineCount());
}

size_t BufferImpl::GetLineData(const LinePosition & line_pos, const wchar_t * & data, size_t len) {
    data = nullptr;

    if (line_pos.line >= GetLineCount()) {
        return 0;
    }

    const auto & line = m_Lines[line_pos.line];

    size_t real_size = line.size();

    if (real_size == 0) {
        data = L"";
    }

    if (line_pos.offset >= real_size)
        return 0;

    real_size -= line_pos.offset;

    data = &line[line_pos.offset];

    return len > 0 && len < real_size ? len : real_size;
}

size_t BufferImpl::GetLineLength(size_t index) {
    if (index >= GetLineCount()) {
        return 0;
    }

    return m_Lines[index].size();
}

size_t BufferImpl::GetLineStartOffset(size_t index) {
    return GetLengthToLine(index);
}

}; // namespace impl

BufferPtr CreateBuffer() {
    return std::make_shared<impl::BufferImpl>();
}

}; // namespace eim
