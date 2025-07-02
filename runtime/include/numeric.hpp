#pragma once
#ifndef MX_OBJECT_NUMERIC_HPP
#define MX_OBJECT_NUMERIC_HPP

#include "object.hpp"

namespace mxs_runtime {
    class MXInteger : MXObject { };

    class MXSmallInteger : MXInteger { };

    class MXBigIneterer : MXInteger { };

    class MXFloatPoint : MXObject { };

    class MXComplex : MXObject { };

    class MXDecimal : MXObject { };
}

// C API
#endif//MX_OBJECT_NUMERIC_HPP