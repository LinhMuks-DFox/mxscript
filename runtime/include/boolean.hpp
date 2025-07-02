#pragma once
#ifndef MXSCRIPT_BOOLEAN_HPP
#define MXSCRIPT_BOOLEAN_HPP

#include "object.hpp"
#include "_typedef.hpp"
#include "macro.hpp"

namespace mxs_runtime {

class MXBoolean : public MXObject {
public:
    const inner_boolean value;
    explicit MXBoolean(inner_boolean v);
};

extern MXS_API const MXBoolean& MX_TRUE;
extern MXS_API const MXBoolean& MX_FALSE;

} // namespace mxs_runtime

#ifdef __cplusplus
extern "C" {
#endif

MXS_API const mxs_runtime::MXBoolean* mxs_get_true();
MXS_API const mxs_runtime::MXBoolean* mxs_get_false();

#ifdef __cplusplus
}
#endif

#endif // MXSCRIPT_BOOLEAN_HPP
