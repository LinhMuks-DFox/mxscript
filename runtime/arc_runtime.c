#include "arc_runtime.h"

void arc_release(ArcObject* obj) {
    if (obj && --obj->ref_count == 0) {
        free(obj);
    }
}
