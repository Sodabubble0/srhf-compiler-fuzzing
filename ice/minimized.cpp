template<class T> struct C { auto g() -> decltype([](auto&x){return x;}) { return [](auto&x){return x;}; } };
C<int> o; auto l = o.g();
