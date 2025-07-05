#include "include/ffi.hpp"
#include "container.hpp"
#include "numeric.hpp"
#include "string.hpp"
#include <dlfcn.h>
#include <string>
#include <unordered_map>
#include <utility>

namespace mxs_runtime {
    namespace {
        struct LibEntry {
            void *handle{ nullptr };
            std::unordered_map<std::string, void *> symbols;
        };

        static std::unordered_map<std::string, LibEntry> g_lib_cache;


        static void *get_foreign_func(const std::string &lib, const std::string &name) {
            auto &entry = g_lib_cache[lib];
            if (!entry.handle) {
                entry.handle = dlopen(lib.c_str(), RTLD_LAZY);
                if (!entry.handle) return nullptr;
            }
            auto it = entry.symbols.find(name);
            if (it != entry.symbols.end()) return it->second;
            void *sym = dlsym(entry.handle, name.c_str());
            if (sym) entry.symbols.emplace(name, sym);
            return sym;
        }

    }// namespace

}// namespace mxs_runtime

extern "C" auto mxs_variadic_print(mxs_runtime::MXObject *fmt_obj,
                                   mxs_runtime::MXObject *list_obj)
        -> mxs_runtime::MXObject * {
    using namespace mxs_runtime;
    auto *fmt = dynamic_cast<MXString *>(fmt_obj);
    auto *lst = dynamic_cast<MXList *>(list_obj);
    if (!fmt || !lst) { return new MXError("TypeError", "expected String and List"); }
    std::string out = fmt->value;
    for (MXObject *elem : lst->elements) {
        out += " ";
        out += elem->repr();
    }
    std::printf("%s", out.c_str());
    std::fflush(stdout);
    return MXCreateInteger(static_cast<inner_integer>(lst->elements.size()));
}
