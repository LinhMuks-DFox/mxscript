#pragma once
#ifndef MXS_TYPEINFO_H
#define MXS_TYPEINFO_H

#include "_typedef.hpp"
#include "macro.hpp"

namespace mxs_runtime {
    class MXObject;

    struct MXTypeInfo {
        const char *name;
        const MXTypeInfo *parent;
        // Binary operation vtable entries
        MXObject *(*op_add)(MXObject *, MXObject *);
        MXObject *(*op_sub)(MXObject *, MXObject *);
        MXObject *(*op_eq)(MXObject *, MXObject *);
    };
}

#ifdef __cplusplus
extern "C" {
#endif
MXS_API mxs_runtime::MXObject *integer_add_integer(mxs_runtime::MXObject *,
                                                   mxs_runtime::MXObject *);
MXS_API mxs_runtime::MXObject *integer_sub_integer(mxs_runtime::MXObject *,
                                                   mxs_runtime::MXObject *);
MXS_API mxs_runtime::MXObject *mxs_op_add(mxs_runtime::MXObject *,
                                          mxs_runtime::MXObject *);
MXS_API mxs_runtime::MXObject *mxs_op_sub(mxs_runtime::MXObject *,
                                          mxs_runtime::MXObject *);
MXS_API mxs_runtime::inner_integer mxs_get_integer_value(mxs_runtime::MXObject *);
#ifdef __cplusplus
}
#endif

#endif// MXS_TYPEINFO_H
