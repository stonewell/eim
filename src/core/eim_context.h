#pragma once

#include "buffer_manager.h"
#include "command_manager.h"
#include "buffer_session.h"

namespace eim {
class EIMContext {
public:
    EIMContext() = default;
    virtual ~EIMContext() = default;

public:
    virtual BufferManagerPtr GetBufferManager() = 0;
    virtual CommandManagerPtr GetCommandManager() = 0;
    virtual BufferSessionVector GetBufferSessions() = 0;
};

}; //namespace eim
