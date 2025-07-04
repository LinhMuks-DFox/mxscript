#include "ffi.hpp"
#include "string.hpp"
#include <dlfcn.h>
#include <string>
#include <unordered_map>

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

extern "C" auto mxs_ffi_call(mxs_runtime::MXObject *lib_name_obj,
                             mxs_runtime::MXObject *func_name_obj, int argc,
                             mxs_runtime::MXObject **argv) -> mxs_runtime::MXObject * {
    using namespace mxs_runtime;
    auto *lib_str = dynamic_cast<MXString *>(lib_name_obj);
    auto *func_str = dynamic_cast<MXString *>(func_name_obj);
    if (!lib_str || !func_str) {
        return new MXError("TypeError", "ffi_call expects string arguments");
    }
    void *fn = get_foreign_func(lib_str->value, func_str->value);
    if (!fn) { return new MXError("FFIError", "symbol lookup failed"); }
    switch (argc) {
        case 0: {
            using Fn = MXObject *(*) ();
            return reinterpret_cast<Fn>(fn)();
        }
        case 1: {
            using Fn = MXObject *(*) (MXObject *);
            return reinterpret_cast<Fn>(fn)(argv[0]);
        }
        case 2: {
            using Fn = MXObject *(*) (MXObject *, MXObject *);
            return reinterpret_cast<Fn>(fn)(argv[0], argv[1]);
        }
        case 3: {
            using Fn = MXObject *(*) (MXObject *, MXObject *, MXObject *);
            return reinterpret_cast<Fn>(fn)(argv[0], argv[1], argv[2]);
        }
        case 4: {
            using Fn = MXObject *(*) (MXObject *, MXObject *, MXObject *, MXObject *);
            return reinterpret_cast<Fn>(fn)(argv[0], argv[1], argv[2], argv[3]);
        }
        case 5: {
            using Fn = MXObject *(*) (MXObject *, MXObject *, MXObject *, MXObject *,
                                      MXObject *);
            return reinterpret_cast<Fn>(fn)(argv[0], argv[1], argv[2], argv[3], argv[4]);
        }
        default:
            return new MXError("FFIError", "unsupported argument count");
    }
}
