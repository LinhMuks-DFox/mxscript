#include "builtin.hpp"
#include "container.hpp"
#include "numeric.hpp"
#include "string.hpp"
#include <string>

// This file contains C++ wrappers for FFI functions, such as modern_print_wrapper.

extern "C" MXS_API auto modern_print_wrapper(mxs_runtime::MXObject *packed_argv)
        -> mxs_runtime::MXObject * {
    using namespace mxs_runtime;
    auto *argv = dynamic_cast<MXFFICallArgv *>(packed_argv);
    if (!argv) { return new MXError("TypeError", "expected FFICallArgv"); }
    std::string out;
    for (MXObject *elem : argv->args) {
        if (!out.empty()) { out += " "; }
        out += elem->repr();
    }
    std::printf("%s", out.c_str());
    std::fflush(stdout);
    return MXCreateInteger(static_cast<inner_integer>(argv->args.size()));
}
