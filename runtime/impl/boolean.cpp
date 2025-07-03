#include "boolean.hpp"
#include "_typedef.hpp"

namespace mxs_runtime {

    static MXBoolean true_instance{ true };
    static MXBoolean false_instance{ false };

    MXS_API const MXBoolean &MX_TRUE = true_instance;
    MXS_API const MXBoolean &MX_FALSE = false_instance;

    MXBoolean::MXBoolean(inner_boolean v) : MXObject(true), value(v) {
        this->set_type_name("boolean");
    }

    auto MXBoolean::repr() const -> inner_string { return value ? "true" : "false"; }

}// namespace mxs_runtime

extern "C" {

const mxs_runtime::MXBoolean *mxs_get_true() { return &mxs_runtime::MX_TRUE; }
const mxs_runtime::MXBoolean *mxs_get_false() { return &mxs_runtime::MX_FALSE; }

}// extern "C"
