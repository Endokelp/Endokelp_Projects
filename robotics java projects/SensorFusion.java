import java.util.*;
import java.util.concurrent.*;

/**
 * Sensor Fusion System for Robotics
 * Demonstrates combining multiple sensor inputs for accurate robot positioning
 * Uses Kalman filtering and weighted sensor fusion techniques
 */
public class SensorFusion {
    
    // Sensor data structures
    static class SensorReading {
        double x, y, z;
        double confidence;
        long timestamp;
        String sensorType;
        
        public SensorReading(double x, double y, double z, double confidence, String sensorType) {
            this.x = x;
            this.y = y;
            this.z = z;
            this.confidence = confidence;
            this.sensorType = sensorType;
            this.timestamp = System.currentTimeMillis();
        }
        
        @Override
        public String toString() {
            return String.format("%s: (%.2f, %.2f, %.2f) conf=%.2f", 
                sensorType, x, y, z, confidence);
        }
    }
    
    // Kalman Filter for position estimation
    static class KalmanFilter {
        private double[][] state;      // [x, y, vx, vy]
        private double[][] covariance; // Error covariance matrix
        private double[][] processNoise;
        private double[][] measurementNoise;
        private double dt = 0.1; // Time step
        
        public KalmanFilter() {
            // Initialize 4x4 matrices for 2D position and velocity
            state = new double[4][1];
            covariance = createIdentityMatrix(4, 1.0);
            
            // Process noise (how much we trust our model)
            processNoise = createIdentityMatrix(4, 0.1);
            
            // Measurement noise (how much we trust sensors)
            measurementNoise = createIdentityMatrix(2, 0.5);
        }
        
        public void predict() {
            // State transition matrix (constant velocity model)
            double[][] F = {
                {1, 0, dt, 0},
                {0, 1, 0, dt},
                {0, 0, 1, 0},
                {0, 0, 0, 1}
            };
            
            // Predict state: x = F * x
            state = matrixMultiply(F, state);
            
            // Predict covariance: P = F * P * F^T + Q
            double[][] Ft = transpose(F);
            covariance = matrixAdd(matrixMultiply(matrixMultiply(F, covariance), Ft), processNoise);
        }
        
        public void update(double measX, double measY, double confidence) {
            // Measurement matrix (we observe position, not velocity)
            double[][] H = {
                {1, 0, 0, 0},
                {0, 1, 0, 0}
            };
            
            // Measurement vector
            double[][] z = {{measX}, {measY}};
            
            // Innovation (measurement - prediction)
            double[][] Hx = matrixMultiply(H, state);
            double[][] y = matrixSubtract(z, Hx);
            
            // Innovation covariance
            double[][] Ht = transpose(H);
            double[][] S = matrixAdd(matrixMultiply(matrixMultiply(H, covariance), Ht), 
                                   scaleMatrix(measurementNoise, 1.0 / confidence));
            
            // Kalman gain
            double[][] K = matrixMultiply(matrixMultiply(covariance, Ht), matrixInverse(S));
            
            // Update state: x = x + K * y
            state = matrixAdd(state, matrixMultiply(K, y));
            
            // Update covariance: P = (I - K * H) * P
            double[][] I = createIdentityMatrix(4, 1.0);
            double[][] KH = matrixMultiply(K, H);
            covariance = matrixMultiply(matrixSubtract(I, KH), covariance);
        }
        
        public double[] getPosition() {
            return new double[]{state[0][0], state[1][0]};
        }
        
        public double[] getVelocity() {
            return new double[]{state[2][0], state[3][0]};
        }
        
        // Matrix operations (simplified implementations)
        private double[][] createIdentityMatrix(int size, double scale) {
            double[][] matrix = new double[size][size];
            for (int i = 0; i < size; i++) {
                matrix[i][i] = scale;
            }
            return matrix;
        }
        
