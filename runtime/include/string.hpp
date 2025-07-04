#pragma once
#ifndef MX_OBJECT_STRING_HPP
#define MX_OBJECT_STRING_HPP

#include "_typedef.hpp"
#include "macro.hpp"
#include "object.h"
#include "typeinfo.h"

namespace mxs_runtime {

    class MXString : public MXObject {
    public:
        inner_string value;
        explicit MXString(inner_string v);
        auto repr() const -> inner_string override;
    };

    MXS_API MXString *MXCreateString(const char *c_str);

}// namespace mxs_runtime

#ifdef __cplusplus
extern "C" {
#endif
MXS_API mxs_runtime::MXObject *
mxs_string_from_integer(mxs_runtime::MXObject *integer_obj);
#ifdef __cplusplus
}
#endif

#endif// MX_OBJECT_STRING_HPP
