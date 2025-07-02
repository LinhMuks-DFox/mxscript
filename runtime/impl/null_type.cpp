#include "include/null_type.hpp"
#include "_typedef.hpp"
#include "macro.hpp"
#include "object.hpp"

namespace mxs_runtime {
    static MXS_API MXNil nil_instance;

    MXS_API const MXNil &MXNIL = nil_instance;


}// namespace
