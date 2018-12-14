#include "eim_context.h"
#include "cmd_base.h"

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
        context->GetBufferManager()->GetBuffer(L"", true);

        return json_args;
    }
};
}; //namespace eim
