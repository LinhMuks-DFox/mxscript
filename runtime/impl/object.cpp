#include "include/object.hpp"

namespace mxs_runtime {
    MXObject::MXObject() { }
    MXObject::~MXObject() { }
    std::size_t MXObject::decrease_ref() {
        this->ref_cnt--;
        if (this->ref_cnt == 0) { delete this; }
        return this->ref_cnt;
    }
    std::size_t MXObject::increase_ref() {
        this->ref_cnt++;
        return this->ref_cnt;
    }
}
