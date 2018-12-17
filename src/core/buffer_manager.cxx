#include "buffer_manager.h"

#include <unordered_map>

namespace eim {
namespace impl {
class BufferManagerImpl : public virtual BufferManager {
public:
    using BufferManager::BufferManager;
    virtual ~BufferManagerImpl() = default;

public:
    virtual BufferPtr GetBuffer(std::wstring name, bool create = true);
    virtual FileBufferPtr GetFileBuffer(std::string file_path, bool create = true);

private:
    BufferVector m_Buffers;

    using BufferNameMapping = std::unordered_map<std::wstring, BufferPtr>;
    using BufferPathMapping = std::unordered_map<std::string, FileBufferPtr>;

    BufferNameMapping m_BufferNameMap;
    BufferPathMapping m_BufferPathMap;
};

BufferPtr BufferManagerImpl::GetBuffer(std::wstring name, bool create) {
    auto it = m_BufferNameMap.find(name);

    if (it != m_BufferNameMap.end()) {
        return it->second;
    }

    if (create) {
        auto buf = CreateBuffer();
        buf->SetName(name);

        m_BufferNameMap.emplace(name, buf);
        m_Buffers.push_back(buf);

        return buf;
    }

    return BufferPtr{};
}

FileBufferPtr BufferManagerImpl::GetFileBuffer(std::string file_path, bool create) {
    auto it = m_BufferPathMap.find(file_path);

    if (it != m_BufferPathMap.end()) {
        return it->second;
    }

    if (create) {
        auto buf = CreateFileBuffer(file_path);

        m_BufferNameMap.emplace(buf->GetName(), buf);
        m_BufferPathMap.emplace(file_path, buf);
        m_Buffers.push_back(buf);

        return buf;
    }

    return FileBufferPtr{};
}

}; //namespace impl

BufferManagerPtr CreateBufferManager() {
    return std::make_shared<impl::BufferManagerImpl>();
}

}; //namespace eim
