# MXScript Fast Path FFI Mapping

This document defines the authoritative mapping between MXScript built-in operations and the high performance "Fast Path" C API functions provided by the runtime. When the compiler can statically determine operand types it will call these C functions directly, bypassing dynamic dispatch.

Each entry lists the MXScript level operation, the operand types required for fast dispatch, the `extern "C"` function name to invoke, and the underlying C++ runtime method that implements the logic.

## Binary Arithmetic Operators

| MXScript Operation | Static Types | Fast Path C-API Function | Runtime C++ Method |
|--------------------|--------------|-------------------------|--------------------|
| `+` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_add_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_add_integer` |
| `+` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_add_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_add_float` |
| `+` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_add_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_add_integer` |
| `+` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_add_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_add_float` |
| `-` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_sub_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_sub_integer` |
| `-` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_sub_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_sub_float` |
| `-` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_sub_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_sub_integer` |
| `-` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_sub_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_sub_float` |
| `*` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_mul_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_mul_integer` |
| `*` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_mul_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_mul_float` |
| `*` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_mul_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_mul_integer` |
| `*` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_mul_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_mul_float` |
| `/` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_div_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_div_integer` |
| `/` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_div_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_div_float` |
| `/` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_div_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_div_integer` |
| `/` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_div_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_div_float` |
| `%` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_mod_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_mod_integer` |
| `%` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_mod_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_mod_float` |
| `%` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_mod_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_mod_integer` |
| `%` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_mod_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_mod_float` |
| `+` | `string, string` | `extern "C" mxs_runtime::MXObject* mxs_string_add_string(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::string_add_string` |

## Binary Comparison Operators

| MXScript Operation | Static Types | Fast Path C-API Function | Runtime C++ Method |
|--------------------|--------------|-------------------------|--------------------|
| `==` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_eq_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_eq_integer` |
| `==` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_eq_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_eq_float` |
| `==` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_eq_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_eq_integer` |
| `==` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_eq_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_eq_float` |
| `!=` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_ne_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_ne_integer` |
| `!=` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_ne_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_ne_float` |
| `!=` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_ne_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_ne_integer` |
| `!=` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_ne_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_ne_float` |
| `>` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_gt_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_gt_integer` |
| `>` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_gt_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_gt_float` |
| `>` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_gt_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_gt_integer` |
| `>` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_gt_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_gt_float` |
| `<` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_lt_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_lt_integer` |
| `<` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_lt_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_lt_float` |
| `<` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_lt_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_lt_integer` |
| `<` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_lt_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_lt_float` |
| `>=` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_ge_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_ge_integer` |
| `>=` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_ge_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_ge_float` |
| `>=` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_ge_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_ge_integer` |
| `>=` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_ge_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_ge_float` |
| `<=` | `int, int` | `extern "C" mxs_runtime::MXObject* mxs_integer_le_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_le_integer` |
| `<=` | `int, float` | `extern "C" mxs_runtime::MXObject* mxs_integer_le_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::integer_le_float` |
| `<=` | `float, int` | `extern "C" mxs_runtime::MXObject* mxs_float_le_integer(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_le_integer` |
| `<=` | `float, float` | `extern "C" mxs_runtime::MXObject* mxs_float_le_float(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::float_le_float` |
| `==` | `string, string` | `extern "C" mxs_runtime::MXObject* mxs_string_eq_string(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::string_eq_string` |
| `!=` | `string, string` | `extern "C" mxs_runtime::MXObject* mxs_string_ne_string(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::string_ne_string` |
| `<` | `string, string` | `extern "C" mxs_runtime::MXObject* mxs_string_lt_string(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::string_lt_string` |
| `<=` | `string, string` | `extern "C" mxs_runtime::MXObject* mxs_string_le_string(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::string_le_string` |
| `>` | `string, string` | `extern "C" mxs_runtime::MXObject* mxs_string_gt_string(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::string_gt_string` |
| `>=` | `string, string` | `extern "C" mxs_runtime::MXObject* mxs_string_ge_string(mxs_runtime::MXObject* left, mxs_runtime::MXObject* right);` | `mxs_runtime::string_ge_string` |

## Unary Operators

