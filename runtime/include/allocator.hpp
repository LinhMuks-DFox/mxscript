#pragma once
#ifndef MXSCRIPT_ALLOCATOR_HPP
#define MXSCRIPT_ALLOCATOR_HPP

#include "macro.hpp"
#include <unordered_set>
#include <mutex>

namespace mxs_runtime {
    class MXObject; // forward declaration

    class Allocator {
    private:
        std::unordered_set<MXObject*> objects;
        std::mutex mtx;
    public:
        void registerObject(MXObject* obj);
        void unregisterObject(MXObject* obj);
    };

    MXS_API extern Allocator& MX_ALLOCATOR;
}

#endif // MXSCRIPT_ALLOCATOR_HPP
