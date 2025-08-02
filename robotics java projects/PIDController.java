import java.util.*;

/**
 * PID Controller Implementation for Robotics
 * Demonstrates Proportional-Integral-Derivative control for precise motor control
 * Essential for robotics applications requiring accurate positioning and movement
 */
public class PIDController {
    private double kp, ki, kd; //PID constants
    private double previousError = 0;
    private double integral = 0;
    private double setpoint = 0;
    private double outputMin = -100, outputMax = 100;
    private long lastTime = 0;
    
    //Constructor
    public PIDController(double kp, double ki, double kd) {
        this.kp = kp;
        this.ki = ki;
        this.kd = kd;
        this.lastTime = System.currentTimeMillis();
    }
    
    /**
     * Calculate PID output based on current value
     * @param currentValue Current measured value
     * @return Control output
     */
    public double calculate(double currentValue) {
        long currentTime = System.currentTimeMillis();
        double deltaTime = (currentTime - lastTime) / 1000.0; //Convert to seconds
        
        if (deltaTime <= 0) deltaTime = 0.001; //Prevent division by zero
        
        double error = setpoint - currentValue;
        
        //Proportional term
        double proportional = kp * error;
        
        //Integral term
        integral += error * deltaTime;
        double integralTerm = ki * integral;
        
        //Derivative term
        double derivative = (error - previousError) / deltaTime;
        double derivativeTerm = kd * derivative;
        
        //Calculate total output
        double output = proportional + integralTerm + derivativeTerm;
        
        //Apply output limits
        output = Math.max(outputMin, Math.min(outputMax, output));
        
        //Update for next iteration
        previousError = error;
        lastTime = currentTime;
        
        return output;
    }
    
    /**
     * Set the target setpoint
     */
    public void setSetpoint(double setpoint) {
        this.setpoint = setpoint;
    }
    
    /**
     * Set output limits
     */
    public void setOutputLimits(double min, double max) {
        this.outputMin = min;
        this.outputMax = max;
    }
    
    /**
     * Reset the controller (clear integral and previous error)
     */
    public void reset() {
        integral = 0;
        previousError = 0;
        lastTime = System.currentTimeMillis();
    }
    
    /**
     * Get current PID parameters
     */
    public double[] getPIDParameters() {
        return new double[]{kp, ki, kd};
    }
    
    /**
     * Set new PID parameters
     */
    public void setPIDParameters(double kp, double ki, double kd) {
        this.kp = kp;
        this.ki = ki;
        this.kd = kd;
    }
    
    /**
     * Auto-tune PID parameters using Ziegler-Nichols method (simplified)
     */
    public void autoTune(MotorSimulator motor, double targetValue) {
        System.out.println("Starting PID Auto-Tuning (Simplified Ziegler-Nichols)...");
        
        // Step 1: Find critical gain (Ku) where system oscillates
        double ku = findCriticalGain(motor, targetValue);
        
        if (ku > 0) {
            // Step 2: Calculate PID parameters based on Ziegler-Nichols
            this.kp = 0.6 * ku;
            this.ki = 2 * kp / 1.0; // Assuming Tu = 1.0 for simplification
            this.kd = kp * 1.0 / 8;
            
            System.out.printf("Auto-tuned parameters: Kp=%.3f, Ki=%.3f, Kd=%.3f%n", kp, ki, kd);
        } else {
            System.out.println("Could not find critical gain, using default values.");
            this.kp = 1.0;
            this.ki = 0.1;
            this.kd = 0.05;
        }
    }
    
    private double findCriticalGain(MotorSimulator motor, double targetValue) {
        //Simplified critical gain finding
        //In practice, this would involve more sophisticated oscillation detection
        double testGain = 0.1;
        
        while (testGain < 10.0) {
            PIDController testController = new PIDController(testGain, 0, 0);
            testController.setSetpoint(targetValue);
            
            //Test for oscillation
            if (testForOscillation(testController, motor, targetValue)) {
                return testGain;
            }
            
            testGain += 0.1;
        }
        
        return -1; //No critical gain found
    }
    
