#include "string.hpp"
#include "allocator.hpp"
#include "numeric.hpp"
#include "typeinfo.h"

namespace mxs_runtime {

    static const MXTypeInfo STRING_TYPE_INFO{ "String", nullptr };

    MXString::MXString(inner_string v)
        : MXObject(&STRING_TYPE_INFO, false), value(std::move(v)) { }

    auto MXString::repr() const -> inner_string { return value; }

}// namespace mxs_runtime

extern "C" MXS_API auto MXCreateString(const char *c_str) -> mxs_runtime::MXString * {
    if (!c_str) return nullptr;
    auto *obj = new mxs_runtime::MXString(mxs_runtime::inner_string(c_str));
    obj->increase_ref();
    return obj;
}

extern "C" MXS_API auto mxs_string_from_integer(mxs_runtime::MXObject *integer_obj)
        -> mxs_runtime::MXObject * {
    using namespace mxs_runtime;
    if (!integer_obj || integer_obj->type_info != &g_integer_type_info) {
        return new MXError("TypeError", "Argument must be an Integer.");
    }
    auto val = static_cast<MXInteger *>(integer_obj)->value;
    auto str = std::to_string(val);
    return mxs_runtime::MXCreateString(str.c_str());
}
