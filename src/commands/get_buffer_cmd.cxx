#include "eim_context.h"
#include "cmd_base.h"
#include "command_register.h"

#include "tao/json.hpp"

#include <locale>
#include <codecvt>

namespace eim
{
namespace cmd {

static
std::wstring_convert<std::codecvt_utf8<wchar_t>, wchar_t> wcharconv;

class GetBufferCommand : public virtual CommandBase<GetBufferCommand> {
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

        BufferPtr buf{};

        std::string err;

        if (buf_name.has_value() && !file_path.has_value()) {
            buf = context->GetBufferManager()->GetBuffer(wcharconv.from_bytes(buf_name->c_str()), create.has_value() ? create.value() : true);
        } else if (file_path.has_value()) {
            buf = context->GetBufferManager()->GetFileBuffer(file_path.value(), create.has_value() ? create.value() : true);
        } else {
            err = "invalid parameter, must have one of name or path.";
        }

        const tao::json::value result = {
            {"buf", wcharconv.to_bytes(buf->GetName())},
            {"result", buf != nullptr},
            {"error", err}
        };
        return tao::json::to_string(result);
    }
};

REG_CMD(GetBufferCommand);

}; //namespace cmd
}; //namespace eim
