import java.util.*;

/**
 * Robot Arm Kinematics for Robotics
 * Implements forward and inverse kinematics for robotic arm control
 * Demonstrates mathematical modeling and robotics mathematics
 */
public class RobotArmKinematics {
    
    // Joint representation
    static class Joint {
        double angle;        // Joint angle in radians
        double length;       // Link length
        double minAngle;     // Joint limits
        double maxAngle;
        String name;
        
        public Joint(String name, double length, double minAngle, double maxAngle) {
            this.name = name;
            this.length = length;
            this.minAngle = minAngle;
            this.maxAngle = maxAngle;
            this.angle = 0;
        }
        
        public void setAngle(double angle) {
            this.angle = Math.max(minAngle, Math.min(maxAngle, angle));
        }
        
        public double getAngle() {
            return angle;
        }
        
        @Override
        public String toString() {
            return String.format("%s: %.2f° (%.3f rad), Length: %.2f", 
                name, Math.toDegrees(angle), angle, length);
        }
    }
    
    // 3D Point representation
    static class Point3D {
        double x, y, z;
        
        public Point3D(double x, double y, double z) {
            this.x = x;
            this.y = y;
            this.z = z;
        }
        
        public double distanceTo(Point3D other) {
            return Math.sqrt(Math.pow(x - other.x, 2) + 
                           Math.pow(y - other.y, 2) + 
                           Math.pow(z - other.z, 2));
        }
        
        @Override
        public String toString() {
            return String.format("(%.3f, %.3f, %.3f)", x, y, z);
        }
    }
    
    // Transformation matrix for 3D transformations
    static class TransformMatrix {
        double[][] matrix;
        
        public TransformMatrix() {
            matrix = new double[4][4];
            // Initialize as identity matrix
            for (int i = 0; i < 4; i++) {
                matrix[i][i] = 1.0;
            }
        }
        
        public static TransformMatrix rotationZ(double angle) {
            TransformMatrix tm = new TransformMatrix();
            double cos = Math.cos(angle);
            double sin = Math.sin(angle);
            
            tm.matrix[0][0] = cos;
            tm.matrix[0][1] = -sin;
            tm.matrix[1][0] = sin;
            tm.matrix[1][1] = cos;
            
            return tm;
        }
        
        public static TransformMatrix translation(double x, double y, double z) {
            TransformMatrix tm = new TransformMatrix();
            tm.matrix[0][3] = x;
            tm.matrix[1][3] = y;
            tm.matrix[2][3] = z;
            return tm;
        }
        
        public TransformMatrix multiply(TransformMatrix other) {
            TransformMatrix result = new TransformMatrix();
            
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 4; j++) {
                    result.matrix[i][j] = 0;
                    for (int k = 0; k < 4; k++) {
                        result.matrix[i][j] += this.matrix[i][k] * other.matrix[k][j];
                    }
                }
            }
            
