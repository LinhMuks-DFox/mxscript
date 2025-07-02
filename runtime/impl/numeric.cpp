#include "numeric.hpp"
#include "allocator.hpp"

namespace mxs_runtime {

MXNumeric::MXNumeric(bool is_static) : MXObject(is_static) {
    this->set_type_name("numeric");
}

MXInteger::MXInteger(inner_integer v) : MXNumeric(false), value(v) {
    this->set_type_name("integer");
}

MXFloat::MXFloat(inner_float v) : MXNumeric(false), value(v) {
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

