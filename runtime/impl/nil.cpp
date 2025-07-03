#include "nil.hpp"
#include "_typedef.hpp"

namespace mxs_runtime {

    static MXNil nil_instance;

    MXS_API const MXNil &MX_NIL = nil_instance;

    MXNil::MXNil() : MXObject(true) { this->set_type_name("nil"); }
    auto MXNil::repr() const -> inner_string { return "nil"; }

}// namespace mxs_runtime

extern "C" {

const mxs_runtime::MXNil *mxs_get_nil() { return &mxs_runtime::MX_NIL; }

}// extern "C"
