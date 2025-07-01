#ifndef ARC_RUNTIME_H
#define ARC_RUNTIME_H

#include <stdlib.h>

void* arc_alloc(size_t size);
void* arc_retain(void* ptr);
void arc_release(void* ptr);

#endif /* ARC_RUNTIME_H */
