#ifndef MX_FUNCTIONS_HPP
#define MX_FUNCTIONS_HPP
#include "include/_typedef.hpp"
#include "include/object.hpp"
#include <cstddef>
#include <iostream>
namespace mxs_runtime {

    inner_string type_of(const MXObject *obj);
    inner_string type_of(const MXObject &obj);
}

extern "C" std::size_t mx_print(mxs_runtime::MXObject *obj);
#endif// MX_FUNCTIONS_HPP
