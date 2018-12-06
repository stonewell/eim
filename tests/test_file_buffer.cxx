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

int main(int argc, char ** argv) {
    if (argc < 2) {
        std::wcout << L"usage: test_file_buffer <file>" << std::endl;
        return 1;
    }

    std::wcout << "loading... " << argv[1] << std::endl;
    eim::FileBufferPtr pBuffer = eim::CreateFileBuffer();

    if (!pBuffer->LoadFromFile(argv[1]))
        return 2;

    print_lines(pBuffer);

    if (!pBuffer->SaveToFile("test_new.c"))
        return 3;

    return pBuffer == nullptr ? 1 : 0;
}
