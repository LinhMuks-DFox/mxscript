#include "functions.hpp"
#include "_typedef.hpp"
#include "boolean.hpp"
#include "nil.hpp"
#include "numeric.hpp"
#include "object.hpp"
#include <cstddef>
#include <cstdio>
#include <iostream>
#include <ostream>

namespace mxs_runtime {
    inner_string type_of(const MXObject *obj) { return obj->get_type_name(); }
    inner_string type_of(const MXObject &obj) { return obj.get_type_name(); }
}

extern "C" std::size_t mx_print(mxs_runtime::MXObject *obj) {
    using namespace mxs_runtime;
    auto repr = obj->repr();
    std::fprintf(stdout, "%s", repr.c_str());
    std::fflush(stdout);

    return repr.length();
}
