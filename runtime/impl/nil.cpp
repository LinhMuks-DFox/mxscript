#include "nil.hpp"
#include "_typedef.hpp"

namespace mxs_runtime {

    static const RTTI RTTI_NIL{"Nil"};
    static MXNil nil_instance;

    MXS_API const MXNil &MX_NIL = nil_instance;

    MXNil::MXNil() : MXObject(&RTTI_NIL, true) {}
    auto MXNil::repr() const -> inner_string { return "nil"; }

}// namespace mxs_runtime

extern "C" {

auto mxs_get_nil() -> const mxs_runtime::MXNil* {
    return &mxs_runtime::MX_NIL;
}

}// extern "C"
