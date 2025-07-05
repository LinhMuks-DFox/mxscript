#include "include/ffi.hpp"
#include "container.hpp"
#include "numeric.hpp"
#include "string.hpp"
#include <array>
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

        static constexpr int MAX_FFI_ARGS = 10;

        template<std::size_t... Is>
        using FnFor = MXObject *(*) (decltype((void) Is,
                                              static_cast<MXObject *>(nullptr))...);

        template<std::size_t... Is>
        auto invoke(void *fn, MXObject **argv, std::index_sequence<Is...>) -> MXObject * {
            return reinterpret_cast<FnFor<Is...>>(fn)(argv[Is]...);
        }

        template<std::size_t N>
        auto call_ffi(void *fn, MXObject **argv) -> MXObject * {
            return invoke(fn, argv, std::make_index_sequence<N>{});
        }

        template<std::size_t... Ns>
        constexpr auto make_table(std::index_sequence<Ns...>)
                -> std::array<MXObject *(*) (void *, MXObject **), sizeof...(Ns)> {
            return { &call_ffi<Ns>... };
        }

        static constexpr auto CALL_TABLE =
                make_table(std::make_index_sequence<MAX_FFI_ARGS + 1>{});

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
    if (argc < 0 || argc > MAX_FFI_ARGS) {
        return new MXError("FFIError", "ffi_call supports up to " +
                                               std::to_string(MAX_FFI_ARGS) +
                                               " arguments");
    }
    return CALL_TABLE[static_cast<std::size_t>(argc)](fn, argv);
}

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
