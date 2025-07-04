#pragma once
#ifndef MXSCRIPT_CONTAINER_HPP
#define MXSCRIPT_CONTAINER_HPP

#include "_typedef.hpp"
#include "macro.hpp"
#include "object.h"
#include "typeinfo.h"
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace mxs_runtime {

    //======================================================================
    // Base Class
    //======================================================================

    /**
     * @brief Abstract base class for all container types.
     */
    class MXContainer : public MXObject {
    public:
        explicit MXContainer(const MXTypeInfo *info, bool is_static = false);
        virtual auto length() const -> std::size_t = 0;
        virtual auto contains(const MXObject &obj) const -> bool = 0;
    };


    //======================================================================
    // Concrete Container Implementations
    //======================================================================

    /**
     * @brief A mutable, ordered sequence of objects. Analogous to Python's list.
     */
    class MXList : public MXContainer {
    public:
        std::vector<MXObject *> elements;

        explicit MXList(bool is_static = false);
        ~MXList();
        auto length() const -> std::size_t override;
        auto contains(const MXObject &obj) const -> bool override;

        // --- List Methods ---
        auto append(MXObject &value) -> MXObject *;
        auto pop() -> MXObject *;
        auto extend(const MXList &other) -> MXObject *;
        auto index_of(const MXObject &value) const -> MXObject *;
        auto insert(inner_integer index, MXObject &value) -> MXObject *;
        auto remove(const MXObject &value) -> MXObject *;

        // --- VTable Operations ---
        auto op_getitem(const MXObject &key) const -> MXObject *;
        auto op_setitem(const MXObject &key, MXObject &value) -> MXObject *;
        auto op_append(MXObject &value) -> MXObject *;
        auto op_add(const MXObject &other) -> MXObject * override;
        auto op_mul(const MXObject &other) -> MXObject * override;
    };

    /**
     * @brief A mutable mapping of key-value pairs. Analogous to Python's dict.
     * Note: Requires custom hash and equality functors for MXObject*.
     */
    class MXDict : public MXContainer {
    public:
        // Placeholder for a map using a custom hash for MXObject*
        std::unordered_map<MXObject *, MXObject *> elements;

        explicit MXDict(bool is_static = false);
        auto length() const -> std::size_t override;
        auto contains(const MXObject &key) const -> bool override;

        // --- VTable Operations ---
        auto op_getitem(const MXObject &key) const -> MXObject *;
        auto op_setitem(const MXObject &key, MXObject &value) -> void;
    };

    /**
     * @brief An immutable, ordered sequence of objects. Analogous to Python's tuple.
     */
    class MXTuple : public MXContainer {
    public:
        const std::vector<MXObject *> elements;

        explicit MXTuple(std::vector<MXObject *> elems, bool is_static = false);
        auto length() const -> std::size_t override;
        auto contains(const MXObject &obj) const -> bool override;

        // --- VTable Operations ---
        auto op_getitem(const MXObject &key) const -> MXObject *;
    };


}// namespace mxs_runtime


#ifdef __cplusplus
extern "C" {
#endif
//======================================================================
// C API for Runtime Object Creation
//======================================================================
MXS_API mxs_runtime::MXList *MXCreateList();
MXS_API mxs_runtime::MXDict *MXCreateDict();
MXS_API mxs_runtime::MXTuple *MXCreateTuple(mxs_runtime::MXObject **elements,
                                            std::size_t count);


//======================================================================
// C API for Container Operations (Static & Dynamic Dispatch)
//======================================================================

// --- Get Item (`obj[key]`) ---
MXS_API mxs_runtime::MXObject *list_getitem(mxs_runtime::MXObject *list,
                                            mxs_runtime::MXObject *index);// Fast path
MXS_API mxs_runtime::MXObject *dict_getitem(mxs_runtime::MXObject *dict,
                                            mxs_runtime::MXObject *key);// Fast path
MXS_API mxs_runtime::MXObject *
mxs_op_getitem(mxs_runtime::MXObject *container,
               mxs_runtime::MXObject *key);// Polymorphic path

// --- Set Item (`obj[key] = value`) ---
MXS_API mxs_runtime::MXObject *list_setitem(mxs_runtime::MXObject *list,
                                            mxs_runtime::MXObject *index,
                                            mxs_runtime::MXObject *value);// Fast path
MXS_API void dict_setitem(mxs_runtime::MXObject *dict, mxs_runtime::MXObject *key,
                          mxs_runtime::MXObject *value);// Fast path
MXS_API mxs_runtime::MXObject *
mxs_op_setitem(mxs_runtime::MXObject *container, mxs_runtime::MXObject *key,
               mxs_runtime::MXObject *value);// Polymorphic path

// --- List specific ---
MXS_API mxs_runtime::MXObject *list_append(mxs_runtime::MXObject *list,
                                           mxs_runtime::MXObject *value);

#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_CONTAINER_HPP
