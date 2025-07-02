#include "arc_runtime.h"

void *arc_alloc(size_t size) {
  long long *base = (long long *)malloc(sizeof(long long) + size);
  if (!base) {
    return NULL;
  }
  *base = 1;
  return (void *)(base + 1);
}

void *arc_retain(void *ptr) {
  if (!ptr) {
    return NULL;
  }
  long long *base = ((long long *)ptr) - 1;
  ++(*base);
  return ptr;
}

void arc_release(void *ptr) {
  if (!ptr) {
    return;
  }
  long long *base = ((long long *)ptr) - 1;
  if (--(*base) == 0) {
    free(base);
  }
}
