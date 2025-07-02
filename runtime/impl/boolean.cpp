#include "include/boolean.hpp"
#include "_typedef.hpp"
#include "macro.hpp"
#include "object.hpp"

namespace mxs_runtime {
    static MXBoolean mx_true_instance{ true };
    static MXBoolean mx_false_instance{ false };

    MXS_API const MXBoolean &MXTRUE = mx_true_instance;
    MXS_API const MXBoolean &MXFALSE = mx_false_instance;

    MXBoolean::MXBoolean(inner_boolean v) : MXObject(), value(v) {
        this->set_type_name("boolean");
    }

}// namespace
