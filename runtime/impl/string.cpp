#include "string.hpp"
#include "allocator.hpp"

namespace mxs_runtime {

    static const RTTI RTTI_STRING{ "String" };

    MXString::MXString(inner_string v)
        : MXObject(&RTTI_STRING, false), value(std::move(v)) { }

    auto MXString::repr() const -> inner_string { return value; }

}// namespace mxs_runtime

extern "C" MXS_API auto MXCreateString(const char *c_str) -> mxs_runtime::MXString * {
    if (!c_str) return nullptr;
    auto *obj = new mxs_runtime::MXString(mxs_runtime::inner_string(c_str));
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    obj->increase_ref();
    return obj;
}
