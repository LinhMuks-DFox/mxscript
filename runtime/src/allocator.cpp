#include "allocator.hpp"
#include "object.hpp"

namespace mxs_runtime {

static Allocator allocator_instance;
MXS_API Allocator& MX_ALLOCATOR = allocator_instance;

void Allocator::registerObject(MXObject* obj) {
    if (!obj) return;
    std::lock_guard<std::mutex> lock(mtx);
    objects.insert(obj);
}

void Allocator::unregisterObject(MXObject* obj) {
    if (!obj) return;
    std::lock_guard<std::mutex> lock(mtx);
    objects.erase(obj);
}

} // namespace mxs_runtime
