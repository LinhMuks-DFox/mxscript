#ifndef MX_TYPE_DEF
#define MX_TYPE_DEF
#include <cctype>
#include <cstdint>
#include <string>

namespace mxs_runtime {
    using hash_code_type = std::uint64_t;
    using inner_string = std::string;
    using inner_boolean = bool;
    using refer_count_type = std::uint64_t;
}

#endif//MX_TYPE_DEF