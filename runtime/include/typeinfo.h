#pragma once
#ifndef MXS_TYPEINFO_H
#define MXS_TYPEINFO_H

#include "_typedef.hpp"
#include "macro.hpp"
#include <string>

namespace mxs_runtime {
    class MXObject;

    struct MXTypeInfo {
        std::string inner_string;
        const MXTypeInfo *parent;
    };
}

#ifdef __cplusplus
extern "C" {
#endif
MXS_API mxs_runtime::MXObject *mxs_op_add(mxs_runtime::MXObject *,
                                          mxs_runtime::MXObject *);
MXS_API mxs_runtime::MXObject *mxs_op_sub(mxs_runtime::MXObject *,
                                          mxs_runtime::MXObject *);
MXS_API bool mxs_is_instance(mxs_runtime::MXObject *obj,
                             const mxs_runtime::MXTypeInfo *target_type_info);
#ifdef __cplusplus
}
#endif

#endif// MXS_TYPEINFO_H
