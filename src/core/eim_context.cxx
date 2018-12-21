#include "eim_context.h"

namespace eim {

namespace impl {
class EIMContextImpl : public virtual EIMContext {
public:
    using EIMContext::EIMContext;
    virtual ~EIMContextImpl() = default;

public:
    virtual BufferManagerPtr GetBufferManager() {
        return m_BufferManager;
    }

    virtual CommandManagerPtr GetCommandManager() {
        return m_CommandManager;
    }

    virtual BufferSessionManagerPtr GetSessionManager() {
        return m_SessionManager;
    }

public:
    void Initialize();

private:
    BufferManagerPtr m_BufferManager;
    CommandManagerPtr m_CommandManager;
    BufferSessionManagerPtr m_SessionManager;
};

void EIMContextImpl::Initialize() {
    m_BufferManager = CreateBufferManager();
    m_CommandManager = CreateCommandManager();
    m_SessionManager = CreateBufferSessionManager();
}

};

EIMContextPtr CreateEIMContext() {
    std::shared_ptr<impl::EIMContextImpl> context =
            std::make_shared<impl::EIMContextImpl>();
    context->Initialize();

    return context;
}

}; //namespace eim
