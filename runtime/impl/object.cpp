#include "include/object.h"
#include "_typedef.hpp"
#include "allocator.hpp"
#include "boolean.hpp"
#include "typeinfo.h"
#include <cstddef>
#include <cstring>

namespace mxs_runtime {

    static const MXTypeInfo OBJECT_TYPE_INFO{ "object", nullptr };
    static const MXTypeInfo FFICALLARGV_TYPE_INFO{ "FFICallArgv", nullptr };

    MXObject::MXObject(const MXTypeInfo *info, bool is_static)
        : type_info(info), _is_static(is_static) {
        MX_ALLOCATOR.registerObject(this);
    }

    MXObject::~MXObject() { MX_ALLOCATOR.unregisterObject(this); }


    MXObject::MXObject(const MXObject &other)
        : type_info(other.type_info), _is_static(other._is_static) { }

    auto MXObject::increase_ref() -> refer_count_type { return ++ref_cnt; }

    auto MXObject::decrease_ref() -> refer_count_type {
        if (ref_cnt > 0) { --ref_cnt; }
        return ref_cnt;
    }

    auto MXObject::get_type_name() const -> const char * {
        return type_info->inner_string.c_str();
    }

    auto MXObject::equals(const MXObject &other) -> inner_boolean {
        return this == &other;
    }

    auto MXObject::equals(const MXObject *other) -> inner_boolean {
        return this == other;
    }

    auto MXObject::hash_code() -> hash_code_type {
        return reinterpret_cast<hash_code_type>(this);
    }

    auto MXObject::repr() const -> inner_string { return type_info->inner_string; }
    static const MXTypeInfo g_mxerror_type_info{ "Error", nullptr };
    MXError::MXError() : MXObject(&g_mxerror_type_info, false) { }

    MXFFICallArgv::MXFFICallArgv(std::vector<MXObject *> &&arg_list)
        : MXObject(&FFICALLARGV_TYPE_INFO, false), args(std::move(arg_list)) { }

    MXFFICallArgv::~MXFFICallArgv() {
        for (MXObject *obj : args) {
            if (obj) { ::decrease_ref(obj); }
        }
    }

    auto MXError::repr() const -> inner_string {
        return inner_string("An MXError occurred.");
    }

    auto MXObject::op_add(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '+' not supported.");
    }

    auto MXObject::op_sub(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '-' not supported.");
    }

    auto MXObject::op_mul(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '*' not supported.");
    }

    auto MXObject::op_div(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '/' not supported.");
    }

    auto MXObject::op_eq(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '==' not supported.");
    }

    auto MXObject::op_ne(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '!=' not supported.");
    }

    auto MXObject::op_lt(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '<' not supported.");
    }

    auto MXObject::op_le(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '<=' not supported.");
    }

    auto MXObject::op_gt(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '>' not supported.");
    }

    auto MXObject::op_ge(const MXObject &other) -> MXObject * {
        return new MXError("TypeError: Operator '>=' not supported.");
    }

    auto MXObject::op_is(const MXObject &other) -> MXObject * {
        return this == &other ? const_cast<MXBoolean *>(&MX_TRUE)
                              : const_cast<MXBoolean *>(&MX_FALSE);
    }
}// namespace mxs_runtime

extern "C" {

mxs_runtime::MXObject *new_mx_object() {
    return new mxs_runtime::MXObject(&mxs_runtime::OBJECT_TYPE_INFO);
}

void delete_mx_object(mxs_runtime::MXObject *obj) { delete obj; }

std::size_t increase_ref(mxs_runtime::MXObject *obj) {
    if (!obj) return 0;
    return obj->increase_ref();
}

std::size_t decrease_ref(mxs_runtime::MXObject *obj) {
    if (!obj) return 0;
    std::size_t cnt = obj->decrease_ref();
    if (cnt == 0) { delete obj; }
    return cnt;
}

const char *mxs_get_object_type_name(mxs_runtime::MXObject *obj) {
    if (!obj) return nullptr;
    return obj->get_type_name();
}

std::size_t mx_object_repr_length(mxs_runtime::MXObject *obj) {
    if (!obj) return 0;
    return obj->repr().length();
}

void mx_object_repr(mxs_runtime::MXObject *obj, char *buffer, std::size_t buffer_size) {
    if (!obj || !buffer || buffer_size == 0) return;
    std::string repr = obj->repr();
    std::strncpy(buffer, repr.c_str(), buffer_size - 1);
    buffer[buffer_size - 1] = '\0';
}

MXS_API bool mxs_is_instance(mxs_runtime::MXObject *obj,
                             const mxs_runtime::MXTypeInfo *target_type_info) {
    if (!obj || !target_type_info) return false;
    const mxs_runtime::MXTypeInfo *cur = obj->get_type_info();
    while (cur) {
        if (cur == target_type_info) return true;
        cur = cur->parent;
    }
    return false;
}

MXS_API mxs_runtime::MXObject *MXCreateFFICallArgv(mxs_runtime::MXObject **args,
                                                   std::size_t count) {
    std::vector<mxs_runtime::MXObject *> vec;
    vec.reserve(count);
    for (std::size_t i = 0; i < count; ++i) {
        mxs_runtime::MXObject *obj = args[i];
        if (obj) { increase_ref(obj); }
        vec.push_back(obj);
    }
    auto *obj = new mxs_runtime::MXFFICallArgv(std::move(vec));
    obj->increase_ref();
    return obj;
}

MXS_API void MXFFICallArgv_destructor(mxs_runtime::MXObject *obj) {
    if (!obj) return;
    auto *argv = dynamic_cast<mxs_runtime::MXFFICallArgv *>(obj);
    if (argv) { delete argv; }
}

}// extern "C"