    private boolean testForOscillation(PIDController controller, MotorSimulator motor, double target) {
        //Simplified oscillation test
        double[] values = new double[20];
        motor.reset();
        
        for (int i = 0; i < 20; i++) {
            double output = controller.calculate(motor.getCurrentPosition());
            motor.update(output);
            values[i] = motor.getCurrentPosition();
            
            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        //Check for oscillation pattern (simplified)
        double variance = calculateVariance(values);
        return variance > 0.1; //Threshold for oscillation detection
    }
    
    private double calculateVariance(double[] values) {
        double mean = Arrays.stream(values).average().orElse(0.0);
        double variance = Arrays.stream(values)
                .map(x -> Math.pow(x - mean, 2))
                .average().orElse(0.0);
        return variance;
    }
    
    /**
     * Motor Simulator for testing PID controller
     */
    static class MotorSimulator {
        private double position = 0;
        private double velocity = 0;
        private double acceleration = 0;
        private final double friction = 0.1;
        private final double maxAcceleration = 5.0;
        
        public void update(double controlSignal) {
            //Simulate motor dynamics
            acceleration = Math.max(-maxAcceleration, 
                          Math.min(maxAcceleration, controlSignal * 0.1));
            
            velocity += acceleration * 0.02; //dt = 0.02s
            velocity *= (1 - friction); //Apply friction
            
            position += velocity * 0.02;
        }
        
        public double getCurrentPosition() {
            return position;
        }
        
        public void reset() {
            position = 0;
            velocity = 0;
            acceleration = 0;
        }
        
        public double[] getState() {
            return new double[]{position, velocity, acceleration};
        }
    }
    
    /**
     * Demonstration and testing
     */
    public static void main(String[] args) {
        System.out.println("PID Controller for Robotics - Demonstration\n");
        
        //Test 1: Basic PID control
        System.out.println("Test 1: Basic PID Control");
        System.out.println("--------------------------");
        
        PIDController pid = new PIDController(2.0, 0.1, 0.05);
        MotorSimulator motor = new MotorSimulator();
        
        pid.setSetpoint(10.0); //Target position
        pid.setOutputLimits(-50, 50);
        
        System.out.println("Target: 10.0 units");
        System.out.println("Time\tPos\tVel\tAcc\tError\tP\tI\tD\tOutput");
        
        for (int i = 0; i < 51; i++) {
            double currentPos = motor.getCurrentPosition();
            double error = pid.setpoint - currentPos;
            
            double output = pid.calculate(currentPos);
            motor.update(output);
            
            
            if (i % 10 == 0) {
                System.out.printf("Time: %.2fs, Position: %.2f, Error: %.2f%n", 
                    i * 0.02, currentPos, error);
            }
            
            //Detailed output every few steps
            if (i < 50 && i % 1 == 0) {
                double proportional = pid.kp * error;
                double integralTerm = pid.ki * pid.integral;
                double derivative = pid.kd * (error - pid.previousError) / 0.02;
                
                System.out.printf("[%d] SP:%.2f CV:%.2f E:%.2f P:%.2f I:%.2f D:%.2f O:%.2f%n",
                    i, pid.setpoint, currentPos, error, proportional, integralTerm, derivative, output);
            }
            
            try {
                Thread.sleep(20); //20ms delay
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        System.out.printf("\nFinal Position: %.2f (Target: %.2f)\n\n", 
            motor.getCurrentPosition(), pid.setpoint);
        
        //Test 2: Auto-tuning demonstration
        System.out.println("Test 2: Auto-Tuning Demonstration");
        System.out.println("-----------------------------------");
        
        PIDController autoPID = new PIDController(1.0, 0.0, 0.0);
        MotorSimulator autoMotor = new MotorSimulator();
        
        autoPID.autoTune(autoMotor, 8.0);
        
        System.out.println("\nTesting auto-tuned parameters:");
        autoPID.setSetpoint(8.0);
        autoMotor.reset();
        
        for (int i = 0; i <= 25; i += 5) {
            double output = autoPID.calculate(autoMotor.getCurrentPosition());
            autoMotor.update(output);
            System.out.printf("Step %d: Position %.2f%n", i, autoMotor.getCurrentPosition());
            
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        //Test 3: Comparing different PID configurations
        System.out.println("\n\nTest 3: Comparing PID Configurations");
        System.out.println("-------------------------------------\n");
        
        double[][] configs = {
            {1.0, 0.0, 0.0},   //P-only
            {1.0, 0.1, 0.0},   //PI
            {1.0, 0.0, 0.05},  //PD
            {1.0, 0.1, 0.05}   //Full PID
        };
        
        String[] names = {"P-only Controller", "PI Controller", "PD Controller", "Full PID Controller"};
        
        for (int config = 0; config < configs.length; config++) {
            PIDController testPID = new PIDController(configs[config][0], configs[config][1], configs[config][2]);
            MotorSimulator testMotor = new MotorSimulator();
            
            testPID.setSetpoint(8.0);
            
            //Run for 100 steps
            for (int i = 0; i < 100; i++) {
                double output = testPID.calculate(testMotor.getCurrentPosition());
                testMotor.update(output);
                
                try {
                    Thread.sleep(5);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
            
            double finalPos = testMotor.getCurrentPosition();
            double finalError = 8.0 - finalPos;
            
            System.out.printf("%s (P=%.1f, I=%.1f, D=%.2f):%n", 
                names[config], configs[config][0], configs[config][1], configs[config][2]);
            System.out.printf("Final position: %.2f (Error: %.2f)%n%n", finalPos, finalError);
        }
        
        System.out.println("=" .repeat(50));
        System.out.println("PID Controller Demo Complete!");
        System.out.println("This demonstrates essential control theory for robotics.");
    }
}