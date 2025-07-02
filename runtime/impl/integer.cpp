#include "integer.hpp"
#include "allocator.hpp"

namespace mxs_runtime {

MXInteger::MXInteger(inner_integer v) : MXObject(), value(v) {
    this->set_type_name("integer");
}

} // namespace mxs_runtime

extern "C" {
MXS_API mxs_runtime::MXInteger* MXCreateInteger(mxs_runtime::inner_integer value) {
    auto* obj = new mxs_runtime::MXInteger(value);
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    return obj;
}
}
