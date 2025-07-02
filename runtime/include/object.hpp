#pragma once

#ifndef MXSCRIPT_OBJECT_H
#define MXSCRIPT_OBJECT_H

#include "_typedef.hpp"
#include <cstddef>
#include <string>
namespace mxs_runtime {
    class MXObject {
    private:
        refer_count_type ref_cnt = 0;
        std::string object_type_name{ "object" };

    public:
        virtual ~MXObject();
        MXObject();
        MXObject(const MXObject &other);
        refer_count_type increase_ref();
        refer_count_type decrease_ref();
        const std::string &get_type_name() const;
        void set_type_name(const std::string &name);
        virtual inner_boolean equals(const MXObject &other);
        virtual inner_boolean equals(const MXObject *other);
        virtual hash_code_type hash_code();
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
const char *get_object_type_name(mxs_runtime::MXObject *obj);
void set_object_type_name(mxs_runtime::MXObject *obj, const char *name);
mxs_runtime::inner_boolean mx_object_equals(mxs_runtime::MXObject *obj1,
                                            mxs_runtime::MXObject *obj2);
#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_OBJECT_H