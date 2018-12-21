#include "buffer_session_manager.h"

#include <unordered_map>
#include <algorithm>

namespace eim {

namespace impl {
class BufferSessionManagerImpl : public virtual BufferSessionManager {
public:
    BufferSessionManagerImpl() = default;
    virtual ~BufferSessionManagerImpl() = default;

public:
    virtual BufferSessionPtr CreateSession(BufferPtr buf, BufferClientPtr client);
    virtual void DestroySession(BufferPtr buf, BufferClientPtr client);

private:
    using SessionMap = std::unordered_map<std::wstring, BufferSessionPtr>;

    SessionMap m_SessionMap;
};

BufferSessionPtr BufferSessionManagerImpl::CreateSession(BufferPtr buf, BufferClientPtr client) {
    auto it = m_SessionMap.insert(std::make_pair(buf->GetName(), std::make_shared<BufferSession>()));

    BufferSessionPtr & session = it.first->second;

    auto find_client = std::find(session->clients.begin(), session->clients.end(), client);

    if (find_client == session->clients.end()) {
        session->clients.push_front(client);
    }

    return session;
}

void BufferSessionManagerImpl::DestroySession(BufferPtr buf, BufferClientPtr client) {
    auto it = m_SessionMap.find(buf->GetName());

    if (it == m_SessionMap.end())
        return;

    BufferSessionPtr & session = it->second;

    session->clients.remove(client);
}

}; //namespace impl

BufferSessionManagerPtr CreateBufferSessionManager() {
    return std::make_shared<impl::BufferSessionManagerImpl>();
}

}; //namespace eim
