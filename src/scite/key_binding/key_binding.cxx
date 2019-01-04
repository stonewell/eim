#include <string.h>
#include <map>

#include "Scintilla.h"
#include "KeyMap.h"

#include "key_binding.h"


static void update_value(key_binding_u & k, const char * v, size_t len) {
    if (!strncasecmp("ctrl", v, len) && len == strlen("ctrl")) {
        k.key_data.modifier.v.ctrl = true;
    } else if (!strncasecmp("alt", v, len) && len == strlen("alt")) {
        k.key_data.modifier.v.alt = true;
    } else if (!strncasecmp("shift", v, len) && len == strlen("shift")) {
        k.key_data.modifier.v.shift = true;
    } else if (!strncasecmp("super", v, len) && len == strlen("super")) {
        k.key_data.modifier.v.super = true;
    } else {
        k.key_data.keyval = *v;
    }
}

key_binding_u from(const char * data, size_t len) {
    const char * p = data, * p_end = p + len, * p_begin = p;
    key_binding_u k{};

    while(p < p_end) {
        if (*p == '+') {
            update_value(k, p_begin, p - p_begin);
            p_begin = p;
            p_begin++;
        }

        p++;
    }

    if (p_begin < p) {
        update_value(k, p_begin, p - p_begin);
    }

    return k;
}

key_binding_u from(int keyval, int modifier) {
    key_binding_u k{};

    k.key_data.keyval = keyval;
    k.key_data.modifier.v.ctrl = (modifier & SCI_CTRL) == SCI_CTRL;
    k.key_data.modifier.v.alt = (modifier & SCI_ALT) == SCI_ALT;
    k.key_data.modifier.v.shift = (modifier & SCI_SHIFT) == SCI_SHIFT;
    k.key_data.modifier.v.super = (modifier & SCI_SUPER) == SCI_SUPER;

    return k;
}
