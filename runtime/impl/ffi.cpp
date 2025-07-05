#include "include/ffi.hpp"
#include "container.hpp"
#include "numeric.hpp"
#include "string.hpp"
#include <dlfcn.h>
#include <ffi.h>
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

    MXS_API MXObject *mxs_ffi_call(MXObject *lib_name_obj, MXObject *func_name_obj,
                                   MXObject *argv_obj) {
        auto *lib_str = dynamic_cast<MXString *>(lib_name_obj);
        auto *func_str = dynamic_cast<MXString *>(func_name_obj);
        auto *argv = dynamic_cast<MXFFICallArgv *>(argv_obj);
        if (!lib_str || !func_str || !argv) {
            return new MXError("TypeError", "invalid arguments to ffi_call");
        }

        void *fn = get_foreign_func(lib_str->value, func_str->value);
        if (!fn) { return new MXError("FFIError", "symbol lookup failed"); }

        std::size_t argc = argv->args.size();
        std::vector<ffi_type *> arg_types(argc, &ffi_type_pointer);
        ffi_cif cif;
        if (ffi_prep_cif(&cif, FFI_DEFAULT_ABI, static_cast<unsigned int>(argc),
                         &ffi_type_pointer, arg_types.data()) != FFI_OK) {
            return new MXError("FFIError", "ffi_prep_cif failed");
        }

        std::vector<void *> values(argc);
        for (std::size_t i = 0; i < argc; ++i) {
            values[i] = &argv->args[i];
        }

        MXObject *result = nullptr;
        ffi_call(&cif, FFI_FN(fn), &result, values.data());
        return result;
    }

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
