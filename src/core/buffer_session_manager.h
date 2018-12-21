#pragma once

#include "buffer_session.h"
#include "buffer_client.h"
#include <memory>

namespace eim {
class BufferSessionManager {
public:
    BufferSessionManager() = default;
    virtual ~BufferSessionManager() = default;

public:
    virtual BufferSessionPtr CreateSession(BufferPtr buf, BufferClientPtr client) = 0;
    virtual void DestroySession(BufferPtr buf, BufferClientPtr client) = 0;
};

}; //namespace eim
