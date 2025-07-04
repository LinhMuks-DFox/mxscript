#include "container.hpp"
#include "allocator.hpp"

namespace mxs_runtime {

    MXContainer::MXContainer(const MXTypeInfo *info, bool is_static)
        : MXObject(info, is_static) {}

}
