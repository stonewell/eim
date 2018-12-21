#pragma once

#include "buffer.h"
#include <memory>
#include <forward_list>

namespace eim {
class BufferClient {
};

using BufferClientPtr = std::shared_ptr<BufferClient>;
using BufferClientList = std::forward_list<BufferClientPtr>;
}; //namespace eim