| MXScript Operation | Static Types | Fast Path C-API Function | Runtime C++ Method |
|--------------------|--------------|-------------------------|--------------------|
| `- (negation)` | `int` | `extern "C" mxs_runtime::MXObject* mxs_integer_neg(mxs_runtime::MXObject* value);` | `mxs_runtime::integer_neg` |
| `- (negation)` | `float` | `extern "C" mxs_runtime::MXObject* mxs_float_neg(mxs_runtime::MXObject* value);` | `mxs_runtime::float_neg` |
| `+ (unary plus)` | `int` | `extern "C" mxs_runtime::MXObject* mxs_integer_pos(mxs_runtime::MXObject* value);` | `mxs_runtime::integer_pos` |
| `+ (unary plus)` | `float` | `extern "C" mxs_runtime::MXObject* mxs_float_pos(mxs_runtime::MXObject* value);` | `mxs_runtime::float_pos` |
| `~` | `int` | `extern "C" mxs_runtime::MXObject* mxs_integer_invert(mxs_runtime::MXObject* value);` | `mxs_runtime::integer_invert` |
| `not` | `bool` | `extern "C" mxs_runtime::MXObject* mxs_boolean_not(mxs_runtime::MXObject* value);` | `mxs_runtime::boolean_not` |

## Type Casting

| MXScript Operation | Static Types | Fast Path C-API Function | Runtime C++ Method |
|--------------------|--------------|-------------------------|--------------------|
| `cast(String, int)` | `int` | `extern "C" mxs_runtime::MXObject* mxs_string_from_integer(mxs_runtime::MXObject* int_obj);` | `mxs_runtime::mxs_string_from_integer` |
| `cast(Int, float)` | `float` | `extern "C" mxs_runtime::MXObject* mxs_integer_from_float(mxs_runtime::MXObject* float_obj);` | `mxs_runtime::integer_from_float` |
| `cast(Float, int)` | `int` | `extern "C" mxs_runtime::MXObject* mxs_float_from_integer(mxs_runtime::MXObject* int_obj);` | `mxs_runtime::float_from_integer` |
| `cast(String, float)` | `float` | `extern "C" mxs_runtime::MXObject* mxs_string_from_float(mxs_runtime::MXObject* float_obj);` | `mxs_runtime::string_from_float` |

## Container Methods

### List<T>

| MXScript Operation | Static Types | Fast Path C-API Function | Runtime C++ Method |
|--------------------|--------------|-------------------------|--------------------|
| `.append` | `List<T>, T` | `extern "C" mxs_runtime::MXObject* mxs_list_append(mxs_runtime::MXList* list, mxs_runtime::MXObject* value);` | `mxs_runtime::MXList::op_append` |
| `.pop` | `List<T>` | `extern "C" mxs_runtime::MXObject* mxs_list_pop(mxs_runtime::MXList* list);` | `mxs_runtime::MXList::pop` |
| `.extend` | `List<T>, List<T>` | `extern "C" mxs_runtime::MXObject* mxs_list_extend(mxs_runtime::MXList* list, mxs_runtime::MXList* other);` | `mxs_runtime::MXList::extend` |
| `.index_of` | `List<T>, T` | `extern "C" mxs_runtime::MXObject* mxs_list_index_of(mxs_runtime::MXList* list, mxs_runtime::MXObject* value);` | `mxs_runtime::MXList::index_of` |
| `.length` | `List<T>` | `extern "C" mxs_runtime::MXObject* mxs_list_length(mxs_runtime::MXList* list);` | `mxs_runtime::MXList::length` |
| `.insert` | `List<T>, int, T` | `extern "C" mxs_runtime::MXObject* mxs_list_insert(mxs_runtime::MXList* list, mxs_runtime::MXObject* index, mxs_runtime::MXObject* value);` | `mxs_runtime::MXList::insert` |
| `.remove` | `List<T>, T` | `extern "C" mxs_runtime::MXObject* mxs_list_remove(mxs_runtime::MXList* list, mxs_runtime::MXObject* value);` | `mxs_runtime::MXList::remove` |
| `.clear` | `List<T>` | `extern "C" mxs_runtime::MXObject* mxs_list_clear(mxs_runtime::MXList* list);` | `mxs_runtime::MXList::clear` |
| `[]` | `List<T>, int` | `extern "C" mxs_runtime::MXObject* mxs_list_getitem(mxs_runtime::MXObject* list, mxs_runtime::MXObject* index);` | `mxs_runtime::MXList::op_getitem` |
| `[]= ` | `List<T>, int, T` | `extern "C" mxs_runtime::MXObject* mxs_list_setitem(mxs_runtime::MXObject* list, mxs_runtime::MXObject* index, mxs_runtime::MXObject* value);` | `mxs_runtime::MXList::op_setitem` |
| `+` | `List<T>, List<T>` | `extern "C" mxs_runtime::MXObject* mxs_list_add(mxs_runtime::MXList* left, mxs_runtime::MXList* right);` | `mxs_runtime::MXList::op_add` |
| `*` | `List<T>, int` | `extern "C" mxs_runtime::MXObject* mxs_list_mul(mxs_runtime::MXList* list, mxs_runtime::MXObject* count);` | `mxs_runtime::MXList::op_mul` |

