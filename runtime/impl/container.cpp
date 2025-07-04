#include "container.hpp"
#include "allocator.hpp"
#include "numeric.hpp"
#include "typeinfo.h"
#include <stdexcept>
#include <string>

#define CHECK_LIST(obj)                                                                  \
    if (!(obj) || std::string((obj)->get_type_name()) != "List") {                       \
        return new mxs_runtime::MXError("TypeError", "Argument must be a List.");        \
    }

#define CHECK_INT(obj)                                                                   \
    if (!(obj) || std::string((obj)->get_type_name()) != "Integer") {                    \
        return new mxs_runtime::MXError("TypeError", "Argument must be an Integer.");    \
    }

namespace mxs_runtime {

    //============================
    // MXContainer base
    //============================
    MXContainer::MXContainer(const MXTypeInfo *info, bool is_static)
        : MXObject(info, is_static) { }

    //============================
    // Type Info
    //============================
    static const MXTypeInfo g_list_type_info{ "List", nullptr };

    //============================
    // MXList Implementation
    //============================
    MXList::MXList(bool is_static) : MXContainer(&g_list_type_info, is_static) { }

    MXList::~MXList() {
        for (MXObject *elem : elements) { ::decrease_ref(elem); }
    }

    auto MXList::length() const -> std::size_t { return elements.size(); }

    auto MXList::contains(const MXObject &obj) const -> bool {
        for (MXObject *e : elements) {
            if (e->equals(&obj)) return true;
        }
        return false;
    }

    auto MXList::op_getitem(const MXObject &key) const -> MXObject * {
        // only integer index allowed
        if (std::string(key.get_type_name()) != "Integer") { return new MXError(); }
        auto idx = static_cast<const MXInteger &>(key).value;
        if (idx < 0 || static_cast<std::size_t>(idx) >= elements.size()) {
            return new MXError();
        }
        return elements[static_cast<std::size_t>(idx)];
    }

    auto MXList::op_setitem(const MXObject &key, MXObject &value) -> void {
        if (std::string(key.get_type_name()) != "Integer") { return; }
        auto idx = static_cast<const MXInteger &>(key).value;
        if (idx < 0 || static_cast<std::size_t>(idx) >= elements.size()) { return; }
        std::size_t i = static_cast<std::size_t>(idx);
        MXObject *old = elements[i];
        ::increase_ref(&value);
        elements[i] = &value;
        ::decrease_ref(old);
    }

    auto MXList::op_append(MXObject &value) -> void {
        ::increase_ref(&value);
        elements.push_back(&value);
    }


}// namespace mxs_runtime
//============================
// C API
//============================
#ifdef __cplusplus
extern "C" {
#endif
MXS_API mxs_runtime::MXList *MXCreateList() {
    auto *obj = new mxs_runtime::MXList(false);
    mxs_runtime::MX_ALLOCATOR.registerObject(obj);
    obj->increase_ref();
    return obj;
}

MXS_API mxs_runtime::MXObject *list_getitem(mxs_runtime::MXObject *list,
                                            mxs_runtime::MXObject *index) {
    CHECK_LIST(list);
    CHECK_INT(index);
    auto *l = static_cast<mxs_runtime::MXList *>(list);
    return l->op_getitem(*index);
}

MXS_API void list_setitem(mxs_runtime::MXObject *list, mxs_runtime::MXObject *index,
                          mxs_runtime::MXObject *value) {
    CHECK_LIST(list);
    CHECK_INT(index);
    auto *l = static_cast<mxs_runtime::MXList *>(list);
    l->op_setitem(*index, *value);
}

MXS_API void list_append(mxs_runtime::MXObject *list, mxs_runtime::MXObject *value) {
    CHECK_LIST(list);
    auto *l = static_cast<mxs_runtime::MXList *>(list);
    l->op_append(*value);
}

MXS_API mxs_runtime::MXObject *mxs_op_getitem(mxs_runtime::MXObject *container,
                                              mxs_runtime::MXObject *key) {
    CHECK_LIST(container);
    CHECK_INT(key);
    auto *l = static_cast<mxs_runtime::MXList *>(container);
    return l->op_getitem(*key);
}

MXS_API void mxs_op_setitem(mxs_runtime::MXObject *container, mxs_runtime::MXObject *key,
                            mxs_runtime::MXObject *value) {
    CHECK_LIST(container);
    CHECK_INT(key);
    auto *l = static_cast<mxs_runtime::MXList *>(container);
    l->op_setitem(*key, *value);
}
#ifdef __cplusplus
}// extern "C"
#endif
