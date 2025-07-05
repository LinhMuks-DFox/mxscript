#include "numeric.hpp"
#include "allocator.hpp"
#include "typeinfo.h"
#include <format>
#include <string>

namespace mxs_runtime {


    static const MXTypeInfo g_numeric_type_info{ "Numeric", nullptr };
    MXS_API const MXTypeInfo g_integer_type_info{ "Integer", &g_numeric_type_info };
    static const MXTypeInfo g_float_type_info{ "Float", &g_numeric_type_info };

    MXNumeric::MXNumeric(const MXTypeInfo *info, bool is_static)
        : MXObject(info, is_static) { }

    MXInteger::MXInteger(inner_integer v)
        : MXNumeric(&g_integer_type_info, false), value(v) { }

    auto MXInteger::to_string() const -> inner_string { return std::format("{}", value); }

    MXFloat::MXFloat(inner_float v) : MXNumeric(&g_float_type_info, false), value(v) { }

    auto MXFloat::to_string() const -> inner_string { return std::format("{}", value); }

    auto MXInteger::op_add(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateInteger(value + r.value);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(static_cast<inner_float>(value) + r.value);
        }
        return new MXError("TypeError: unsupported '+' operands");
    }

    auto MXInteger::op_sub(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateInteger(value - r.value);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(static_cast<inner_float>(value) - r.value);
        }
        return new MXError("TypeError: unsupported '-' operands");
    }

    auto MXInteger::op_mul(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateInteger(value * r.value);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(static_cast<inner_float>(value) * r.value);
        }
        return new MXError("TypeError: unsupported '*' operands");
    }

    auto MXInteger::op_div(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            if (r.value == 0) return new MXError("ZeroDivisionError");
            return MXCreateInteger(value / r.value);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            if (r.value == 0.0) return new MXError("ZeroDivisionError");
            return MXCreateFloat(static_cast<inner_float>(value) / r.value);
        }
        return new MXError("TypeError: unsupported '/' operands");
    }

    auto MXInteger::op_eq(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return r.value == value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) == r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '==' operands");
    }

    auto MXInteger::op_ne(const MXObject &other) -> MXObject * {
        auto *res = op_eq(other);
        if (auto *b = dynamic_cast<MXBoolean *>(res)) {
            return b->value ? const_cast<MXBoolean *>(&MX_FALSE)
                            : const_cast<MXBoolean *>(&MX_TRUE);
        }
        return res;
    }

    auto MXInteger::op_lt(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value < r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) < r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '<' operands");
    }

    auto MXInteger::op_le(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value <= r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) <= r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '<=' operands");
    }

    auto MXInteger::op_gt(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value > r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) > r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '>' operands");
    }

    auto MXInteger::op_ge(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value >= r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) >= r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '>=' operands");
    }

    auto MXInteger::op_is(const MXObject &other) -> MXObject * {
        return MXObject::op_is(other);
    }

    auto MXFloat::op_add(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(value + r.value);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateFloat(value + static_cast<inner_float>(r.value));
        }
        return new MXError("TypeError: unsupported '+' operands");
    }

    auto MXFloat::op_sub(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(value - r.value);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateFloat(value - static_cast<inner_float>(r.value));
        }
        return new MXError("TypeError: unsupported '-' operands");
    }

    auto MXFloat::op_mul(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(value * r.value);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateFloat(value * static_cast<inner_float>(r.value));
        }
        return new MXError("TypeError: unsupported '*' operands");
    }

    auto MXFloat::op_div(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            if (r.value == 0.0) return new MXError("ZeroDivisionError");
            return MXCreateFloat(value / r.value);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            if (r.value == 0) return new MXError("ZeroDivisionError");
            return MXCreateFloat(value / static_cast<inner_float>(r.value));
        }
        return new MXError("TypeError: unsupported '/' operands");
    }

    auto MXFloat::op_eq(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return r.value == value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value == static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '==' operands");
    }

    auto MXFloat::op_ne(const MXObject &other) -> MXObject * {
        auto *res = op_eq(other);
        if (auto *b = dynamic_cast<MXBoolean *>(res)) {
            return b->value ? const_cast<MXBoolean *>(&MX_FALSE)
                            : const_cast<MXBoolean *>(&MX_TRUE);
        }
        return res;
    }

    auto MXFloat::op_lt(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return value < r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value < static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '<' operands");
    }

    auto MXFloat::op_le(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return value <= r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value <= static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '<=' operands");
    }

    auto MXFloat::op_gt(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return value > r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value > static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '>' operands");
    }

    auto MXFloat::op_ge(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return value >= r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value >= static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '>=' operands");
    }

    auto MXFloat::op_is(const MXObject &other) -> MXObject * {
        return MXObject::op_is(other);
    }

}// namespace mxs_runtime

#ifdef __cplusplus
extern "C" {
#endif

MXS_API mxs_runtime::MXObject *mxs_op_add(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_add(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_sub(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_sub(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_mul(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_mul(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_div(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_div(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_eq(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_eq(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_ne(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_ne(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_lt(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_lt(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_le(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_le(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_gt(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_gt(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_ge(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_ge(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_is(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_is(*right);
}


MXS_API mxs_runtime::MXObject *mxs_int_absolute(mxs_runtime::MXObject *integer_obj) {
    using namespace mxs_runtime;
    if (!integer_obj || integer_obj->type_info != &g_integer_type_info) {
        return new MXError("TypeError", "Argument must be an Integer.");
    }
    auto val = static_cast<MXInteger *>(integer_obj)->value;
    if (val < 0) val = -val;
    return MXCreateInteger(val);
}

auto MXCreateInteger(mxs_runtime::inner_integer value) -> mxs_runtime::MXInteger * {
    auto *obj = new mxs_runtime::MXInteger(value);
    return obj;
}

auto MXCreateFloat(mxs_runtime::inner_float value) -> mxs_runtime::MXFloat * {
    auto *obj = new mxs_runtime::MXFloat(value);
    return obj;
}
#ifdef __cplusplus
}// extern "C"
#endif