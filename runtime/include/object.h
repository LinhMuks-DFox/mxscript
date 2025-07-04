#pragma once
#ifndef MXSCRIPT_OBJECT_H
#define MXSCRIPT_OBJECT_H

#include "_typedef.hpp"
#include "macro.hpp"
#include "typeinfo.h"
#include <cstddef>
#include <string>
#include <vector>
namespace mxs_runtime {

    class MXObject {
    private:
        refer_count_type ref_cnt = 0;
        const MXTypeInfo *type_info;
        bool _is_static = false;

    public:
        explicit MXObject(const MXTypeInfo *info, bool is_static = false);
        MXObject(const MXObject &other);
        virtual ~MXObject();

        auto increase_ref() -> refer_count_type;
        auto decrease_ref() -> refer_count_type;
        auto get_type_name() const -> const char *;
        virtual auto equals(const MXObject &other) -> inner_boolean;
        virtual auto equals(const MXObject *other) -> inner_boolean;
        virtual auto hash_code() -> hash_code_type;
        virtual auto repr() const -> inner_string;// representation

        const MXTypeInfo *get_type_info() const { return type_info; }
    };

    class MXError : public MXObject {
    public:
        MXError();
        virtual ~MXError() = default;
        auto repr() const -> inner_string override;

    private:
        inner_string msg;
        inner_boolean panic;
        inner_string MXErroType;
        MXObject *alternative;
    };

    struct MXPODField {
        const inner_string name;
        const std::size_t offset;
        const MXTypeInfo *const type;
    };

    class MXPODLayout {
    public:
        const inner_string name;
        const std::vector<MXPODField> fields;
        const std::size_t total_size;

        // Constructor to initialize the layout.
        MXPODLayout(inner_string n, std::vector<MXPODField> f, std::size_t size);
    };
    class MXPODObject : public MXObject {
        void *const source;
        const MXPODLayout *const layout;// Pointer to the shared layout definition.

        explicit MXPODObject(void *src, const MXPODLayout *layout_info);
        auto repr() const -> inner_string override;

        // --- VTable Operations ---
        // Provides field access like 'pod_obj.field_name'.
        auto op_getattr(const inner_string &field_name) const -> MXObject *;
        // Compares the content of the memory blocks.
        auto op_eq(const MXObject &other) const -> MXObject *;
    };

}// namespace mxs_runtime

#ifdef __cplusplus
extern "C" {
#endif
mxs_runtime::MXObject *new_mx_object();
void delete_mx_object(mxs_runtime::MXObject *obj);
std::size_t increase_ref(mxs_runtime::MXObject *obj);
std::size_t decrease_ref(mxs_runtime::MXObject *obj);
const char *mxs_get_object_type_name(mxs_runtime::MXObject *obj);
mxs_runtime::inner_boolean mx_object_equals(mxs_runtime::MXObject *obj1,
                                            mxs_runtime::MXObject *obj2);
std::size_t mx_object_repr_length(mxs_runtime::MXObject *obj);
void mx_object_repr(mxs_runtime::MXObject *obj, char *buffer, std::size_t buffer_size);
/**
     * @brief Registers a new POD layout with the runtime.
     * The compiler frontend calls this to define POD structs.
     * @return A pointer to the newly created and registered layout.
     */
MXS_API mxs_runtime::MXPODLayout *
MXRegisterPODLayout(const char *name,
                    const std::vector<mxs_runtime::MXPODLayout> &fields);

/**
      * @brief Creates a non-owning MXPODObject that points to existing memory,
      * associating it with a specific layout.
      */
MXS_API mxs_runtime::MXPODLayout *MXCreatePOD(void *source,
                                              const mxs_runtime::MXPODLayout *layout);

#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_OBJECT_H
