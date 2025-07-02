#ifndef MX_FUNCTIONS_HPP
#define MX_FUNCTIONS_HPP
#include "include/_typedef.hpp"
#include "include/object.hpp"
namespace mxs_runtime {

    inner_string type_of(const MXObject *obj);
    inner_string type_of(const MXObject &obj);
}
#endif// MX_FUNCTIONS_HPP