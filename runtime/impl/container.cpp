#include "container.hpp"
#include "allocator.hpp"
#include "typeinfo.h"
#include "numeric.hpp"
#include <stdexcept>

namespace mxs_runtime {

//============================
// MXContainer base
//============================
MXContainer::MXContainer(const MXTypeInfo *info, bool is_static)
    : MXObject(info, is_static) {}

//============================
// Type Info
//============================
static const MXTypeInfo g_list_type_info{
    "List",
    nullptr,
    nullptr,
    nullptr,
    nullptr
};

//============================
// MXList Implementation
//============================
MXList::MXList(bool is_static)
    : MXContainer(&g_list_type_info, is_static) {}

MXList::~MXList() {
    for (MXObject* elem : elements) {
        ::decrease_ref(elem);
    }
}

auto MXList::length() const -> std::size_t { return elements.size(); }

auto MXList::contains(const MXObject& obj) const -> bool {
    for (MXObject* e : elements) {
        if (e->equals(&obj)) return true;
    }
    return false;
}

auto MXList::op_getitem(const MXObject& key) const -> MXObject* {
    // only integer index allowed
    if (std::string(key.get_type_name()) != "Integer") {
        return new MXError();
    }
    auto idx = static_cast<const MXInteger&>(key).value;
    if (idx < 0 || static_cast<std::size_t>(idx) >= elements.size()) {
        return new MXError();
    }
    return elements[static_cast<std::size_t>(idx)];
}

auto MXList::op_setitem(const MXObject& key, MXObject& value) -> void {
    if (std::string(key.get_type_name()) != "Integer") {
        return;
    }
    auto idx = static_cast<const MXInteger&>(key).value;
    if (idx < 0 || static_cast<std::size_t>(idx) >= elements.size()) {
        return;
    }
    std::size_t i = static_cast<std::size_t>(idx);
    MXObject* old = elements[i];
    ::increase_ref(&value);
    elements[i] = &value;
    ::decrease_ref(old);
}

auto MXList::op_append(MXObject& value) -> void {
    ::increase_ref(&value);
    elements.push_back(&value);
}

//============================
// C API
//============================
extern "C" {
MXS_API MXList* MXCreateList() {
    auto* obj = new MXList(false);
    MX_ALLOCATOR.registerObject(obj);
    obj->increase_ref();
    return obj;
}

MXS_API MXObject* list_getitem(MXObject* list, MXObject* index) {
    if (!list) return new MXError();
    auto* l = dynamic_cast<MXList*>(list);
    if (!l) return new MXError();
    return l->op_getitem(*index);
}

MXS_API void list_setitem(MXObject* list, MXObject* index, MXObject* value) {
    if (!list) return;
    auto* l = dynamic_cast<MXList*>(list);
    if (!l) return;
    l->op_setitem(*index, *value);
}

MXS_API void list_append(MXObject* list, MXObject* value) {
    if (!list) return;
    auto* l = dynamic_cast<MXList*>(list);
    if (!l) return;
    l->op_append(*value);
}

MXS_API MXObject* mxs_op_getitem(MXObject* container, MXObject* key) {
    auto* l = dynamic_cast<MXList*>(container);
    if (l) return l->op_getitem(*key);
    return new MXError();
}

MXS_API void mxs_op_setitem(MXObject* container, MXObject* key, MXObject* value) {
    auto* l = dynamic_cast<MXList*>(container);
    if (l) l->op_setitem(*key, *value);
}
} // extern "C"

} // namespace mxs_runtime

