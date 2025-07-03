#include "include/object.h"
#include "_typedef.hpp"
#include "allocator.hpp"
#include "typeinfo.h"
#include <cstring>

namespace mxs_runtime {

    static MXObject *object_add_stub(MXObject *, MXObject *) { return nullptr; }

    static const MXTypeInfo OBJECT_TYPE_INFO{ "object", nullptr, object_add_stub, nullptr,
                                              nullptr };

    MXObject::MXObject(const MXTypeInfo *info, bool is_static)
        : type_info(info), _is_static(is_static) { }

    MXObject::~MXObject() {
        if (!_is_static) { MX_ALLOCATOR.unregisterObject(this); }
    }

    MXObject::MXObject(const MXObject &other)
        : type_info(other.type_info), _is_static(other._is_static) { }

    auto MXObject::increase_ref() -> refer_count_type { return ++ref_cnt; }

    auto MXObject::decrease_ref() -> refer_count_type {
        if (ref_cnt > 0) { --ref_cnt; }
        return ref_cnt;
    }

    auto MXObject::get_type_name() const -> const char * { return type_info->name; }

    auto MXObject::equals(const MXObject &other) -> inner_boolean {
        return this == &other;
    }

    auto MXObject::equals(const MXObject *other) -> inner_boolean {
        return this == other;
    }

    auto MXObject::hash_code() -> hash_code_type {
        return reinterpret_cast<hash_code_type>(this);
    }

    auto MXObject::repr() const -> inner_string { return type_info->name; }

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

}// extern "C"
