def main():
    print("--- Калькулятор ----")
    try:
        num1 = float(input("Введите первое число: "))
        operator = input("Введите операцию (+, -, *, /): ")
        num2 = float(input("Введите второе число: "))

        if operator == "+":
            print(f"Результат: {num1 + num2}")
        elif operator == "-":
            print(f"Результат: {num1 - num2}")
        elif operator == "*":
            print(f"Результат: {num1 * num2}")
        elif operator == "/":
            if num2 == 0:
                print("Ошибка: деление на ноль!")
            else:
                print(f"Результат: {num1 / num2}")
        else:
            print("Неверная операция!")
    except ValueError:
        print("Ошибка: вводите только числа!")

if __name__ == "__main__":
    main()
