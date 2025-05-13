#pragma once

#include <sstream>

#define RETURN_ON_ERROR(x) { auto r = (x); if (r) { return r; }}

template<typename T>
std::string to_string(T v)
{
  std::ostringstream ss;

  ss << v;

  return ss.str();
}