### Array<T>

| MXScript Operation | Static Types | Fast Path C-API Function | Runtime C++ Method |
|--------------------|--------------|-------------------------|--------------------|
| `.length` | `Array<T>` | `extern "C" mxs_runtime::MXObject* mxs_array_length(mxs_runtime::MXObject* array);` | `mxs_runtime::MXPODArray::length / MXBoxedArray::length` |
| `[]` | `Array<T>, int` | `extern "C" mxs_runtime::MXObject* mxs_array_getitem(mxs_runtime::MXObject* array, mxs_runtime::MXObject* index);` | `mxs_runtime::MXPODArray::op_getitem / MXBoxedArray::op_getitem` |
| `[]=` | `Array<T>, int, T` | `extern "C" mxs_runtime::MXObject* mxs_array_setitem(mxs_runtime::MXObject* array, mxs_runtime::MXObject* index, mxs_runtime::MXObject* value);` | `mxs_runtime::MXPODArray::op_setitem / MXBoxedArray::op_setitem` |

### Tuple

| MXScript Operation | Static Types | Fast Path C-API Function | Runtime C++ Method |
|--------------------|--------------|-------------------------|--------------------|
| `.length` | `Tuple` | `extern "C" mxs_runtime::MXObject* mxs_tuple_length(mxs_runtime::MXTuple* tuple);` | `mxs_runtime::MXTuple::length` |
| `+` | `Tuple, Tuple` | `extern "C" mxs_runtime::MXObject* mxs_tuple_add(mxs_runtime::MXTuple* left, mxs_runtime::MXTuple* right);` | `mxs_runtime::MXTuple::op_add` |
| `[]` | `Tuple, int` | `extern "C" mxs_runtime::MXObject* mxs_tuple_getitem(mxs_runtime::MXTuple* tuple, mxs_runtime::MXObject* index);` | `mxs_runtime::MXTuple::op_getitem` |

### Dict<K,V>

| MXScript Operation | Static Types | Fast Path C-API Function | Runtime C++ Method |
|--------------------|--------------|-------------------------|--------------------|
| `.get` | `Dict<K,V>, K, V|Nil` | `extern "C" mxs_runtime::MXObject* mxs_dict_get(mxs_runtime::MXDict* dict, mxs_runtime::MXObject* key, mxs_runtime::MXObject* default_val);` | `mxs_runtime::MXDict::get` |
| `.remove` | `Dict<K,V>, K` | `extern "C" mxs_runtime::MXObject* mxs_dict_remove(mxs_runtime::MXDict* dict, mxs_runtime::MXObject* key);` | `mxs_runtime::MXDict::remove` |
| `.keys` | `Dict<K,V>` | `extern "C" mxs_runtime::MXObject* mxs_dict_keys(mxs_runtime::MXDict* dict);` | `mxs_runtime::MXDict::keys` |
| `.values` | `Dict<K,V>` | `extern "C" mxs_runtime::MXObject* mxs_dict_values(mxs_runtime::MXDict* dict);` | `mxs_runtime::MXDict::values` |
| `.items` | `Dict<K,V>` | `extern "C" mxs_runtime::MXObject* mxs_dict_items(mxs_runtime::MXDict* dict);` | `mxs_runtime::MXDict::items` |
| `.length` | `Dict<K,V>` | `extern "C" mxs_runtime::MXObject* mxs_dict_length(mxs_runtime::MXDict* dict);` | `mxs_runtime::MXDict::length` |
| `.clear` | `Dict<K,V>` | `extern "C" mxs_runtime::MXObject* mxs_dict_clear(mxs_runtime::MXDict* dict);` | `mxs_runtime::MXDict::clear` |
| `[]` | `Dict<K,V>, K` | `extern "C" mxs_runtime::MXObject* mxs_dict_getitem(mxs_runtime::MXObject* dict, mxs_runtime::MXObject* key);` | `mxs_runtime::MXDict::op_getitem` |
| `[]=` | `Dict<K,V>, K, V` | `extern "C" mxs_runtime::MXObject* mxs_dict_setitem(mxs_runtime::MXObject* dict, mxs_runtime::MXObject* key, mxs_runtime::MXObject* value);` | `mxs_runtime::MXDict::op_setitem` |

---

This table acts as a strict contract between the compiler and the runtime. Whenever the compiler encounters one of these operations with the specified operand types, it can call the listed C API function directly. The runtime guarantees that each function forwards to the corresponding C++ method shown above.

