#include "numeric.hpp"
#include "allocator.hpp"
#include "typeinfo.h"
#include <format>

namespace mxs_runtime {


    static const MXTypeInfo g_integer_type_info{ "Integer", nullptr };

    static const MXTypeInfo g_float_type_info{ "Float", nullptr };

    MXNumeric::MXNumeric(const MXTypeInfo *info, bool is_static)
        : MXObject(info, is_static) { }

    MXInteger::MXInteger(inner_integer v)
        : MXNumeric(&g_integer_type_info, false), value(v) { }

    auto MXInteger::to_string() const -> inner_string { return std::format("{}", value); }
    MXFloat::MXFloat(inner_float v) : MXNumeric(&g_float_type_info, false), value(v) { }

    auto MXFloat::to_string() const -> inner_string { return std::format("{}", value); }

    auto MXInteger::op_add(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            auto &r = static_cast<const MXInteger &>(other);
            return MXCreateInteger(value + r.value);
        }
        return MXObject::op_add(other);
    }

    auto MXInteger::op_sub(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            auto &r = static_cast<const MXInteger &>(other);
            return MXCreateInteger(value - r.value);
        }
        return MXObject::op_sub(other);
    }

    auto MXInteger::op_eq(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            auto &r = static_cast<const MXInteger &>(other);
            return r.value == value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return MXObject::op_eq(other);
    }

    auto MXFloat::op_add(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(value + r.value);
        }
        return MXObject::op_add(other);
    }

    auto MXFloat::op_sub(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(value - r.value);
        }
        return MXObject::op_sub(other);
    }

    auto MXFloat::op_eq(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            auto &r = static_cast<const MXFloat &>(other);
            return r.value == value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return MXObject::op_eq(other);
    }

    MXObject *integer_add_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return MXCreateInteger(l->value + r->value);
    }

    MXObject *integer_sub_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return MXCreateInteger(l->value - r->value);
    }

    MXObject *integer_add(MXObject *self, MXObject *other) {
        if (other->get_type_info() == &g_integer_type_info) {
            return integer_add_integer(self, other);
        }
        return nullptr;
    }

    MXObject *integer_sub(MXObject *self, MXObject *other) {
        if (other->get_type_info() == &g_integer_type_info) {
            return integer_sub_integer(self, other);
        }
        return nullptr;
    }
}// namespace mxs_runtime

#ifdef __cplusplus
extern "C" {
#endif
MXS_API mxs_runtime::MXObject *integer_add_integer(mxs_runtime::MXObject *left,
                                                   mxs_runtime::MXObject *right) {
    return mxs_runtime::integer_add_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_sub_integer(mxs_runtime::MXObject *left,
                                                   mxs_runtime::MXObject *right) {
    return mxs_runtime::integer_sub_integer(left, right);
}

MXS_API mxs_runtime::MXObject *mxs_op_add(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left) return new mxs_runtime::MXError();
    return left->op_add(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_sub(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left) return new mxs_runtime::MXError();
    return left->op_sub(*right);
}

MXS_API mxs_runtime::inner_integer mxs_get_integer_value(mxs_runtime::MXObject *obj) {
    auto *i = static_cast<mxs_runtime::MXInteger *>(obj);
    return i->value;
}

auto MXCreateInteger(mxs_runtime::inner_integer value) -> mxs_runtime::MXInteger * {
    auto *obj = new mxs_runtime::MXInteger(value);
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    return obj;
}

auto MXCreateFloat(mxs_runtime::inner_float value) -> mxs_runtime::MXFloat * {
    auto *obj = new mxs_runtime::MXFloat(value);
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    return obj;
}
#ifdef __cplusplus
}// extern "C"
#endif