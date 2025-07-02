#include "numeric.hpp"
#include "allocator.hpp"

namespace mxs_runtime {

MXInteger::MXInteger(inner_integer v) : MXObject(), value(v) {
    this->set_type_name("integer");
}

MXFloat::MXFloat(inner_float v) : MXObject(), value(v) {
    this->set_type_name("float");
}
} // namespace mxs_runtime

extern "C" {

MXS_API mxs_runtime::MXInteger* MXCreateInteger(mxs_runtime::inner_integer value) {
    auto* obj = new mxs_runtime::MXInteger(value);
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    return obj;
}

MXS_API mxs_runtime::MXFloat* MXCreateFloat(mxs_runtime::inner_float value) {
    auto* obj = new mxs_runtime::MXFloat(value);
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    return obj;
}

} // extern "C"

