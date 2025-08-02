import java.util.*;
import java.util.concurrent.*;

/**
 * Vision Processing System for Robotics
 * Implements computer vision algorithms for object detection and tracking
 * Demonstrates image processing, pattern recognition, and coordinate transformations
 */
public class VisionProcessing {
    
    // Simple image representation
    static class Image {
        int width, height;
        int[][][] pixels; // [height][width][RGB]
        
        public Image(int width, int height) {
            this.width = width;
            this.height = height;
            this.pixels = new int[height][width][3];
        }
        
        public void setPixel(int x, int y, int r, int g, int b) {
            if (x >= 0 && x < width && y >= 0 && y < height) {
                pixels[y][x][0] = Math.max(0, Math.min(255, r));
                pixels[y][x][1] = Math.max(0, Math.min(255, g));
                pixels[y][x][2] = Math.max(0, Math.min(255, b));
            }
        }
        
        public int[] getPixel(int x, int y) {
            if (x >= 0 && x < width && y >= 0 && y < height) {
                return pixels[y][x].clone();
            }
            return new int[]{0, 0, 0};
        }
        
        public int getGrayscale(int x, int y) {
            int[] rgb = getPixel(x, y);
            return (int)(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]);
        }
        
        public Image copy() {
            Image copy = new Image(width, height);
            for (int y = 0; y < height; y++) {
                for (int x = 0; x < width; x++) {
                    int[] pixel = getPixel(x, y);
                    copy.setPixel(x, y, pixel[0], pixel[1], pixel[2]);
                }
            }
            return copy;
        }
    }
    
    // Detected object representation
    static class DetectedObject {
        int x, y, width, height;
        String label;
        double confidence;
        int[] color;
        
        public DetectedObject(int x, int y, int width, int height, String label, double confidence) {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;
            this.label = label;
            this.confidence = confidence;
        }
        
        public int getCenterX() {
            return x + width / 2;
        }
        
        public int getCenterY() {
            return y + height / 2;
        }
        
        public double getArea() {
            return width * height;
        }
        
        @Override
        public String toString() {
            return String.format("%s at (%d,%d) %dx%d, confidence: %.2f", 
                label, x, y, width, height, confidence);
        }
    }
    
    // Camera calibration parameters
    static class CameraCalibration {
        double focalLengthX, focalLengthY;
        double principalPointX, principalPointY;
        double[] distortionCoeffs;
        
        public CameraCalibration(double fx, double fy, double cx, double cy) {
            this.focalLengthX = fx;
            this.focalLengthY = fy;
            this.principalPointX = cx;
            this.principalPointY = cy;
            this.distortionCoeffs = new double[]{0, 0, 0, 0, 0}; // Simplified
        }
        
        // Convert pixel coordinates to real-world coordinates
        public double[] pixelToWorld(int pixelX, int pixelY, double depth) {
            double worldX = (pixelX - principalPointX) * depth / focalLengthX;
            double worldY = (pixelY - principalPointY) * depth / focalLengthY;
            return new double[]{worldX, worldY, depth};
        }
        
        // Convert real-world coordinates to pixel coordinates
        public int[] worldToPixel(double worldX, double worldY, double worldZ) {
            int pixelX = (int)(focalLengthX * worldX / worldZ + principalPointX);
            int pixelY = (int)(focalLengthY * worldY / worldZ + principalPointY);
            return new int[]{pixelX, pixelY};
        }
    }
    
    private CameraCalibration calibration;
    private List<DetectedObject> trackedObjects;
    private Random random;
    
    public VisionProcessing() {
        // Default camera calibration (typical webcam)
        calibration = new CameraCalibration(800, 800, 320, 240);
        trackedObjects = new ArrayList<>();
        random = new Random(42);
    }
    
    /**
     * Color-based object detection
     */
    public List<DetectedObject> detectColorObjects(Image image, int[] targetColor, int tolerance) {
        List<DetectedObject> objects = new ArrayList<>();
        boolean[][] visited = new boolean[image.height][image.width];
        
        for (int y = 0; y < image.height; y++) {
            for (int x = 0; x < image.width; x++) {
                if (!visited[y][x] && isColorMatch(image.getPixel(x, y), targetColor, tolerance)) {
                    // Found a matching pixel, perform flood fill to find the object
                    DetectedObject obj = floodFillObject(image, x, y, targetColor, tolerance, visited);
                    if (obj != null && obj.getArea() > 50) { // Minimum size threshold
                        objects.add(obj);
                    }
                }
            }
        }
        
        return objects;
    }
    
    private boolean isColorMatch(int[] pixel, int[] target, int tolerance) {
        int rDiff = Math.abs(pixel[0] - target[0]);
        int gDiff = Math.abs(pixel[1] - target[1]);
        int bDiff = Math.abs(pixel[2] - target[2]);
        
        return rDiff <= tolerance && gDiff <= tolerance && bDiff <= tolerance;
    }
    
    private DetectedObject floodFillObject(Image image, int startX, int startY, 
                                         int[] targetColor, int tolerance, boolean[][] visited) {
        Queue<int[]> queue = new LinkedList<>();
        queue.offer(new int[]{startX, startY});
        visited[startY][startX] = true;
        
        int minX = startX, maxX = startX;
        int minY = startY, maxY = startY;
        int pixelCount = 0;
        
        while (!queue.isEmpty()) {
            int[] current = queue.poll();
            int x = current[0];
            int y = current[1];
            pixelCount++;
            
            // Update bounding box
            minX = Math.min(minX, x);
            maxX = Math.max(maxX, x);
            minY = Math.min(minY, y);
            maxY = Math.max(maxY, y);
            
            // Check 4-connected neighbors
            int[][] directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
            for (int[] dir : directions) {
                int nx = x + dir[0];
                int ny = y + dir[1];
                
                if (nx >= 0 && nx < image.width && ny >= 0 && ny < image.height && 
                    !visited[ny][nx] && isColorMatch(image.getPixel(nx, ny), targetColor, tolerance)) {
                    visited[ny][nx] = true;
                    queue.offer(new int[]{nx, ny});
                }
            }
        }
        
        if (pixelCount > 10) { // Minimum pixel count
            return new DetectedObject(minX, minY, maxX - minX + 1, maxY - minY + 1, 
                                    "ColorObject", 0.8);
        }
        
        return null;
    }
    
    /**
     * Edge detection using Sobel operator
     */
    public Image detectEdges(Image image) {
        Image edges = new Image(image.width, image.height);
        
        // Sobel kernels
        int[][] sobelX = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
        int[][] sobelY = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
        
        for (int y = 1; y < image.height - 1; y++) {
            for (int x = 1; x < image.width - 1; x++) {
                int gx = 0, gy = 0;
                
                // Apply Sobel kernels
                for (int ky = -1; ky <= 1; ky++) {
                    for (int kx = -1; kx <= 1; kx++) {
                        int gray = image.getGrayscale(x + kx, y + ky);
                        gx += gray * sobelX[ky + 1][kx + 1];
                        gy += gray * sobelY[ky + 1][kx + 1];
                    }
                }
                
                // Calculate gradient magnitude
                int magnitude = (int)Math.sqrt(gx * gx + gy * gy);
                magnitude = Math.min(255, magnitude);
                
                edges.setPixel(x, y, magnitude, magnitude, magnitude);
            }
        }
        
        return edges;
    }
    
    /**
     * Simple template matching for object detection
     */
    public List<DetectedObject> templateMatch(Image image, Image template, double threshold) {
        List<DetectedObject> matches = new ArrayList<>();
        
        for (int y = 0; y <= image.height - template.height; y++) {
            for (int x = 0; x <= image.width - template.width; x++) {
                double correlation = calculateNormalizedCorrelation(image, template, x, y);
                
                if (correlation > threshold) {
                    matches.add(new DetectedObject(x, y, template.width, template.height, 
                                                 "Template", correlation));
                }
            }
        }
        
        // Non-maximum suppression to remove overlapping detections
        return nonMaximumSuppression(matches, 0.3);
    }
    
    private double calculateNormalizedCorrelation(Image image, Image template, int offsetX, int offsetY) {
        double sum1 = 0, sum2 = 0, sum1Sq = 0, sum2Sq = 0, pSum = 0;
        int n = template.width * template.height;
        
        for (int y = 0; y < template.height; y++) {
            for (int x = 0; x < template.width; x++) {
                int gray1 = image.getGrayscale(offsetX + x, offsetY + y);
                int gray2 = template.getGrayscale(x, y);
                
                sum1 += gray1;
                sum2 += gray2;
                sum1Sq += gray1 * gray1;
                sum2Sq += gray2 * gray2;
                pSum += gray1 * gray2;
            }
        }
        
        double num = pSum - (sum1 * sum2 / n);
        double den = Math.sqrt((sum1Sq - sum1 * sum1 / n) * (sum2Sq - sum2 * sum2 / n));
        
        return den == 0 ? 0 : num / den;
    }
    
    private List<DetectedObject> nonMaximumSuppression(List<DetectedObject> objects, double overlapThreshold) {
        objects.sort((a, b) -> Double.compare(b.confidence, a.confidence));
        List<DetectedObject> result = new ArrayList<>();
        
        for (DetectedObject obj : objects) {
            boolean suppress = false;
            
            for (DetectedObject kept : result) {
                double overlap = calculateOverlap(obj, kept);
                if (overlap > overlapThreshold) {
                    suppress = true;
                    break;
                }
            }
            
            if (!suppress) {
                result.add(obj);
            }
        }
        
        return result;
    }
    
    private double calculateOverlap(DetectedObject a, DetectedObject b) {
        int x1 = Math.max(a.x, b.x);
        int y1 = Math.max(a.y, b.y);
        int x2 = Math.min(a.x + a.width, b.x + b.width);
        int y2 = Math.min(a.y + a.height, b.y + b.height);
        
        if (x1 < x2 && y1 < y2) {
            double intersection = (x2 - x1) * (y2 - y1);
            double union = a.getArea() + b.getArea() - intersection;
            return intersection / union;
        }
        
        return 0;
    }
    
    /**
     * Object tracking using simple centroid tracking
     */
    public void updateTracking(List<DetectedObject> newDetections) {
        if (trackedObjects.isEmpty()) {
            // Initialize tracking with new detections
            trackedObjects.addAll(newDetections);
            return;
        }
        
        // Match new detections with existing tracked objects
        double maxDistance = 50.0; // Maximum distance for matching
        List<DetectedObject> updatedTracking = new ArrayList<>();
        List<Boolean> matched = new ArrayList<>(Collections.nCopies(newDetections.size(), false));
        
        for (DetectedObject tracked : trackedObjects) {
            double minDistance = Double.MAX_VALUE;
            int bestMatch = -1;
            
            for (int i = 0; i < newDetections.size(); i++) {
                if (matched.get(i)) continue;
                
                DetectedObject detection = newDetections.get(i);
                double distance = Math.sqrt(
                    Math.pow(tracked.getCenterX() - detection.getCenterX(), 2) +
                    Math.pow(tracked.getCenterY() - detection.getCenterY(), 2)
                );
                
                if (distance < minDistance && distance < maxDistance) {
                    minDistance = distance;
                    bestMatch = i;
                }
            }
            
            if (bestMatch != -1) {
                // Update tracked object with new detection
                DetectedObject detection = newDetections.get(bestMatch);
                tracked.x = detection.x;
                tracked.y = detection.y;
                tracked.width = detection.width;
                tracked.height = detection.height;
                tracked.confidence = detection.confidence;
                
                updatedTracking.add(tracked);
                matched.set(bestMatch, true);
            }
            // If no match found, the tracked object is lost (not added to updated list)
        }
        
        // Add new detections that weren't matched
        for (int i = 0; i < newDetections.size(); i++) {
            if (!matched.get(i)) {
                updatedTracking.add(newDetections.get(i));
            }
        }
        
        trackedObjects = updatedTracking;
    }
    
    /**
     * Convert pixel coordinates to real-world coordinates
     */
    public double[] pixelToWorldCoordinates(int pixelX, int pixelY, double estimatedDepth) {
        return calibration.pixelToWorld(pixelX, pixelY, estimatedDepth);
    }
    
    /**
     * Generate synthetic test image with colored objects
     */
    public Image generateTestImage(int width, int height) {
        Image image = new Image(width, height);
        
        // Fill with background
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                image.setPixel(x, y, 50, 50, 50); // Dark gray background
            }
        }
        
        // Add some colored rectangles
        addRectangle(image, 50, 50, 80, 60, new int[]{255, 0, 0}); // Red
        addRectangle(image, 200, 100, 60, 80, new int[]{0, 255, 0}); // Green
        addRectangle(image, 350, 80, 70, 70, new int[]{0, 0, 255}); // Blue
        addRectangle(image, 150, 200, 90, 50, new int[]{255, 255, 0}); // Yellow
        
        // Add some noise
        for (int i = 0; i < 1000; i++) {
            int x = random.nextInt(width);
            int y = random.nextInt(height);
            int intensity = random.nextInt(100) + 100;
            image.setPixel(x, y, intensity, intensity, intensity);
        }
        
        return image;
    }
    
    private void addRectangle(Image image, int x, int y, int width, int height, int[] color) {
        for (int dy = 0; dy < height; dy++) {
            for (int dx = 0; dx < width; dx++) {
                if (x + dx < image.width && y + dy < image.height) {
                    image.setPixel(x + dx, y + dy, color[0], color[1], color[2]);
                }
            }
        }
    }
    
    /**
     * Print image as ASCII art (for demonstration)
     */
    public void printImageASCII(Image image, int scale) {
        String chars = " .:-=+*#%@";
        
        for (int y = 0; y < image.height; y += scale) {
            for (int x = 0; x < image.width; x += scale) {
                int gray = image.getGrayscale(x, y);
                int charIndex = Math.min(chars.length() - 1, gray * chars.length() / 256);
                System.out.print(chars.charAt(charIndex));
            }
            System.out.println();
        }
    }
    
    public List<DetectedObject> getTrackedObjects() {
        return new ArrayList<>(trackedObjects);
    }
    
    /**
     * Demonstration and testing
     */
    public static void main(String[] args) {
        System.out.println("Vision Processing System for Robotics - Demonstration\n");
        
        VisionProcessing vision = new VisionProcessing();
        
        // Test 1: Generate and display test image
        System.out.println("Test 1: Synthetic Image Generation");
        System.out.println("-----------------------------------");
        
        Image testImage = vision.generateTestImage(400, 300);
        System.out.println("Generated test image: " + testImage.width + "x" + testImage.height);
        
        System.out.println("\nASCII representation (scaled):");
        vision.printImageASCII(testImage, 8);
        
        System.out.println("\n" + "=".repeat(60));
        
        // Test 2: Color-based object detection
        System.out.println("\nTest 2: Color-based Object Detection");
        System.out.println("------------------------------------");
        
        // Detect red objects
        List<DetectedObject> redObjects = vision.detectColorObjects(testImage, new int[]{255, 0, 0}, 30);
        System.out.println("Red objects detected: " + redObjects.size());
        for (DetectedObject obj : redObjects) {
            System.out.println("  " + obj);
            
            // Convert to world coordinates (assuming 1m depth)
            double[] worldCoords = vision.pixelToWorldCoordinates(obj.getCenterX(), obj.getCenterY(), 1.0);
            System.out.printf("    World coordinates: (%.3f, %.3f, %.3f)%n", 
                worldCoords[0], worldCoords[1], worldCoords[2]);
        }
        
        // Detect green objects
        List<DetectedObject> greenObjects = vision.detectColorObjects(testImage, new int[]{0, 255, 0}, 30);
        System.out.println("\nGreen objects detected: " + greenObjects.size());
        for (DetectedObject obj : greenObjects) {
            System.out.println("  " + obj);
        }
        
        // Detect blue objects
        List<DetectedObject> blueObjects = vision.detectColorObjects(testImage, new int[]{0, 0, 255}, 30);
        System.out.println("\nBlue objects detected: " + blueObjects.size());
        for (DetectedObject obj : blueObjects) {
            System.out.println("  " + obj);
        }
        
        System.out.println("\n" + "=".repeat(60));
        
        // Test 3: Edge detection
        System.out.println("\nTest 3: Edge Detection");
        System.out.println("----------------------");
        
        Image edges = vision.detectEdges(testImage);
        System.out.println("Edge detection completed.");
        System.out.println("\nEdge image (ASCII representation):");
        vision.printImageASCII(edges, 8);
        
        System.out.println("\n" + "=".repeat(60));
        
        // Test 4: Object tracking simulation
        System.out.println("\nTest 4: Object Tracking Simulation");
        System.out.println("-----------------------------------");
        
        // Combine all detected objects
        List<DetectedObject> allObjects = new ArrayList<>();
        allObjects.addAll(redObjects);
        allObjects.addAll(greenObjects);
        allObjects.addAll(blueObjects);
        
        System.out.println("Initial tracking with " + allObjects.size() + " objects:");
        vision.updateTracking(allObjects);
        
        List<DetectedObject> tracked = vision.getTrackedObjects();
        for (int i = 0; i < tracked.size(); i++) {
            System.out.println("  Object " + (i + 1) + ": " + tracked.get(i));
        }
        
        // Simulate object movement
        System.out.println("\nSimulating object movement...");
        for (int frame = 1; frame <= 3; frame++) {
            List<DetectedObject> movedObjects = new ArrayList<>();
            
            for (DetectedObject obj : allObjects) {
                // Simulate slight movement
                int newX = obj.x + vision.random.nextInt(21) - 10; // -10 to +10 pixels
                int newY = obj.y + vision.random.nextInt(21) - 10;
                
                DetectedObject moved = new DetectedObject(newX, newY, obj.width, obj.height, 
                                                        obj.label, obj.confidence * 0.95);
                movedObjects.add(moved);
            }
            
            vision.updateTracking(movedObjects);
            
            System.out.println("\nFrame " + frame + " tracking results:");
            tracked = vision.getTrackedObjects();
            for (int i = 0; i < tracked.size(); i++) {
                System.out.println("  Object " + (i + 1) + ": " + tracked.get(i));
            }
        }
        
        System.out.println("\n" + "=".repeat(60));
        
        // Test 5: Camera calibration and coordinate transformation
        System.out.println("\nTest 5: Camera Calibration and Coordinate Transformation");
        System.out.println("---------------------------------------------------------");
        
        System.out.println("Camera calibration parameters:");
        System.out.printf("  Focal length: (%.1f, %.1f)%n", 
            vision.calibration.focalLengthX, vision.calibration.focalLengthY);
        System.out.printf("  Principal point: (%.1f, %.1f)%n", 
            vision.calibration.principalPointX, vision.calibration.principalPointY);
        
        System.out.println("\nCoordinate transformation examples:");
        
        // Test pixel to world conversion
        int[][] testPixels = {{200, 150}, {100, 100}, {300, 200}};
        double[] testDepths = {0.5, 1.0, 1.5};
        
        for (int i = 0; i < testPixels.length; i++) {
            int[] pixel = testPixels[i];
            double depth = testDepths[i];
            
            double[] world = vision.pixelToWorldCoordinates(pixel[0], pixel[1], depth);
            int[] backToPixel = vision.calibration.worldToPixel(world[0], world[1], world[2]);
            
            System.out.printf("  Pixel (%d, %d) at depth %.1fm -> World (%.3f, %.3f, %.3f) -> Pixel (%d, %d)%n",
                pixel[0], pixel[1], depth, world[0], world[1], world[2], 
                backToPixel[0], backToPixel[1]);
        }
        
        System.out.println("\n" + "=".repeat(60));
        
        // Test 6: Template matching simulation
        System.out.println("\nTest 6: Template Matching (Simulated)");
        System.out.println("--------------------------------------");
        
        // Create a small template (simulated)
        Image template = new Image(30, 30);
        for (int y = 0; y < 30; y++) {
            for (int x = 0; x < 30; x++) {
                if (x > 5 && x < 25 && y > 5 && y < 25) {
                    template.setPixel(x, y, 255, 0, 0); // Red square template
                } else {
                    template.setPixel(x, y, 50, 50, 50); // Background
                }
            }
        }
        
        List<DetectedObject> templateMatches = vision.templateMatch(testImage, template, 0.7);
        System.out.println("Template matches found: " + templateMatches.size());
        for (DetectedObject match : templateMatches) {
            System.out.println("  " + match);
        }
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Vision Processing Demo Complete!");
        System.out.println("This demonstrates computer vision for robotics applications.");
        System.out.println("\nKey Features Demonstrated:");
        System.out.println("- Color-based object detection with flood fill");
        System.out.println("- Edge detection using Sobel operators");
        System.out.println("- Template matching with normalized correlation");
        System.out.println("- Object tracking using centroid tracking");
        System.out.println("- Camera calibration and coordinate transformations");
        System.out.println("- Non-maximum suppression for duplicate removal");
    }
}