#pragma once

#define RETURN_ON_ERROR(x) { auto r = (x); if (r) { return r; }}
