package javaProjects;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.Collections;


public class UltimateEven_Odd {

    public static void main(String[] args) {
        Scanner user = new Scanner(System.in);
        ArrayList<Integer> numbers = new ArrayList<>();
        System.out.println("Ultimate Even or Odd");
        System.out.println("Number even or odd checker. Do you want to enter numbers? (Y/y for yes)");

        String input = user.nextLine();

        if (input.equalsIgnoreCase("yes") || input.equalsIgnoreCase("y")) {
            boolean repeat = true;

            while (repeat) {
                System.out.println("Enter a number: ");
                int number = user.nextInt();
                numbers.add(number); 
                user.nextLine();

                System.out.println("Do you want to Check another number? (Y/y for yes anything else to quit)");
                String input2 = user.nextLine();
                
                

     if (input2.equalsIgnoreCase("yes") || input2.equalsIgnoreCase("y")) {
                    continue;          
          }
     
     
          else {
                    repeat = false;
                }
     
            }
        
            System.out.println("\nResults:");
            for (int number : numbers) {
                System.out.println(number + ": " + checkNumber(number));
            }
            stats(numbers);
            System.out.println();
            System.out.println("thank you for using Ultimate even or odd");

            user.close();
        }       
        
        
        else {    
        
            System.out.println("Nevermind then");
        }
      
    }



    public static String checkNumber(int num) {
        if (num == 0) {
            return "Zero";
        } else if (num % 2 == 0) {
            return "Even";
        } else {
            return "Odd";
        }
    }

    public static void stats(ArrayList<Integer> num) {
        Scanner scan = new Scanner(System.in);
        System.out.print("Do you wanna see the stats of your list? \n");
        String input3 = scan.nextLine();

        if (input3.equalsIgnoreCase("yes") || input3.equalsIgnoreCase("y")) {
            // Sort the numbers
            Collections.sort(num);

            // Calculate mean
            double sum = 0;
            for (int n : num) {
                sum += n;
            }
            double mean = sum / num.size();

            // Calculate median
            double median;
            if (num.size() % 2 == 0) {
                median = (num.get(num.size() / 2 - 1) + num.get(num.size() / 2)) / 2.0;
            } else {
                median = num.get(num.size() / 2);
            }

            // Calculate mode using a simple loop
            int mode = num.get(0);
            int maxFreq = 0;


            
            for(int i = 0; i < num.size(); i++) {
            	int count = 1;
            	for(int j = i+1; j < num.size(); j++) {
            		if (num.get(i) == num.get(j)) {
            			count++;
            		}
            		else {
            			break;
            		}
            	}
            	if (count > maxFreq) {
            		maxFreq = count;
            		mode = num.get(i);
            	}
            }
            

            // If no duplicates, return the first element as mode
            if (maxFreq == 1) {
                mode = num.get(0);
            }

            // Calculate variance and standard deviation
            double variance = 0;
            for (int n : num) {
                variance += Math.pow(n - mean, 2);
            }
            variance /= num.size();
            double stdDev = Math.sqrt(variance);

            // Print the results
            System.out.println("\nStatistics:");
            System.out.println("Mean: " + mean);
            System.out.println("Median: " + median);
            System.out.println("Mode: " + mode);
            System.out.println("Standard Deviation: " + stdDev);
        }
    }

}