            return result;
        }
        
        public Point3D transform(Point3D point) {
            double x = matrix[0][0] * point.x + matrix[0][1] * point.y + 
                      matrix[0][2] * point.z + matrix[0][3];
            double y = matrix[1][0] * point.x + matrix[1][1] * point.y + 
                      matrix[1][2] * point.z + matrix[1][3];
            double z = matrix[2][0] * point.x + matrix[2][1] * point.y + 
                      matrix[2][2] * point.z + matrix[2][3];
            
            return new Point3D(x, y, z);
        }
    }
    
    // Robot arm configuration
    private List<Joint> joints;
    private Point3D basePosition;
    
    public RobotArmKinematics() {
        joints = new ArrayList<>();
        basePosition = new Point3D(0, 0, 0);
        initializeDefaultArm();
    }
    
    private void initializeDefaultArm() {
        // Create a 6-DOF robot arm (typical industrial robot)
        joints.add(new Joint("Base", 0.5, -Math.PI, Math.PI));           // Base rotation
        joints.add(new Joint("Shoulder", 1.0, -Math.PI/2, Math.PI/2));   // Shoulder pitch
        joints.add(new Joint("Elbow", 0.8, -Math.PI, 0));               // Elbow pitch
        joints.add(new Joint("Wrist1", 0.3, -Math.PI, Math.PI));        // Wrist roll
        joints.add(new Joint("Wrist2", 0.2, -Math.PI/2, Math.PI/2));    // Wrist pitch
        joints.add(new Joint("Wrist3", 0.1, -Math.PI, Math.PI));        // Wrist yaw
    }
    
    /**
     * Forward Kinematics: Calculate end-effector position from joint angles
     */
    public Point3D forwardKinematics() {
        TransformMatrix currentTransform = new TransformMatrix();
        Point3D currentPosition = new Point3D(0, 0, 0);
        
        // Apply transformations for each joint
        for (int i = 0; i < joints.size(); i++) {
            Joint joint = joints.get(i);
            
            // Rotation around Z-axis for this joint
            TransformMatrix rotation = TransformMatrix.rotationZ(joint.getAngle());
            
            // Translation along X-axis for link length
            TransformMatrix translation = TransformMatrix.translation(joint.length, 0, 0);
            
            // Combine transformations
            currentTransform = currentTransform.multiply(rotation).multiply(translation);
        }
        
        // Transform origin to get end-effector position
        return currentTransform.transform(new Point3D(0, 0, 0));
    }
    
    /**
     * Inverse Kinematics: Calculate joint angles to reach target position
     * Uses analytical solution for 2-DOF case and numerical methods for higher DOF
     */
    public boolean inverseKinematics(Point3D target) {
        if (joints.size() == 2) {
            return inverseKinematics2DOF(target);
        } else {
            return inverseKinematicsNumerical(target, 100, 0.001);
        }
    }
    
    /**
     * Analytical inverse kinematics for 2-DOF planar arm
     */
    private boolean inverseKinematics2DOF(Point3D target) {
        if (joints.size() < 2) return false;
        
        double x = target.x;
        double y = target.y;
        double l1 = joints.get(0).length;
        double l2 = joints.get(1).length;
        
        // Distance to target
        double distance = Math.sqrt(x * x + y * y);
        
        // Check if target is reachable
        if (distance > l1 + l2 || distance < Math.abs(l1 - l2)) {
            System.out.println("Target unreachable: distance = " + distance + 
                             ", max reach = " + (l1 + l2));
            return false;
        }
        
        // Calculate joint angles using law of cosines
        double cosTheta2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2);
        double theta2 = Math.acos(Math.max(-1, Math.min(1, cosTheta2))); // Elbow up solution
        
        double k1 = l1 + l2 * Math.cos(theta2);
        double k2 = l2 * Math.sin(theta2);
        double theta1 = Math.atan2(y, x) - Math.atan2(k2, k1);
        
        // Set joint angles
        joints.get(0).setAngle(theta1);
        joints.get(1).setAngle(theta2);
        
        return true;
    }
    
    /**
     * Numerical inverse kinematics using Jacobian method
     */
    private boolean inverseKinematicsNumerical(Point3D target, int maxIterations, double tolerance) {
        for (int iteration = 0; iteration < maxIterations; iteration++) {
            Point3D currentPos = forwardKinematics();
            
            // Calculate error
            double errorX = target.x - currentPos.x;
            double errorY = target.y - currentPos.y;
            double errorZ = target.z - currentPos.z;
            double error = Math.sqrt(errorX * errorX + errorY * errorY + errorZ * errorZ);
            
            if (error < tolerance) {
                return true; // Solution found
            }
            
            // Calculate Jacobian matrix (simplified)
            double[][] jacobian = calculateJacobian();
            
            // Calculate joint angle updates using pseudo-inverse
            double[] deltaAngles = calculateJointUpdates(jacobian, errorX, errorY, errorZ);
            
            // Update joint angles
            for (int i = 0; i < joints.size() && i < deltaAngles.length; i++) {
                double newAngle = joints.get(i).getAngle() + deltaAngles[i] * 0.1; // Damping factor
                joints.get(i).setAngle(newAngle);
            }
        }
        
        return false; // No solution found within iterations
    }
    
    /**
     * Calculate Jacobian matrix for current configuration
     */
    private double[][] calculateJacobian() {
        double[][] jacobian = new double[3][joints.size()];
        double deltaAngle = 0.001; // Small angle for numerical differentiation
        
        Point3D basePos = forwardKinematics();
        
        for (int j = 0; j < joints.size(); j++) {
            // Perturb joint angle
            double originalAngle = joints.get(j).getAngle();
            joints.get(j).setAngle(originalAngle + deltaAngle);
            
            Point3D perturbedPos = forwardKinematics();
            
            // Calculate partial derivatives
            jacobian[0][j] = (perturbedPos.x - basePos.x) / deltaAngle;
            jacobian[1][j] = (perturbedPos.y - basePos.y) / deltaAngle;
            jacobian[2][j] = (perturbedPos.z - basePos.z) / deltaAngle;
            
            // Restore original angle
            joints.get(j).setAngle(originalAngle);
        }
        
        return jacobian;
    }
    
    /**
     * Calculate joint updates using simplified pseudo-inverse
     */
    private double[] calculateJointUpdates(double[][] jacobian, double errorX, double errorY, double errorZ) {
        double[] errors = {errorX, errorY, errorZ};
        double[] updates = new double[joints.size()];
        
        // Simplified approach: use transpose instead of full pseudo-inverse
        for (int j = 0; j < joints.size(); j++) {
            updates[j] = 0;
            for (int i = 0; i < 3; i++) {
                updates[j] += jacobian[i][j] * errors[i];
            }
        }
        
        return updates;
    }
    
    /**
     * Check if a point is within the robot's workspace
     */
    public boolean isInWorkspace(Point3D point) {
        // Calculate maximum reach
        double maxReach = joints.stream().mapToDouble(j -> j.length).sum();
        double distance = point.distanceTo(basePosition);
        
        return distance <= maxReach;
    }
    
    /**
     * Generate workspace points for visualization
     */
    public List<Point3D> generateWorkspace(int samples) {
        List<Point3D> workspacePoints = new ArrayList<>();
        Random random = new Random(42); // Fixed seed for reproducibility
        
        for (int i = 0; i < samples; i++) {
            // Set random joint angles within limits
            for (Joint joint : joints) {
                double randomAngle = joint.minAngle + 
                    random.nextDouble() * (joint.maxAngle - joint.minAngle);
                joint.setAngle(randomAngle);
            }
            
            // Calculate forward kinematics for this configuration
            Point3D point = forwardKinematics();
            workspacePoints.add(point);
        }
        
        return workspacePoints;
    }
    
    /**
     * Plan a trajectory between two points
     */
    public List<Point3D> planTrajectory(Point3D start, Point3D end, int steps) {
        List<Point3D> trajectory = new ArrayList<>();
        
        for (int i = 0; i <= steps; i++) {
            double t = (double) i / steps;
            
            // Linear interpolation in Cartesian space
            double x = start.x + t * (end.x - start.x);
            double y = start.y + t * (end.y - start.y);
            double z = start.z + t * (end.z - start.z);
            
            trajectory.add(new Point3D(x, y, z));
        }
        
        return trajectory;
    }
    
    /**
     * Execute trajectory by calculating inverse kinematics for each point
     */
    public boolean executeTrajectory(List<Point3D> trajectory) {
        System.out.println("Executing trajectory with " + trajectory.size() + " points:");
        
        for (int i = 0; i < trajectory.size(); i++) {
            Point3D target = trajectory.get(i);
            
            if (inverseKinematics(target)) {
                Point3D achieved = forwardKinematics();
                double error = target.distanceTo(achieved);
                
                if (i % (trajectory.size() / 5) == 0) { // Print every 20% of trajectory
                    System.out.printf("Step %d: Target %s -> Achieved %s (Error: %.4f)%n", 
                        i, target, achieved, error);
                }
            } else {
                System.out.println("Failed to reach point " + i + ": " + target);
                return false;
            }
        }
        
        return true;
    }
    
    public void printJointStates() {
        System.out.println("Current Joint States:");
        for (int i = 0; i < joints.size(); i++) {
            System.out.println("  Joint " + (i + 1) + " - " + joints.get(i));
        }
    }
    
    public void setJointAngles(double[] angles) {
        for (int i = 0; i < Math.min(angles.length, joints.size()); i++) {
            joints.get(i).setAngle(angles[i]);
        }
    }
    
    /**
     * Demonstration and testing
     */
    public static void main(String[] args) {
        System.out.println("Robot Arm Kinematics - Demonstration\n");
        
        // Test 1: Forward Kinematics
        System.out.println("Test 1: Forward Kinematics");
        System.out.println("---------------------------");
        
        RobotArmKinematics arm = new RobotArmKinematics();
        
        // Set some joint angles
        double[] testAngles = {Math.PI/4, Math.PI/6, -Math.PI/4, 0, Math.PI/8, 0};
        arm.setJointAngles(testAngles);
        
        arm.printJointStates();
        Point3D endEffector = arm.forwardKinematics();
        System.out.println("\nEnd-effector position: " + endEffector);
        
        System.out.println("\n" + "=".repeat(50));
        
        // Test 2: Inverse Kinematics
        System.out.println("\nTest 2: Inverse Kinematics");
        System.out.println("---------------------------");
        
        Point3D target1 = new Point3D(1.5, 1.0, 0.5);
        System.out.println("Target position: " + target1);
        
        if (arm.inverseKinematics(target1)) {
            System.out.println("Inverse kinematics successful!");
            arm.printJointStates();
            
            Point3D achieved = arm.forwardKinematics();
            double error = target1.distanceTo(achieved);
            System.out.println("Achieved position: " + achieved);
            System.out.println("Position error: " + error);
        } else {
            System.out.println("Inverse kinematics failed - target may be unreachable");
        }
        
        System.out.println("\n" + "=".repeat(50));
        
        // Test 3: Workspace Analysis
        System.out.println("\nTest 3: Workspace Analysis");
        System.out.println("---------------------------");
        
        List<Point3D> workspace = arm.generateWorkspace(1000);
        
        // Analyze workspace
        double maxX = workspace.stream().mapToDouble(p -> p.x).max().orElse(0);
        double minX = workspace.stream().mapToDouble(p -> p.x).min().orElse(0);
        double maxY = workspace.stream().mapToDouble(p -> p.y).max().orElse(0);
        double minY = workspace.stream().mapToDouble(p -> p.y).min().orElse(0);
        double maxZ = workspace.stream().mapToDouble(p -> p.z).max().orElse(0);
        double minZ = workspace.stream().mapToDouble(p -> p.z).min().orElse(0);
        
        System.out.printf("Workspace bounds:%n");
        System.out.printf("  X: %.3f to %.3f (range: %.3f)%n", minX, maxX, maxX - minX);
        System.out.printf("  Y: %.3f to %.3f (range: %.3f)%n", minY, maxY, maxY - minY);
        System.out.printf("  Z: %.3f to %.3f (range: %.3f)%n", minZ, maxZ, maxZ - minZ);
        
        // Test some points
        Point3D[] testPoints = {
            new Point3D(1.0, 0.5, 0.2),
            new Point3D(2.5, 1.5, 1.0),
            new Point3D(0.1, 0.1, 0.1),
            new Point3D(5.0, 5.0, 5.0)
        };
        
        System.out.println("\nReachability test:");
        for (Point3D point : testPoints) {
            boolean reachable = arm.isInWorkspace(point);
            System.out.printf("  %s: %s%n", point, reachable ? "Reachable" : "Unreachable");
        }
        
        System.out.println("\n" + "=".repeat(50));
        
        // Test 4: Trajectory Planning
        System.out.println("\nTest 4: Trajectory Planning");
        System.out.println("----------------------------");
        
        Point3D startPoint = new Point3D(1.0, 0.5, 0.3);
        Point3D endPoint = new Point3D(1.2, 1.0, 0.8);
        
        System.out.println("Planning trajectory from " + startPoint + " to " + endPoint);
        
        List<Point3D> trajectory = arm.planTrajectory(startPoint, endPoint, 10);
        boolean success = arm.executeTrajectory(trajectory);
        
        if (success) {
            System.out.println("\nTrajectory executed successfully!");
        } else {
            System.out.println("\nTrajectory execution failed!");
        }
        
        System.out.println("\n" + "=".repeat(50));
        
        // Test 5: 2-DOF Analytical Solution
        System.out.println("\nTest 5: 2-DOF Analytical Inverse Kinematics");
        System.out.println("---------------------------------------------");
        
        // Create a simple 2-DOF arm for analytical solution
        RobotArmKinematics arm2DOF = new RobotArmKinematics();
        arm2DOF.joints.clear();
        arm2DOF.joints.add(new Joint("Joint1", 1.0, -Math.PI, Math.PI));
        arm2DOF.joints.add(new Joint("Joint2", 0.8, -Math.PI, Math.PI));
        
        Point3D target2DOF = new Point3D(1.5, 0.5, 0);
        System.out.println("2-DOF Target: " + target2DOF);
        
        if (arm2DOF.inverseKinematics(target2DOF)) {
            System.out.println("Analytical solution found!");
            arm2DOF.printJointStates();
            
            Point3D achieved2DOF = arm2DOF.forwardKinematics();
            double error2DOF = target2DOF.distanceTo(achieved2DOF);
            System.out.println("Achieved: " + achieved2DOF);
            System.out.println("Error: " + error2DOF);
        } else {
            System.out.println("Target unreachable for 2-DOF arm");
        }
        
        System.out.println("\n" + "=".repeat(50));
        System.out.println("Robot Arm Kinematics Demo Complete!");
        System.out.println("This demonstrates essential robotics mathematics.");
        System.out.println("\nKey Features Demonstrated:");
        System.out.println("- Forward kinematics using transformation matrices");
        System.out.println("- Analytical inverse kinematics for 2-DOF arms");
        System.out.println("- Numerical inverse kinematics using Jacobian method");
        System.out.println("- Workspace analysis and reachability testing");
        System.out.println("- Trajectory planning and execution");
    }
}