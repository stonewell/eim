#pragma once

#include <stdint.h>
#include <string>
#include <unordered_map>
#include <memory>
#include <map>

#pragma pack(push)
#pragma pack(1)

typedef union __key_binding {
    struct {
        union {
            struct {
                bool ctrl:1;
                bool alt:1;
                bool shift:1;
                bool super:1;
            } v;
            uint8_t m;
        } modifier;
        uint8_t keyval;
    } key_data;
    uint16_t v;
} key_binding_u;

#pragma pack(pop)

key_binding_u from(const char * data, size_t len);
key_binding_u from(int keyval, int modifier);

struct __key_map;
using key_map_ptr = std::shared_ptr<struct __key_map>;
using key_map_ptr_map = std::map<uint16_t, key_map_ptr>;

typedef struct __key_map {
    key_map_ptr_map sub_key_map;
    std::string command;
} key_map_s;
