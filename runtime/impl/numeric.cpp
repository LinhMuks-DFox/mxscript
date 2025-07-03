#include "numeric.hpp"
#include "allocator.hpp"
#include <format>

namespace mxs_runtime {

static const RTTI RTTI_INTEGER{"Integer"};
static const RTTI RTTI_FLOAT{"Float"};

MXNumeric::MXNumeric(const RTTI* rtti, bool is_static) : MXObject(rtti, is_static) {}

MXInteger::MXInteger(inner_integer v) : MXNumeric(&RTTI_INTEGER, false), value(v) {}

auto MXInteger::to_string() const -> inner_string {
    return std::format("{}", value);
}
MXFloat::MXFloat(inner_float v) : MXNumeric(&RTTI_FLOAT, false), value(v) {}

auto MXFloat::to_string() const -> inner_string {
    return std::format("{}", value);
}
} // namespace mxs_runtime

extern "C" {

auto MXCreateInteger(mxs_runtime::inner_integer value) -> mxs_runtime::MXInteger* {
    auto* obj = new mxs_runtime::MXInteger(value);
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    return obj;
}

auto MXCreateFloat(mxs_runtime::inner_float value) -> mxs_runtime::MXFloat* {
    auto* obj = new mxs_runtime::MXFloat(value);
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    return obj;
}

} // extern "C"

