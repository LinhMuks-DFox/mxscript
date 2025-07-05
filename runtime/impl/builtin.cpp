#include "builtin.hpp"
#include <cstdio>
#include <string>

using namespace mxs_runtime;

extern "C" MXS_API MXObject *printf_wrapper(MXObject *format_obj, MXObject *packed_obj) {
    auto *fmt = dynamic_cast<MXString *>(format_obj);
    auto *argv = dynamic_cast<MXFFICallArgv *>(packed_obj);
    if (!fmt || !argv) {
        return new MXError("TypeError", "expected String and FFICallArgv");
    }

    std::string out = fmt->value;
    for (MXObject *elem : argv->args) {
        out += " ";
        if (auto *s = dynamic_cast<MXString *>(elem)) {
            out += s->value;
        } else if (auto *i = dynamic_cast<MXInteger *>(elem)) {
            out += std::to_string(i->value);
        } else if (auto *f = dynamic_cast<MXFloat *>(elem)) {
            out += std::to_string(f->value);
        } else if (auto *b = dynamic_cast<MXBoolean *>(elem)) {
            out += b->value ? "true" : "false";
        } else if (dynamic_cast<MXNil *>(elem)) {
            out += "nil";
        } else {
            out += elem->repr();
        }
    }

    int printed = std::printf("%s", out.c_str());
    std::fflush(stdout);
    return MXCreateInteger(static_cast<inner_integer>(printed));
}

