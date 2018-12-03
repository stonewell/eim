#pragma once

#include "buffer.h"
#include <memory>
#include <vector>

namespace eim {
class BufferClient {
};

using BufferClientPtr = std::shared_ptr<BufferClient>;
using BufferClientVector = std::vector<BufferClientPtr>;
}; //namespace eim
