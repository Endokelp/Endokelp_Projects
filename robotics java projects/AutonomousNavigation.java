import java.util.*;

/**
 * Autonomous Navigation System for Robotics
 * Implements A* pathfinding algorithm for obstacle avoidance
 * Demonstrates: Graph algorithms, heuristics, robotics navigation
 */
public class AutonomousNavigation {
    private static final int GRID_SIZE = 20;
    private static final char EMPTY = '·';
    private static final char OBSTACLE = '█';
    private static final char PATH = '*';
    private static final char START = 'S';
    private static final char END = 'E';
    
    private char[][] grid;
    private boolean[][] obstacles;
    
    // Node class for A* algorithm
    static class Node implements Comparable<Node> {
        int x, y;
        double gCost, hCost, fCost;
        Node parent;
        
        Node(int x, int y) {
            this.x = x;
            this.y = y;
        }
        
        @Override
        public int compareTo(Node other) {
            return Double.compare(this.fCost, other.fCost);
        }
        
        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (obj == null || getClass() != obj.getClass()) return false;
            Node node = (Node) obj;
            return x == node.x && y == node.y;
        }
        
        @Override
        public int hashCode() {
            return Objects.hash(x, y);
        }
    }
    
    public AutonomousNavigation() {
        grid = new char[GRID_SIZE][GRID_SIZE];
        obstacles = new boolean[GRID_SIZE][GRID_SIZE];
        initializeGrid();
        generateObstacles();
    }
    
    private void initializeGrid() {
        for (int i = 0; i < GRID_SIZE; i++) {
            for (int j = 0; j < GRID_SIZE; j++) {
                grid[i][j] = EMPTY;
                obstacles[i][j] = false;
            }
        }
    }
    
    private void generateObstacles() {
        // Create some strategic obstacles
        int[][] obstaclePatterns = {
            {3, 10}, {3, 11}, {3, 12}, // Horizontal wall
            {4, 12}, {5, 12}, // Vertical extension
            {5, 5}, {6, 5}, {7, 5}, {7, 6}, {7, 7}, // L-shaped obstacle
            {8, 15}, {9, 15}, {10, 15}, {10, 16}, {10, 17}, // Another pattern
            {12, 3}, {12, 4}, {12, 5}, {12, 6} // Bottom obstacle
        };
        
        for (int[] pos : obstaclePatterns) {
            if (pos[0] < GRID_SIZE && pos[1] < GRID_SIZE) {
                obstacles[pos[0]][pos[1]] = true;
                grid[pos[0]][pos[1]] = OBSTACLE;
            }
        }
    }
    
    public List<Node> findPath(int startX, int startY, int endX, int endY) {
        PriorityQueue<Node> openSet = new PriorityQueue<>();
        Set<Node> closedSet = new HashSet<>();
        
        Node startNode = new Node(startX, startY);
        Node endNode = new Node(endX, endY);
        
        startNode.gCost = 0;
        startNode.hCost = calculateHeuristic(startNode, endNode);
        startNode.fCost = startNode.gCost + startNode.hCost;
        
        openSet.add(startNode);
        
        while (!openSet.isEmpty()) {
            Node current = openSet.poll();
            closedSet.add(current);
            
            if (current.equals(endNode)) {
                return reconstructPath(current);
            }
            
            for (Node neighbor : getNeighbors(current)) {
                if (closedSet.contains(neighbor) || isObstacle(neighbor.x, neighbor.y)) {
                    continue;
                }
                
                double tentativeGCost = current.gCost + getDistance(current, neighbor);
                
                if (!openSet.contains(neighbor)) {
                    openSet.add(neighbor);
                } else if (tentativeGCost >= neighbor.gCost) {
                    continue;
                }
                
                neighbor.parent = current;
                neighbor.gCost = tentativeGCost;
                neighbor.hCost = calculateHeuristic(neighbor, endNode);
                neighbor.fCost = neighbor.gCost + neighbor.hCost;
            }
        }
        
        return new ArrayList<>(); // No path found
    }
    
    private double calculateHeuristic(Node a, Node b) {
        // Manhattan distance
        return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
    }
    
    private double getDistance(Node a, Node b) {
        // Euclidean distance for more accurate pathfinding
        return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
    }
    
    private List<Node> getNeighbors(Node node) {
        List<Node> neighbors = new ArrayList<>();
        int[][] directions = {{-1,0}, {1,0}, {0,-1}, {0,1}, {-1,-1}, {-1,1}, {1,-1}, {1,1}};
        
        for (int[] dir : directions) {
            int newX = node.x + dir[0];
            int newY = node.y + dir[1];
            
            if (isValidPosition(newX, newY)) {
                neighbors.add(new Node(newX, newY));
            }
        }
        
        return neighbors;
    }
    
    private boolean isValidPosition(int x, int y) {
        return x >= 0 && x < GRID_SIZE && y >= 0 && y < GRID_SIZE;
    }
    
    private boolean isObstacle(int x, int y) {
        return obstacles[x][y];
    }
    
    private List<Node> reconstructPath(Node endNode) {
        List<Node> path = new ArrayList<>();
        Node current = endNode;
        
        while (current != null) {
            path.add(0, current);
            current = current.parent;
        }
        
        return path;
    }
    
    public void displayPath(List<Node> path, int startX, int startY, int endX, int endY) {
        char[][] displayGrid = new char[GRID_SIZE][GRID_SIZE];
        
        // Copy original grid
        for (int i = 0; i < GRID_SIZE; i++) {
            System.arraycopy(grid[i], 0, displayGrid[i], 0, GRID_SIZE);
        }
        
        // Mark path
        for (Node node : path) {
            if (!(node.x == startX && node.y == startY) && !(node.x == endX && node.y == endY)) {
                displayGrid[node.x][node.y] = PATH;
            }
        }
        
        // Mark start and end
        displayGrid[startX][startY] = START;
        displayGrid[endX][endY] = END;
        
        System.out.println("\nAutonomous Navigation - Path Planning Result:");
        System.out.println("S = Start, E = End, * = Path, █ = Obstacle, · = Free\n");
        
        for (int i = 0; i < GRID_SIZE; i++) {
            for (int j = 0; j < GRID_SIZE; j++) {
                System.out.print(displayGrid[i][j] + " ");
            }
            System.out.println();
        }
        
        System.out.println("\nPath coordinates:");
        for (int i = 0; i < path.size(); i++) {
            Node node = path.get(i);
            System.out.println("Step " + i + ": (" + node.x + "," + node.y + ")");
        }
    }
    
    public static void main(String[] args) {
        AutonomousNavigation nav = new AutonomousNavigation();
        
        // Test case 1: Simple diagonal path
        System.out.println("Finding path from (1,1) to (8,8)");
        List<Node> path1 = nav.findPath(1, 1, 8, 8);
        if (!path1.isEmpty()) {
            System.out.println("Path found! Length: " + path1.size() + " steps");
            nav.displayPath(path1, 1, 1, 8, 8);
        } else {
            System.out.println("No path found!");
        }
        
        System.out.println("\n" + "=".repeat(50));
        
        // Test case 2: Path around obstacles
        System.out.println("Finding path from (1,1) to (15,2)");
        List<Node> path2 = nav.findPath(1, 1, 15, 2);
        if (!path2.isEmpty()) {
            System.out.println("Path found! Length: " + path2.size() + " steps");
            nav.displayPath(path2, 1, 1, 15, 2);
        } else {
            System.out.println("No path found!");
        }
        
        System.out.println("\n" + "=".repeat(50));
        System.out.println("Autonomous Navigation System Demo Complete!");
        System.out.println("This demonstrates A* pathfinding for robotics applications.");
    }
}