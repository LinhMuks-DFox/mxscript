#include "include/object.hpp"
#include "_typedef.hpp"
#include "allocator.hpp"
#include <cstring>

namespace mxs_runtime {

    static const RTTI RTTI_OBJECT{ "object" };

    MXObject::MXObject(const RTTI *rtti_ptr, bool is_static)
        : rtti(rtti_ptr), _is_static(is_static) { }
    MXObject::~MXObject() {
        if (!_is_static) { MX_ALLOCATOR.unregisterObject(this); }
    }

    MXObject::MXObject(const MXObject &other)
        : rtti(other.rtti), _is_static(other._is_static) { }

    auto MXObject::increase_ref() -> refer_count_type { return ++ref_cnt; }

    auto MXObject::decrease_ref() -> refer_count_type {
        if (ref_cnt > 0) { --ref_cnt; }
        return ref_cnt;
    }

    auto MXObject::get_type_name() const -> const std::string & {
        return rtti->type_name;
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

    auto MXObject::repr() const -> inner_string { return rtti->type_name; }


}// namespace mxs_runtime

extern "C" {

auto new_mx_object() -> mxs_runtime::MXObject * {
    return new mxs_runtime::MXObject(&mxs_runtime::RTTI_OBJECT);
}

auto delete_mx_object(mxs_runtime::MXObject *obj) -> void { delete obj; }

auto increase_ref(mxs_runtime::MXObject *obj) -> mxs_runtime::refer_count_type {
    if (!obj) return 0;
    return obj->increase_ref();
}

auto decrease_ref(mxs_runtime::MXObject *obj) -> mxs_runtime::refer_count_type {
    if (!obj) return 0;
    std::size_t cnt = obj->decrease_ref();
    if (cnt == 0) { delete obj; }
    return cnt;
}

auto mxs_get_object_type_name(mxs_runtime::MXObject *obj) -> const char * {
    if (!obj) return nullptr;
    return obj->get_type_name().c_str();
}

auto mx_object_repr_length(mxs_runtime::MXObject *obj) -> std::size_t {
    if (!obj) return 0;
    return obj->repr().length();
}


auto mx_object_repr(mxs_runtime::MXObject *obj, char *buffer, std::size_t buffer_size)
        -> void {
    if (!obj || !buffer || buffer_size == 0) return;
    std::string repr = obj->repr();
    std::strncpy(buffer, repr.c_str(), buffer_size - 1);
    buffer[buffer_size - 1] = '\0';
}


}// extern "C"
