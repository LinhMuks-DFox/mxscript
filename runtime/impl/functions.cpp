#include "functions.hpp"
#include "numeric.hpp"
#include "boolean.hpp"
#include "nil.hpp"
#include <iostream>

namespace mxs_runtime {
    inner_string type_of(const MXObject *obj) { return obj->get_type_name(); }
    inner_string type_of(const MXObject &obj) { return obj.get_type_name(); }
}

extern "C" void mxs_print_object(mxs_runtime::MXObject *obj) {
    using namespace mxs_runtime;
    if (obj == nullptr) {
        std::cout << "nil";
        std::cout.flush();
        return;
    }
    if (auto *i = dynamic_cast<MXInteger *>(obj)) {
        std::cout << i->value;
    } else if (auto *f = dynamic_cast<MXFloat *>(obj)) {
        std::cout << f->value;
    } else if (auto *b = dynamic_cast<MXBoolean *>(obj)) {
        std::cout << (b->value ? "true" : "false");
    } else if (dynamic_cast<MXNil *>(obj)) {
        std::cout << "nil";
    } else {
        std::cout << "<object>";
    }
    std::cout.flush();
}

