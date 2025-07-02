#pragma once
#ifndef MXSCRIPT_NIL_HPP
#define MXSCRIPT_NIL_HPP

#include "macro.hpp"
#include "object.hpp"

namespace mxs_runtime {

    class MXNil : public MXObject {
    public:
        MXNil();
        ~MXNil() = default;
    };

    extern MXS_API const MXNil &MX_NIL;

}// namespace mxs_runtime

#ifdef __cplusplus
extern "C" {
#endif

MXS_API const mxs_runtime::MXNil *mxs_get_nil();

#ifdef __cplusplus
}
#endif

#endif// MXSCRIPT_NIL_HPP
