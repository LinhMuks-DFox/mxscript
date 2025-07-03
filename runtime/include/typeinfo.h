#pragma once
#ifndef MXS_TYPEINFO_H
#define MXS_TYPEINFO_H

namespace mxs_runtime {
class MXObject;

struct MXTypeInfo {
    const char* name;
    const MXTypeInfo* parent;
    // Binary operation vtable entries
    MXObject* (*op_add)(MXObject*, MXObject*);
    MXObject* (*op_sub)(MXObject*, MXObject*);
    MXObject* (*op_eq)(MXObject*, MXObject*);
};

}

#endif // MXS_TYPEINFO_H
