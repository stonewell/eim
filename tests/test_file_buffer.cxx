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

    std::wcout << "---------------------------" << std::endl << std::endl;
}

int main() {
    eim::FileBufferPtr pBuffer = eim::CreateFileBuffer();

    pBuffer->LoadFromFile("/home/stone/test.c");

    print_lines(pBuffer);

    pBuffer->SaveToFile("test_new.c");

    return pBuffer == nullptr ? 1 : 0;
}
