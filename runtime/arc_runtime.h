#include <stdint.h>
#include <stdlib.h>

typedef struct {
    int32_t ref_count;
    /* Object data follows */
} ArcObject;

static inline void arc_retain(ArcObject* obj) {
    if (obj) {
        ++obj->ref_count;
    }
}

void arc_release(ArcObject* obj);
