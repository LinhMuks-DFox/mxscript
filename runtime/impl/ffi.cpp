#include "builtin.hpp"
#include "container.hpp"
#include "numeric.hpp"
#include "string.hpp"
#include <dlfcn.h>
#include <string>
#include <unordered_map>
#include <utility>

namespace mxs_runtime {
    namespace {
        struct LibCache {
            std::unordered_map<std::string, void *> handle_map;
            ~LibCache() {
                for (auto const &[key, val] : handle_map) {
                    if (val) { dlclose(val); }
                }
            }
        };

        static LibCache g_lib_cache;

        static auto get_foreign_func(const std::string &lib, const std::string &name)
                -> mxs_runtime::MXObject * {
            void *&handle = g_lib_cache.handle_map[lib];
            if (!handle) {
                handle = dlopen(lib.c_str(), RTLD_LAZY);
                if (!handle) { return new MXError("FFIError", dlerror()); }
            }
            void *sym = dlsym(handle, name.c_str());
            if (!sym) { return new MXError("FFIError", dlerror()); }
            return reinterpret_cast<MXObject *>(sym);
        }

    }// namespace

}// namespace mxs_runtime

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
