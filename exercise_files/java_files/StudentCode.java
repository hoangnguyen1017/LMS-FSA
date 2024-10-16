import java.util.Scanner;

public class SquareCalculator {
    public static void main(String[] args) {
        // Create a Scanner object to read input
        Scanner scanner = new Scanner(System.in);

        // Prompt the user for an integer
        System.out.print("Enter an integer: ");
        int number = scanner.nextInt();

        // Calculate the square of the number
        int square = number * number;

        // Print the result
        System.out.println(square);

        // Close the scanner
        scanner.close();
    }
}