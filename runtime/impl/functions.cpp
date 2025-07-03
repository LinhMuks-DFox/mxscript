#include "functions.hpp"
#include "_typedef.hpp"
#include "boolean.hpp"
#include "nil.hpp"
#include "numeric.hpp"
#include "object.h"
#include <cstddef>
#include <cstdio>
#include <iostream>
#include <ostream>
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

extern "C" auto mxs_print_object(mxs_runtime::MXObject *obj) -> std::size_t {
    auto text = obj->repr();
    std::print("{}", text);
    return text.length();
}
