#pragma once
#ifndef MXSCRIPT_OBJECT_H
#define MXSCRIPT_OBJECT_H
#include "object.hpp"
#include <cstddef>
#include <string>
// cpp implementation
namespace mxs_runtime {
    class MXObject {
    private:
        std::size_t ref_cnt = 0;
        std::string object_type_name{ "object" };

    public:
        virtual ~MXObject();
        MXObject();
        MXObject(const MXObject &other);
        std::size_t increase_ref();
        std::size_t decrease_ref();
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

#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_OBJECT_H