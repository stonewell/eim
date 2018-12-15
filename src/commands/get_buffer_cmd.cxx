#include "eim_context.h"
#include "cmd_base.h"

#include "tao/json.hpp"

namespace eim
{
class GetBufferCommand : public virtual CommandBase {
public:
    GetBufferCommand()
        : CommandBase("get_buffer") {
    }

    virtual ~GetBufferCommand() = default;

public:
    virtual std::string Execute(EIMContextPtr context, const std::string & json_args) {
        const tao::json::value v = tao::json::from_string(json_args);

        auto buf_name = v.optional<std::string>("name");
        auto file_path = v.optional<std::string>("path");
        auto create = v.optional<bool>("create");

        context->GetBufferManager()->GetBuffer(L"", create.has_value() ? create.value() : true);

        return json_args;
    }
};
}; //namespace eim
