#pragma once
#include "_typedef.hpp"
#ifndef MXSCRIPT_BOOLEAN_H
#define MXSCRIPT_BOOLEAN_H
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
}

static mxs_runtime::MXBoolean MX_TRUE{ true };
static mxs_runtime::MXBoolean MX_FALSE{ false };


// C API:

#ifdef __cplusplus
extern "C" {
#endif

#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_BOOLEAN_H