#include "allocator.hpp"
#include "object.hpp"
#include <cstdio>

namespace mxs_runtime {

    static Allocator allocator_instance;
    MXS_API Allocator &MX_ALLOCATOR = allocator_instance;

    void Allocator::registerObject(MXObject *obj) {
        if (!obj) return;
        std::lock_guard<std::mutex> lock(mtx);
        objects.insert(obj);
    }

    void Allocator::unregisterObject(MXObject *obj) {
        if (!obj) return;
        std::lock_guard<std::mutex> lock(mtx);
        objects.erase(obj);
    }

    void Allocator::dump_stats() {
        std::lock_guard<std::mutex> lock(mtx);
        printf("Live objects: %zu\n", objects.size());
        for (MXObject *obj : objects) {
            const char *type = obj ? obj->get_type_name().c_str() : "<null>";
            printf("  %p (%s)\n", (void *) obj, type);
        }
    }

}// namespace mxs_runtime

extern "C" MXS_API void mxs_allocator_dump_stats() {
    mxs_runtime::MX_ALLOCATOR.dump_stats();
}
