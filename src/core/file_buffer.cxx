#include "file_buffer.h"

#include <stdio.h>
#include <fstream>
#include <locale>
#include <codecvt>
#include <iostream>

namespace eim {
namespace impl {
class FileBufferImpl : public virtual FileBuffer {
public:
    FileBufferImpl(const std::string & file_path, BufferPtr buf);
    virtual ~FileBufferImpl() = default;

public:
    virtual bool LoadFromFile(const std::string & file_path);
    virtual bool SaveToFile(const std::string & file_path);
    virtual bool Save() {
        if (m_FilePath.empty()) return false;

        return SaveToFile(m_FilePath);
    }
    virtual bool Load() {
        if (m_FilePath.empty()) return false;

        return LoadFromFile(m_FilePath);
    }

    virtual const std::string & GetFilePath() const {
        return m_FilePath;
    }

public:
    virtual std::wstring GetName() {
        return m_Buf->GetName();
    }

    virtual void SetName(const std::wstring & name) {
        m_Buf->SetName(name);
    }

    virtual void Insert(size_t offset, const wchar_t * data, size_t len) {
        m_Buf->Insert(offset, data, len);
    }

    virtual void Delete(size_t offset, size_t len) {
        m_Buf->Delete(offset, len);
    }

    virtual void DeleteLine(size_t index) {
        m_Buf->DeleteLine(index);
    }
    virtual void Clear() {
        m_Buf->Clear();
    }

    virtual size_t GetLength() {
        return m_Buf->GetLength();
    }

    virtual size_t GetLineCount() {
        return m_Buf->GetLineCount();
    }

    virtual size_t GetLineData(const LinePosition & line_pos, const wchar_t * & data, size_t len) {
        return m_Buf->GetLineData(line_pos, data, len);
    }

    virtual size_t GetLineLength(size_t index) {
        return m_Buf->GetLineLength(index);
    }

    virtual size_t GetLineStartOffset(size_t index) {
        return m_Buf->GetLineStartOffset(index);
    }

    virtual size_t LinePositionToDocPos(const LinePosition & line_pos) {
        return m_Buf->LinePositionToDocPos(line_pos);
    }

    virtual LinePosition DocPosToLinePosition(size_t offset) {
        return m_Buf->DocPosToLinePosition(offset);
    }
private:
    std::string m_FilePath;
    BufferPtr m_Buf;
};

FileBufferImpl::FileBufferImpl(const std::string & file_path, BufferPtr buf)
    : m_FilePath {file_path}
    , m_Buf {buf ? buf : CreateBuffer()}
{
    if (!buf && !m_FilePath.empty())
        Load();
}

bool FileBufferImpl::LoadFromFile(const std::string & file_path) {
    std::locale old_locale;
    std::locale utf8_locale(old_locale,new std::codecvt_utf8<wchar_t>);

    std::wifstream fis(file_path);
    if (fis.fail()) return false;

    fis.imbue(utf8_locale);

    wchar_t buf[4096];

    auto read_count = fis.readsome(buf, 4096);

    while(fis.good()) {
        if (read_count > 0) {
            m_Buf->Insert(m_Buf->GetLength(), buf, read_count);
        } else {
            fis.read(buf, 1);

            if (fis.eof())
                break;

            m_Buf->Insert(m_Buf->GetLength(), buf, 1);
        }

        read_count = fis.readsome(buf, 4096);
    }

    m_FilePath = file_path;

    return true;
}

bool FileBufferImpl::SaveToFile(const std::string & file_path) {
    std::locale old_locale;
    std::locale utf8_locale(old_locale,new std::codecvt_utf8<wchar_t>);

    std::wofstream fos(file_path);
    if (fos.fail()) return false;

    fos.imbue(utf8_locale);

    size_t line_count = m_Buf->GetLineCount();

    for(size_t i=0;i < line_count; i++) {
        const wchar_t * data = nullptr;
        size_t rsize = m_Buf->GetLineData({i, 0}, data);

        fos.write(data, rsize);
    }

    m_FilePath = file_path;
    return true;
}

}; //namespace impl

FileBufferPtr CreateFileBuffer(const std::string & file_path, BufferPtr buf) {
    return std::make_shared<impl::FileBufferImpl>(file_path, buf);
}

FileBufferPtr CreateFileBuffer(const std::string & file_path) {
    return CreateFileBuffer(file_path, BufferPtr {} );
}

FileBufferPtr CreateFileBuffer(BufferPtr buf) {
    return CreateFileBuffer("", buf);
}

FileBufferPtr CreateFileBuffer() {
    return CreateFileBuffer("", BufferPtr {});
}

}; //namespace eim
