#include "include/object.hpp"
#include "_typedef.hpp"
#include "allocator.hpp"
#include <cstring>

namespace mxs_runtime {

    MXObject::MXObject(bool is_static) : _is_static(is_static) {}
    MXObject::~MXObject() {
        if (!_is_static) {
            MX_ALLOCATOR.unregisterObject(this);
        }
    }

    MXObject::MXObject(const MXObject &other)
        : ref_cnt(other.ref_cnt), object_type_name(other.object_type_name), _is_static(other._is_static) {}

    refer_count_type MXObject::increase_ref() { return ++ref_cnt; }

    refer_count_type MXObject::decrease_ref() {
        if (ref_cnt > 0) { --ref_cnt; }
        return ref_cnt;
    }

    const std::string &MXObject::get_type_name() const { return object_type_name; }

    void MXObject::set_type_name(const std::string &name) { object_type_name = name; }

    inner_boolean MXObject::equals(const MXObject &other) { return this == &other; }
    inner_boolean MXObject::equals(const MXObject *other) { return this == other; }
    hash_code_type MXObject::hash_code() { return reinterpret_cast<hash_code_type>(this); }


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

}// extern "C"
