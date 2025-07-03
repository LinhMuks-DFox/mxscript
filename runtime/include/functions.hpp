#ifndef MX_FUNCTIONS_HPP
#define MX_FUNCTIONS_HPP
#include "include/_typedef.hpp"
#include "include/object.h"
#include <cstddef>
#include <iostream>
namespace mxs_runtime {

    inner_string type_of(const MXObject *obj);
    inner_string type_of(const MXObject &obj);
}

extern "C" mxs_runtime::MXObject *mxs_print_object_ext(mxs_runtime::MXObject *obj,
                                                       mxs_runtime::MXObject *end);
#endif// MX_FUNCTIONS_HPP
