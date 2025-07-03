#include "include/object.hpp"
#include "_typedef.hpp"
#include "allocator.hpp"
#include <cstring>

namespace mxs_runtime {

    MXObject::MXObject(bool is_static) : _is_static(is_static) { }
    MXObject::~MXObject() {
        if (!_is_static) { MX_ALLOCATOR.unregisterObject(this); }
    }

    MXObject::MXObject(const MXObject &other)
        : ref_cnt(other.ref_cnt), object_type_name(other.object_type_name),
          _is_static(other._is_static) { }

    auto MXObject::increase_ref() -> refer_count_type { return ++ref_cnt; }

    refer_count_type MXObject::decrease_ref() {
        if (ref_cnt > 0) { --ref_cnt; }
        return ref_cnt;
    }

    auto MXObject::get_type_name() const -> const std::string & {
        return object_type_name;
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

    auto MXObject::repr() const -> inner_string { return object_type_name; }


}// namespace mxs_runtime

extern "C" {

mxs_runtime::MXObject *new_mx_object() { return new mxs_runtime::MXObject(); }

void delete_mx_object(mxs_runtime::MXObject *obj) { delete obj; }

mxs_runtime::refer_count_type increase_ref(mxs_runtime::MXObject *obj) {
    if (!obj) return 0;
    return obj->increase_ref();
}

mxs_runtime::refer_count_type decrease_ref(mxs_runtime::MXObject *obj) {
    if (!obj) return 0;
    std::size_t cnt = obj->decrease_ref();
    if (cnt == 0) { delete obj; }
    return cnt;
}

const char *get_object_type_name(mxs_runtime::MXObject *obj) {
    if (!obj) return nullptr;
    return obj->get_type_name().c_str();
}

void set_object_type_name(mxs_runtime::MXObject *obj, const char *name) {
    if (!obj) return;
    obj->set_type_name(name ? std::string(name) : std::string());
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
