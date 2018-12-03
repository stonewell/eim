#include <stdio.h>
#include <iostream>
#include "file_buffer.h"

static
void print_lines(const eim::BufferPtr & buf) {
    size_t line_count = buf->GetLineCount();

    for(size_t i=0;i < line_count; i++) {
        const wchar_t * data = nullptr;
        size_t rsize = buf->GetLineData({i, 0}, data);

        std::wcout << i << ":" << rsize << "[" << data << "]" << std::endl;
    }
}

int main() {
    eim::FileBuffer * pBuffer = nullptr;
    eim::BufferPtr buf = eim::CreateBuffer();

    std::wstring a(L"abc\rdef\nghi\r\n");

    buf->Insert(0, a.c_str(), a.size());

    print_lines(buf);

    buf->Insert(buf->GetLength(), L"IIII", 4);
    buf->Insert(buf->GetLength(), L"GGGGG\n", 6);

    print_lines(buf);

    buf->Insert(buf->GetLength(), L"KKKK", 4);
    print_lines(buf);
    return pBuffer == nullptr ? 0 : 1;
}
