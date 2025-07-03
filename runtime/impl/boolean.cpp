#include "boolean.hpp"
#include "typeinfo.h"
#include "_typedef.hpp"

namespace mxs_runtime {

    static MXObject* bool_add_stub(MXObject*, MXObject*) { return nullptr; }
    static const MXTypeInfo BOOLEAN_TYPE_INFO{ "Boolean", nullptr, bool_add_stub, nullptr, nullptr };
    static MXBoolean true_instance{ true };
    static MXBoolean false_instance{ false };

    MXS_API const MXBoolean &MX_TRUE = true_instance;
    MXS_API const MXBoolean &MX_FALSE = false_instance;

    MXBoolean::MXBoolean(inner_boolean v) : MXObject(&BOOLEAN_TYPE_INFO, true), value(v) { }

    auto MXBoolean::repr() const -> inner_string { return value ? "true" : "false"; }

}// namespace mxs_runtime

extern "C" {

auto mxs_get_true() -> const mxs_runtime::MXBoolean * { return &mxs_runtime::MX_TRUE; }
auto mxs_get_false() -> const mxs_runtime::MXBoolean * { return &mxs_runtime::MX_FALSE; }

}// extern "C"
