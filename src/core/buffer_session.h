#pragma once

#include "buffer.h"
#include "command.h"
#include <memory>
#include <vector>

namespace eim {
struct BufferSession {
    BufferPtr buf;
    CommandStack cmds;
};

using BufferSessionPtr = std::shared_ptr<BufferSession>;
using BufferSessionVector = std::vector<BufferSessionPtr>;
}; //namespace eim
