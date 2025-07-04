#include "functions.hpp"
#include "_typedef.hpp"
#include "boolean.hpp"
#include "nil.hpp"
#include "numeric.hpp"
#include "object.h"
#include "string.hpp"
#include <cstddef>
#include <cstdio>
#include <iostream>
#include <ostream>
#include <string>
#if __has_include(<print>)
#include <print>
#else
#include <cstdio>
#include <format>
namespace std {
    template<class... Args>
    void print(std::format_string<Args...> fmt, Args &&...args) {
        std::fputs(std::format(fmt, std::forward<Args>(args)...).c_str(), stdout);
    }
}
#endif

namespace mxs_runtime {
    auto type_of(const MXObject *obj) -> inner_string { return obj->get_type_name(); }
    auto type_of(const MXObject &obj) -> inner_string { return obj.get_type_name(); }
}

extern "C" auto mxs_print_object_ext(mxs_runtime::MXObject *obj,
                                     mxs_runtime::MXObject *end)
        -> mxs_runtime::MXObject * {
    if (!obj) {
        return new mxs_runtime::MXError("TypeError", "Object argument is null.");
    }
    if (end && std::string(end->get_type_name()) != "String") {
        return new mxs_runtime::MXError("TypeError", "end must be a String.");
    }
    auto text = obj->repr();
    auto *end_str = end ? static_cast<mxs_runtime::MXString *>(end) : nullptr;
    auto suffix = end_str ? end_str->value : mxs_runtime::inner_string{};
    std::print("{}{}", text, suffix);
    return const_cast<mxs_runtime::MXObject *>(
            reinterpret_cast<const mxs_runtime::MXObject *>(mxs_get_nil()));
}
