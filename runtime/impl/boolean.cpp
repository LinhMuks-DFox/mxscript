#include "include/boolean.hpp"
#include "_typedef.hpp"
#include "macro.hpp"
#include "object.hpp"

namespace mxs_runtime {
    static MXBoolean mx_true_instance{ true };
    static MXBoolean mx_false_instance{ false };

    MXS_API const MXBoolean &MXTRUE = mx_true_instance;
    MXS_API const MXBoolean &MXFALSE = mx_false_instance;

    MXBoolean::MXBoolean() : MXObject(), value(false) {
        this->set_type_name("boolean");
    }

    MXBoolean::MXBoolean(inner_boolean v) : MXObject(), value(v) {
        this->set_type_name("boolean");
    }

    MXBoolean::~MXBoolean() = default;

    inner_boolean MXBoolean::equals(const MXObject &other) {
        const MXBoolean *b = dynamic_cast<const MXBoolean*>(&other);
        return b && b->value == value;
    }

    inner_boolean MXBoolean::equals(const MXObject *other) {
        return other && equals(*other);
    }

    inner_boolean MXBoolean::equals(const MXBoolean &other) {
        return value == other.value;
    }

    inner_boolean MXBoolean::equals(const MXBoolean *other) {
        return other && value == other->value;
    }

}// namespace
