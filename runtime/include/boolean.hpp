#pragma once
#ifndef MXSCRIPT_BOOLEAN_H
#define MXSCRIPT_BOOLEAN_H
#include "_typedef.hpp"
#include "macro.hpp"
#include "object.hpp"
// cpp implementation
namespace mxs_runtime {
    class MXBoolean : MXObject {
    public:
        MXBoolean();
        MXBoolean(inner_boolean value);
        ~MXBoolean();
        const inner_boolean value;

    public:
        inner_boolean equals(const MXObject &other);
        inner_boolean equals(const MXObject *other);
        inner_boolean equals(const MXBoolean &other);
        inner_boolean equals(const MXBoolean *other);
    };
    extern MXS_API const MXBoolean &MX_TRUE;
    extern MXS_API const MXBoolean &MX_FALSE;
}


// C API:

#ifdef __cplusplus
extern "C" {
#endif

#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_BOOLEAN_H