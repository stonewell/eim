#include "buffer.h"
#include "file_buffer.h"

#include <vector>
#include <functional>
#include <algorithm>
#include <iostream>

namespace eim {
namespace impl {

class BufferImpl : public virtual Buffer {
public:
    BufferImpl() {};
    virtual ~BufferImpl() {}

public:
    virtual std::wstring GetName() {
        return m_Name;
    }

    virtual void SetName(const std::wstring & name) {
        m_Name = name;
    }

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
    virtual void DeleteLine(size_t index) {
        if (index < GetLineCount()) {
            m_Lines.erase(m_Lines.begin() + index);
        }
    }
    virtual void Clear() {
        m_Lines.clear();
    }

private:
    using LineVector = std::vector<std::wstring>;

    LineVector m_Lines;

    size_t GetLengthToLine(size_t index);
    size_t GetLineLastPos(size_t index);

    std::wstring m_Name;
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

    LinePosition line_pos {last_line - 1, offset - last_doc_pos };

    //make sure do not put line offset between '\r\n'.
    if (m_Lines[line_pos.line].size() > 0
        && line_pos.offset > 0
        && m_Lines[line_pos.line][line_pos.offset] == L'\n'
        && m_Lines[line_pos.line][line_pos.offset - 1] == L'\r') {
        line_pos.offset -= 1;
    }

    return line_pos;
}

size_t BufferImpl::GetLengthToLine(size_t index) {
    return LinePositionToDocPos({index, 0});
}

void BufferImpl::Insert(size_t offset, const wchar_t * data, size_t len) {
    auto line_pos = DocPosToLinePosition(offset);

    size_t begin = 0, end = 0;

    LineVector::iterator it = m_Lines.begin() + line_pos.line;
    bool first = true;

    std::function<void(const wchar_t * str, size_t len)> f(
        [this, first, &it, line_pos](const wchar_t * str, size_t len) {
            if (first && it != m_Lines.end()) {
                if (line_pos.offset < it->size()) {
                    LineVector::iterator new_it = m_Lines.insert(it + 1, it->substr(line_pos.offset));
                    *it = it->substr(0, line_pos.offset);
                    it = new_it;
                }

                it->append(str, len);
            } else {
                it = m_Lines.insert(it, std::wstring(str, len));
            }
        });

    while(end < len) {
        if (data[end] == L'\r' || data[end] == L'\n') {
            if (data[end] == L'\r' && end + 1 < len && data[end + 1] == '\n') {
                end++;
            }

            f(&data[begin], end - begin + 1);

            first = false;
            it++;
            begin = end + 1;
        }

        end++;
    }

    if (begin < end) {
        f(&data[begin], end - begin);
    }

    //check if last line end with \r\n, if so add new empty line without \r\n
    if (m_Lines.size() > 0) {
        if (it == m_Lines.end())
            it--;

        if (it == m_Lines.end() - 1
            && (it->back() == L'\r' || it->back() == L'\n')) {
            m_Lines.push_back(std::wstring(L""));
        }
    }
}

void BufferImpl::Delete(size_t offset, size_t len) {
    if (len == 0)
        return;

    auto line_pos = DocPosToLinePosition(offset);

    while(line_pos.line < GetLineCount() && len > 0) {
        size_t avaiable_len = m_Lines[line_pos.line].size() - line_pos.offset;
        size_t line_step = 1;
        size_t new_offset = 0;

        if (avaiable_len > 0) {
            size_t remove_len = std::min(avaiable_len, len);

            m_Lines[line_pos.line].erase(line_pos.offset, remove_len);
            len -= remove_len;

            //clear empty line
            if (m_Lines[line_pos.line].empty()) {
                m_Lines.erase(m_Lines.begin() + line_pos.line);
                line_step = 0;
            } else if (!(m_Lines[line_pos.line].back() == L'\r'
                         || m_Lines[line_pos.line].back() == L'\n')) {
                //merge two lines
                if (line_pos.line < GetLineCount() - 1) {
                    new_offset = m_Lines[line_pos.line].size();

                    m_Lines[line_pos.line].append(m_Lines[line_pos.line + 1]);
                    m_Lines.erase(m_Lines.begin() + line_pos.line + 1);

                    line_step = 0;
                }
            }
        }

        line_pos.line += line_step;
        line_pos.offset = new_offset;
    }
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