        private double[][] matrixMultiply(double[][] a, double[][] b) {
            int rows = a.length;
            int cols = b[0].length;
            int common = b.length;
            double[][] result = new double[rows][cols];
            
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    for (int k = 0; k < common; k++) {
                        result[i][j] += a[i][k] * b[k][j];
                    }
                }
            }
            return result;
        }
        
        private double[][] matrixAdd(double[][] a, double[][] b) {
            int rows = a.length;
            int cols = a[0].length;
            double[][] result = new double[rows][cols];
            
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    result[i][j] = a[i][j] + b[i][j];
                }
            }
            return result;
        }
        
        private double[][] matrixSubtract(double[][] a, double[][] b) {
            int rows = a.length;
            int cols = a[0].length;
            double[][] result = new double[rows][cols];
            
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    result[i][j] = a[i][j] - b[i][j];
                }
            }
            return result;
        }
        
        private double[][] transpose(double[][] matrix) {
            int rows = matrix.length;
            int cols = matrix[0].length;
            double[][] result = new double[cols][rows];
            
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    result[j][i] = matrix[i][j];
                }
            }
            return result;
        }
        
        private double[][] scaleMatrix(double[][] matrix, double scale) {
            int rows = matrix.length;
            int cols = matrix[0].length;
            double[][] result = new double[rows][cols];
            
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    result[i][j] = matrix[i][j] * scale;
                }
            }
            return result;
        }
        
        private double[][] matrixInverse(double[][] matrix) {
            // Simplified 2x2 matrix inverse
            if (matrix.length == 2 && matrix[0].length == 2) {
                double det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0];
                if (Math.abs(det) < 1e-10) {
                    return createIdentityMatrix(2, 1.0); // Return identity if singular
                }
                
                double[][] result = new double[2][2];
                result[0][0] = matrix[1][1] / det;
                result[0][1] = -matrix[0][1] / det;
                result[1][0] = -matrix[1][0] / det;
                result[1][1] = matrix[0][0] / det;
                return result;
            }
            return createIdentityMatrix(matrix.length, 1.0); // Fallback
        }
    }
    
    // Sensor simulators
    static class GPSSensor {
        private Random random = new Random();
        private double trueX, trueY;
        
        public GPSSensor(double trueX, double trueY) {
            this.trueX = trueX;
            this.trueY = trueY;
        }
        
        public SensorReading getReading() {
            // GPS has good accuracy but can have occasional large errors
            double noise = random.nextGaussian() * 0.5;
            double x = trueX + noise;
            double y = trueY + noise;
            
            // Occasionally simulate GPS dropout or large error
            double confidence = random.nextDouble() > 0.1 ? 0.9 : 0.3;
            if (confidence < 0.5) {
                x += random.nextGaussian() * 5.0; // Large error
                y += random.nextGaussian() * 5.0;
            }
            
            return new SensorReading(x, y, 0, confidence, "GPS");
        }
        
        public void updateTruePosition(double x, double y) {
            this.trueX = x;
            this.trueY = y;
        }
    }
    
    static class IMUSensor {
        private Random random = new Random();
        private double trueX, trueY;
        private double driftX = 0, driftY = 0;
        
        public IMUSensor(double trueX, double trueY) {
            this.trueX = trueX;
            this.trueY = trueY;
        }
        
        public SensorReading getReading() {
            // IMU has consistent readings but accumulates drift over time
            driftX += random.nextGaussian() * 0.01;
            driftY += random.nextGaussian() * 0.01;
            
            double noise = random.nextGaussian() * 0.2;
            double x = trueX + driftX + noise;
            double y = trueY + driftY + noise;
            
            return new SensorReading(x, y, 0, 0.8, "IMU");
        }
        
        public void updateTruePosition(double x, double y) {
            this.trueX = x;
            this.trueY = y;
        }
        
        public void resetDrift() {
            driftX = 0;
            driftY = 0;
        }
    }
    
    static class LidarSensor {
        private Random random = new Random();
        private double trueX, trueY;
        
        public LidarSensor(double trueX, double trueY) {
            this.trueX = trueX;
            this.trueY = trueY;
        }
        
        public SensorReading getReading() {
            // Lidar is very accurate but can be affected by obstacles
            double noise = random.nextGaussian() * 0.1;
            double x = trueX + noise;
            double y = trueY + noise;
            
            // Occasionally simulate obstacle interference
            double confidence = random.nextDouble() > 0.05 ? 0.95 : 0.4;
            
            return new SensorReading(x, y, 0, confidence, "Lidar");
        }
        
        public void updateTruePosition(double x, double y) {
            this.trueX = x;
            this.trueY = y;
        }
    }
    
    // Main sensor fusion class
    private KalmanFilter kalmanFilter;
    private GPSSensor gps;
    private IMUSensor imu;
    private LidarSensor lidar;
    private List<SensorReading> recentReadings;
    private final int maxRecentReadings = 10;
    
    public SensorFusion(double initialX, double initialY) {
        kalmanFilter = new KalmanFilter();
        gps = new GPSSensor(initialX, initialY);
        imu = new IMUSensor(initialX, initialY);
        lidar = new LidarSensor(initialX, initialY);
        recentReadings = new ArrayList<>();
    }
    
    public double[] getFusedPosition() {
        // Get readings from all sensors
        SensorReading gpsReading = gps.getReading();
        SensorReading imuReading = imu.getReading();
        SensorReading lidarReading = lidar.getReading();
        
        // Store recent readings
        recentReadings.add(gpsReading);
        recentReadings.add(imuReading);
        recentReadings.add(lidarReading);
        
        if (recentReadings.size() > maxRecentReadings) {
            recentReadings.subList(0, recentReadings.size() - maxRecentReadings).clear();
        }
        
        // Method 1: Weighted average fusion
        double[] weightedPos = weightedAverageFusion(Arrays.asList(gpsReading, imuReading, lidarReading));
        
        // Method 2: Kalman filter fusion
        kalmanFilter.predict();
        
        // Update with highest confidence sensor first
        List<SensorReading> sortedReadings = Arrays.asList(gpsReading, imuReading, lidarReading);
        sortedReadings.sort((a, b) -> Double.compare(b.confidence, a.confidence));
        
        for (SensorReading reading : sortedReadings) {
            if (reading.confidence > 0.5) { // Only use reliable readings
                kalmanFilter.update(reading.x, reading.y, reading.confidence);
            }
        }
        
        double[] kalmanPos = kalmanFilter.getPosition();
        
        // Combine both methods for final result
        double[] finalPos = new double[2];
        finalPos[0] = 0.6 * kalmanPos[0] + 0.4 * weightedPos[0];
        finalPos[1] = 0.6 * kalmanPos[1] + 0.4 * weightedPos[1];
        
        return finalPos;
    }
    
    private double[] weightedAverageFusion(List<SensorReading> readings) {
        double totalWeight = 0;
        double weightedX = 0;
        double weightedY = 0;
        
        for (SensorReading reading : readings) {
            double weight = reading.confidence;
            
            // Apply sensor-specific weighting
            switch (reading.sensorType) {
                case "GPS":
                    weight *= 1.0; // GPS baseline
                    break;
                case "IMU":
                    weight *= 0.8; // IMU slightly less trusted due to drift
                    break;
                case "Lidar":
                    weight *= 1.2; // Lidar most trusted when available
                    break;
            }
            
            weightedX += reading.x * weight;
            weightedY += reading.y * weight;
            totalWeight += weight;
        }
        
        if (totalWeight > 0) {
            return new double[]{weightedX / totalWeight, weightedY / totalWeight};
        } else {
            return new double[]{0, 0};
        }
    }
    
    public void updateTruePosition(double x, double y) {
        gps.updateTruePosition(x, y);
        imu.updateTruePosition(x, y);
        lidar.updateTruePosition(x, y);
    }
    
    public void printSensorStatus() {
        System.out.println("Recent Sensor Readings:");
        for (int i = Math.max(0, recentReadings.size() - 3); i < recentReadings.size(); i++) {
            System.out.println("  " + recentReadings.get(i));
        }
        
        double[] pos = kalmanFilter.getPosition();
        double[] vel = kalmanFilter.getVelocity();
        System.out.printf("Kalman State - Pos: (%.2f, %.2f), Vel: (%.2f, %.2f)%n", 
            pos[0], pos[1], vel[0], vel[1]);
    }
    
    /**
     * Demonstration and testing
     */
    public static void main(String[] args) {
        System.out.println("Sensor Fusion System for Robotics - Demonstration\n");
        
        // Initialize sensor fusion system
        SensorFusion fusion = new SensorFusion(0.0, 0.0);
        
        System.out.println("Simulating robot movement with sensor fusion...");
        System.out.println("True Position -> Fused Position (Error)\n");
        
        // Simulate robot moving in a square pattern
        double[][] waypoints = {
            {0, 0}, {5, 0}, {5, 5}, {0, 5}, {0, 0},
            {2, 2}, {8, 2}, {8, 8}, {2, 8}, {2, 2}
        };
        
        for (int i = 0; i < waypoints.length; i++) {
            double trueX = waypoints[i][0];
            double trueY = waypoints[i][1];
            
            // Update true position for sensors
            fusion.updateTruePosition(trueX, trueY);
            
            // Get fused position estimate
            double[] fusedPos = fusion.getFusedPosition();
            
            // Calculate error
            double error = Math.sqrt(Math.pow(fusedPos[0] - trueX, 2) + Math.pow(fusedPos[1] - trueY, 2));
            
            System.out.printf("Step %2d: True(%.1f, %.1f) -> Fused(%.2f, %.2f) Error: %.3f%n", 
                i + 1, trueX, trueY, fusedPos[0], fusedPos[1], error);
            
            // Print detailed sensor information every few steps
            if (i % 3 == 0) {
                System.out.println();
                fusion.printSensorStatus();
                System.out.println();
            }
            
            // Simulate time delay
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        System.out.println("\n" + "=".repeat(60));
        
        // Test sensor reliability over time
        System.out.println("\nTesting sensor fusion accuracy over extended period...");
        
        double totalError = 0;
        int testSteps = 50;
        
        for (int i = 0; i < testSteps; i++) {
            // Simulate continuous movement
            double t = i * 0.1;
            double trueX = 5 * Math.cos(t);
            double trueY = 5 * Math.sin(t);
            
            fusion.updateTruePosition(trueX, trueY);
            double[] fusedPos = fusion.getFusedPosition();
            
            double error = Math.sqrt(Math.pow(fusedPos[0] - trueX, 2) + Math.pow(fusedPos[1] - trueY, 2));
            totalError += error;
            
            if (i % 10 == 0) {
                System.out.printf("t=%.1fs: True(%.2f, %.2f) Fused(%.2f, %.2f) Error: %.3f%n", 
                    t, trueX, trueY, fusedPos[0], fusedPos[1], error);
            }
            
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        double averageError = totalError / testSteps;
        System.out.printf("\nAverage positioning error: %.3f units%n", averageError);
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Sensor Fusion Demo Complete!");
        System.out.println("This demonstrates multi-sensor integration for robotics.");
        System.out.println("\nKey Features Demonstrated:");
        System.out.println("- Kalman filtering for state estimation");
        System.out.println("- Weighted sensor fusion based on confidence");
        System.out.println("- Handling sensor noise and dropouts");
        System.out.println("- Real-time position estimation");
    }
}