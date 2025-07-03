#pragma once
#ifndef MX_OBJECT_STRING_HPP
#define MX_OBJECT_STRING_HPP

#include "_typedef.hpp"
#include "macro.hpp"
#include "object.hpp"

namespace mxs_runtime {

    class MXString : public MXObject {
    public:
        inner_string value;
        explicit MXString(inner_string v);
        auto repr() const -> inner_string override;
    };

    MXS_API MXString *MXCreateString(const char *c_str);

}// namespace mxs_runtime

#endif// MX_OBJECT_STRING_HPP
