#include "eim_context.h"

#include <unordered_map>
#include <algorithm>


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

public:
    void Initialize();

    virtual BufferSessionPtr CreateSession(BufferPtr buf, BufferClientPtr client);
    virtual void DestroySession(BufferPtr buf, BufferClientPtr client);

private:
    using SessionMap = std::unordered_map<std::wstring, BufferSessionPtr>;

    SessionMap m_SessionMap;
    BufferManagerPtr m_BufferManager;
    CommandManagerPtr m_CommandManager;
};

void EIMContextImpl::Initialize() {
    m_BufferManager = CreateBufferManager();
    m_CommandManager = CreateCommandManager();
}

BufferSessionPtr EIMContextImpl::CreateSession(BufferPtr buf, BufferClientPtr client) {
    auto it = m_SessionMap.insert(std::make_pair(buf->GetName(), std::make_shared<BufferSession>()));

    BufferSessionPtr & session = it.first->second;

    auto find_client = std::find(session->clients.begin(), session->clients.end(), client);

    if (find_client == session->clients.end()) {
        session->clients.push_front(client);
    }

    return session;
}

void EIMContextImpl::DestroySession(BufferPtr buf, BufferClientPtr client) {
    auto it = m_SessionMap.find(buf->GetName());

    if (it == m_SessionMap.end())
        return;

    BufferSessionPtr & session = it->second;

    session->clients.remove(client);
}
};

EIMContextPtr CreateEIMContext() {
    std::shared_ptr<impl::EIMContextImpl> context =
            std::make_shared<impl::EIMContextImpl>();
    context->Initialize();

    return context;
}

}; //namespace eim
