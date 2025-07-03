#include "string.hpp"
#include "allocator.hpp"
#include "typeinfo.h"

namespace mxs_runtime {

    static MXObject *string_add_stub(MXObject *, MXObject *) { return nullptr; }
    static const MXTypeInfo STRING_TYPE_INFO{ "String", nullptr, string_add_stub, nullptr,
                                              nullptr };

    MXString::MXString(inner_string v)
        : MXObject(&STRING_TYPE_INFO, false), value(std::move(v)) { }

    auto MXString::repr() const -> inner_string { return value; }

}// namespace mxs_runtime

extern "C" MXS_API auto MXCreateString(const char *c_str) -> mxs_runtime::MXString * {
    if (!c_str) return nullptr;
    auto *obj = new mxs_runtime::MXString(mxs_runtime::inner_string(c_str));
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    obj->increase_ref();
    return obj;
}
