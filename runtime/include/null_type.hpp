#pragma once
#ifndef MXSCRIPT_NULL_HPP
#define MXSCRIPT_NULL_HPP
#include "_typedef.hpp"
#include "object.hpp"
namespace mxs_runtime {
    class MXNil : MXObject {
    public:
        MXNil();
        MXNil(inner_boolean value);
        ~MXNil();
        const MXObject *value = nullptr;

    public:
        inner_boolean equals(const MXObject &other);
        inner_boolean equals(const MXObject *other);
        inner_boolean equals(const MXNil &other);
        inner_boolean equals(const MXNil *other);
    };
}

static mxs_runtime::MXNil MXNIL;


// C API:

#ifdef __cplusplus
extern "C" {
#endif

#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_NULL_HPP