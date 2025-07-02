#ifndef ARC_RUNTIME_H
#define ARC_RUNTIME_H

#include <stdlib.h>
#ifdef __cplusplus
extern "C" {
#endif

void *arc_alloc(size_t size);
void *arc_retain(void *ptr);
void arc_release(void *ptr);

#ifdef __cplusplus
}
#endif

#endif /* ARC_RUNTIME_H */
