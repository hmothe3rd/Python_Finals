def SumOfNumbers(numbers):
    return sum(numbers)

def AverageOfNumbers(numbers):
    return sum(numbers) / len(numbers) if numbers else 0

def main():
    n = int(input("How many numbers do you want to enter: "))
    numbers = list(map(float, input(f"Enter the numbers (separated by space): ").split()))

    if len(numbers) != n:
        print(f"Error: You should enter exactly {n} numbers.")
        return

    sum_of_numbers = SumOfNumbers(numbers)
    average_of_numbers = AverageOfNumbers(numbers)

    print(f"The sum of the numbers is {sum_of_numbers}")
    print(f"The average is {average_of_numbers}")

if __name__ == "__main__":
    main()
