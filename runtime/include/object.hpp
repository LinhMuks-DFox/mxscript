#pragma once

#ifndef MXSCRIPT_OBJECT_H
#define MXSCRIPT_OBJECT_H

#include "_typedef.hpp"
#include "macro.hpp"
#include <cstddef>
#include <string>

namespace mxs_runtime {

    struct RTTI {
        std::string type_name;
    };

    class MXObject {
    private:
        refer_count_type ref_cnt = 0;
        const RTTI *const rtti;
        bool _is_static = false;

    public:
        explicit MXObject(const RTTI *rtti, bool is_static = false);
        MXObject(const MXObject &other);
        virtual ~MXObject();
        auto increase_ref() -> refer_count_type;
        auto decrease_ref() -> refer_count_type;
        auto get_type_name() const -> const std::string &;
        virtual auto equals(const MXObject &other) -> inner_boolean;
        virtual auto equals(const MXObject *other) -> inner_boolean;
        virtual auto hash_code() -> hash_code_type;
        virtual auto repr() const
                -> inner_string;// return a representation in string form
    };

}// namespace mxs_runtime


// C API:

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
#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_OBJECT_H
