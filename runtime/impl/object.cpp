#include "include/object.hpp"
#include <cstring>

namespace mxs_runtime {

MXObject::MXObject() = default;
MXObject::~MXObject() = default;

MXObject::MXObject(const MXObject &other)
    : ref_cnt(other.ref_cnt), object_type_name(other.object_type_name) {}

std::size_t MXObject::increase_ref() { return ++ref_cnt; }

std::size_t MXObject::decrease_ref() {
    if (ref_cnt > 0) {
        --ref_cnt;
    }
    return ref_cnt;
}

const std::string &MXObject::get_type_name() const { return object_type_name; }

void MXObject::set_type_name(const std::string &name) { object_type_name = name; }

} // namespace mxs_runtime

extern "C" {

mxs_runtime::MXObject *new_mx_object() { return new mxs_runtime::MXObject(); }

void delete_mx_object(mxs_runtime::MXObject *obj) { delete obj; }

std::size_t increase_ref(mxs_runtime::MXObject *obj) {
    if (!obj)
        return 0;
    return obj->increase_ref();
}

std::size_t decrease_ref(mxs_runtime::MXObject *obj) {
    if (!obj)
        return 0;
    std::size_t cnt = obj->decrease_ref();
    if (cnt == 0) {
        delete obj;
    }
    return cnt;
}

const char *get_object_type_name(mxs_runtime::MXObject *obj) {
    if (!obj)
        return nullptr;
    return obj->get_type_name().c_str();
}

void set_object_type_name(mxs_runtime::MXObject *obj, const char *name) {
    if (!obj)
        return;
    obj->set_type_name(name ? std::string(name) : std::string());
}

} // extern "C"
