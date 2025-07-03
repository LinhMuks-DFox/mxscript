#include "boolean.hpp"
#include "_typedef.hpp"

namespace mxs_runtime {

    static const RTTI RTTI_BOOLEAN{"Boolean"};
    static MXBoolean true_instance{ true };
    static MXBoolean false_instance{ false };

    MXS_API const MXBoolean &MX_TRUE = true_instance;
    MXS_API const MXBoolean &MX_FALSE = false_instance;

    MXBoolean::MXBoolean(inner_boolean v)
        : MXObject(&RTTI_BOOLEAN, true), value(v) {}

    auto MXBoolean::repr() const -> inner_string { return value ? "true" : "false"; }

}// namespace mxs_runtime

extern "C" {

auto mxs_get_true() -> const mxs_runtime::MXBoolean* {
    return &mxs_runtime::MX_TRUE;
}
auto mxs_get_false() -> const mxs_runtime::MXBoolean* {
    return &mxs_runtime::MX_FALSE;
}

}// extern "C"
