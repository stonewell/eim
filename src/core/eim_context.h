#pragma once

#include "eim_core.h"
#include "buffer_manager.h"
#include "command_manager.h"
#include "buffer_session.h"
#include "buffer_session_manager.h"

namespace eim {
class EIMContext : public virtual BufferSessionManager {
public:
    EIMContext() = default;
    virtual ~EIMContext() = default;

public:
    virtual BufferManagerPtr GetBufferManager() = 0;
    virtual CommandManagerPtr GetCommandManager() = 0;
};

EIMContextPtr CreateEIMContext();
}; //namespace eim
