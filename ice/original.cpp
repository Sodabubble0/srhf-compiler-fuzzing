template <typename T>
class CrashingClass {
public:
    static const int value = 42;

    auto getLambda() -> decltype([](auto& x) { return x.value; }) {
        return [](auto& x) { return x.value; };
    }
};

int main() {
    CrashingClass<int> obj;
    auto lambda = obj.getLambda();
    lambda(obj); // This line would cause a compile-time error
    return 0;
}