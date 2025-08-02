import java.util.*;
import java.util.concurrent.*;
import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Robot Communication Protocol System
 * Implements communication protocols for multi-robot coordination
 */
public class RobotCommunication {
    
    //Message types for robot communication
    enum MessageType {
        HEARTBEAT(0x01),
        POSITION_UPDATE(0x02),
        TASK_ASSIGNMENT(0x03),
        STATUS_REPORT(0x04),
        EMERGENCY_STOP(0x05),
        COORDINATION_REQUEST(0x06),
        SENSOR_DATA(0x07),
        ACKNOWLEDGMENT(0x08);
        
        private final int code;
        
        MessageType(int code) {
            this.code = code;
        }
        
        public int getCode() {
            return code;
        }
        
        public static MessageType fromCode(int code) {
            for (MessageType type : values()) {
                if (type.code == code) {
                    return type;
                }
            }
            throw new IllegalArgumentException("Unknown message type code: " + code);
        }
    }
    
    //Robot message structure
    static class RobotMessage {
        private int senderId;
        private int receiverId; // -1 for broadcast
        private MessageType type;
        private long timestamp;
        private byte[] payload;
        private int sequenceNumber;
        private String checksum;
        
        public RobotMessage(int senderId, int receiverId, MessageType type, byte[] payload, int sequenceNumber) {
            this.senderId = senderId;
            this.receiverId = receiverId;
            this.type = type;
            this.payload = payload != null ? payload.clone() : new byte[0];
            this.timestamp = System.currentTimeMillis();
            this.sequenceNumber = sequenceNumber;
            this.checksum = calculateChecksum();
        }
        
        private String calculateChecksum() {
            try {
                MessageDigest md = MessageDigest.getInstance("MD5");
                ByteBuffer buffer = ByteBuffer.allocate(16 + payload.length);
                buffer.putInt(senderId);
                buffer.putInt(receiverId);
                buffer.putInt(type.getCode());
                buffer.putInt(sequenceNumber);
                buffer.put(payload);
                
                byte[] hash = md.digest(buffer.array());
                StringBuilder sb = new StringBuilder();
                for (byte b : hash) {
                    sb.append(String.format("%02x", b));
                }
                return sb.toString().substring(0, 8); // Use first 8 characters
            } catch (NoSuchAlgorithmException e) {
                return "00000000";
            }
        }
        
        public boolean verifyChecksum() {
            return checksum.equals(calculateChecksum());
        }
        
        public byte[] serialize() {
            ByteBuffer buffer = ByteBuffer.allocate(32 + payload.length);
            buffer.putInt(senderId);
            buffer.putInt(receiverId);
            buffer.putInt(type.getCode());
            buffer.putLong(timestamp);
            buffer.putInt(sequenceNumber);
            buffer.putInt(payload.length);
            buffer.put(payload);
            buffer.put(checksum.getBytes());
            return buffer.array();
        }
        
        public static RobotMessage deserialize(byte[] data) {
            ByteBuffer buffer = ByteBuffer.wrap(data);
            int senderId = buffer.getInt();
            int receiverId = buffer.getInt();
            MessageType type = MessageType.fromCode(buffer.getInt());
            long timestamp = buffer.getLong();
            int sequenceNumber = buffer.getInt();
            int payloadLength = buffer.getInt();
            
            byte[] payload = new byte[payloadLength];
            buffer.get(payload);
            
            byte[] checksumBytes = new byte[8];
            buffer.get(checksumBytes);
            
            RobotMessage message = new RobotMessage(senderId, receiverId, type, payload, sequenceNumber);
            message.timestamp = timestamp;
            return message;
        }
        
        //Getters
        public int getSenderId() { return senderId; }
        public int getReceiverId() { return receiverId; }
        public MessageType getType() { return type; }
        public long getTimestamp() { return timestamp; }
        public byte[] getPayload() { return payload.clone(); }
        public int getSequenceNumber() { return sequenceNumber; }
        public String getChecksum() { return checksum; }
        
        @Override
        public String toString() {
            return String.format("Message[%s: %d->%d, seq=%d, payload=%d bytes, checksum=%s]",
                type, senderId, receiverId, sequenceNumber, payload.length, checksum);
        }
    }
    
    //Robot position data
    static class Position {
        double x, y, z;
        double heading; // radians
        
        public Position(double x, double y, double z, double heading) {
            this.x = x;
            this.y = y;
            this.z = z;
            this.heading = heading;
        }
        
        public byte[] toBytes() {
            ByteBuffer buffer = ByteBuffer.allocate(32);
            buffer.putDouble(x);
            buffer.putDouble(y);
            buffer.putDouble(z);
            buffer.putDouble(heading);
            return buffer.array();
        }
        
        public static Position fromBytes(byte[] data) {
            ByteBuffer buffer = ByteBuffer.wrap(data);
            return new Position(buffer.getDouble(), buffer.getDouble(), 
                             buffer.getDouble(), buffer.getDouble());
        }
        
        @Override
        public String toString() {
            return String.format("Position(%.2f, %.2f, %.2f, heading=%.2f°)", 
                x, y, z, Math.toDegrees(heading));
        }
    }
    
    //Task assignment data
    static class TaskAssignment {
        String taskId;
        String taskType;
        Position targetPosition;
        Map<String, String> parameters;
        
        public TaskAssignment(String taskId, String taskType, Position targetPosition) {
            this.taskId = taskId;
            this.taskType = taskType;
            this.targetPosition = targetPosition;
            this.parameters = new HashMap<>();
        }
        
        public void addParameter(String key, String value) {
            parameters.put(key, value);
        }
        
        public byte[] toBytes() {
            StringBuilder sb = new StringBuilder();
            sb.append(taskId).append("|");
            sb.append(taskType).append("|");
            sb.append(targetPosition.x).append(",").append(targetPosition.y)
              .append(",").append(targetPosition.z).append(",").append(targetPosition.heading).append("|");
            
            for (Map.Entry<String, String> entry : parameters.entrySet()) {
                sb.append(entry.getKey()).append("=").append(entry.getValue()).append(";");
            }
            
            return sb.toString().getBytes();
        }
        
        public static TaskAssignment fromBytes(byte[] data) {
            String str = new String(data);
            String[] parts = str.split("\\|");
            
            String taskId = parts[0];
            String taskType = parts[1];
            
            String[] posData = parts[2].split(",");
            Position pos = new Position(Double.parseDouble(posData[0]), 
                                      Double.parseDouble(posData[1]),
                                      Double.parseDouble(posData[2]),
                                      Double.parseDouble(posData[3]));
            
            TaskAssignment task = new TaskAssignment(taskId, taskType, pos);
            
            if (parts.length > 3 && !parts[3].isEmpty()) {
                String[] params = parts[3].split(";");
                for (String param : params) {
                    if (!param.isEmpty()) {
                        String[] kv = param.split("=");
                        if (kv.length == 2) {
                            task.addParameter(kv[0], kv[1]);
                        }
                    }
                }
            }
            
            return task;
        }
        
        @Override
        public String toString() {
            return String.format("Task[%s: %s at %s, params=%s]", 
                taskId, taskType, targetPosition, parameters);
        }
    }
    
    //Robot status information
    static class RobotStatus {
        int robotId;
        String status; // IDLE, MOVING, WORKING, ERROR, CHARGING
        double batteryLevel; // 0.0 to 1.0
        Position currentPosition;
        String currentTask;
        Map<String, Double> sensorReadings;
        
        public RobotStatus(int robotId, String status, double batteryLevel, Position position) {
            this.robotId = robotId;
            this.status = status;
            this.batteryLevel = batteryLevel;
            this.currentPosition = position;
            this.sensorReadings = new HashMap<>();
        }
        
        public void addSensorReading(String sensor, double value) {
            sensorReadings.put(sensor, value);
        }
        
        public byte[] toBytes() {
            StringBuilder sb = new StringBuilder();
            sb.append(robotId).append("|");
            sb.append(status).append("|");
            sb.append(batteryLevel).append("|");
            sb.append(currentPosition.x).append(",").append(currentPosition.y)
              .append(",").append(currentPosition.z).append(",").append(currentPosition.heading).append("|");
            sb.append(currentTask != null ? currentTask : "").append("|");
            
            for (Map.Entry<String, Double> entry : sensorReadings.entrySet()) {
                sb.append(entry.getKey()).append("=").append(entry.getValue()).append(";");
            }
            
            return sb.toString().getBytes();
        }
        
        public static RobotStatus fromBytes(byte[] data) {
            String str = new String(data);
            String[] parts = str.split("\\|");
            
            int robotId = Integer.parseInt(parts[0]);
            String status = parts[1];
            double batteryLevel = Double.parseDouble(parts[2]);
            
            String[] posData = parts[3].split(",");
            Position pos = new Position(Double.parseDouble(posData[0]), 
                                      Double.parseDouble(posData[1]),
                                      Double.parseDouble(posData[2]),
                                      Double.parseDouble(posData[3]));
            
            RobotStatus robotStatus = new RobotStatus(robotId, status, batteryLevel, pos);
            
            if (parts.length > 4 && !parts[4].isEmpty()) {
                robotStatus.currentTask = parts[4];
            }
            
            if (parts.length > 5 && !parts[5].isEmpty()) {
                String[] sensors = parts[5].split(";");
                for (String sensor : sensors) {
                    if (!sensor.isEmpty()) {
                        String[] kv = sensor.split("=");
                        if (kv.length == 2) {
                            robotStatus.addSensorReading(kv[0], Double.parseDouble(kv[1]));
                        }
                    }
                }
            }
            
            return robotStatus;
        }
        
        @Override
        public String toString() {
            return String.format("RobotStatus[ID=%d, %s, battery=%.1f%%, pos=%s, task=%s, sensors=%s]",
                robotId, status, batteryLevel * 100, currentPosition, currentTask, sensorReadings);
        }
    }
    
    //Communication network simulator
    static class NetworkSimulator {
        private Map<Integer, Robot> robots;
        private Queue<RobotMessage> messageQueue;
        private Random random;
        private double packetLossRate;
        private int networkDelay; // milliseconds
        
        public NetworkSimulator(double packetLossRate, int networkDelay) {
            this.robots = new ConcurrentHashMap<>();
            this.messageQueue = new ConcurrentLinkedQueue<>();
            this.random = new Random(42);
            this.packetLossRate = packetLossRate;
            this.networkDelay = networkDelay;
        }
        
        public void addRobot(Robot robot) {
            robots.put(robot.getId(), robot);
        }
        
        public void removeRobot(int robotId) {
            robots.remove(robotId);
        }
        
        public boolean sendMessage(RobotMessage message) {
            //Simulate packet loss
            if (random.nextDouble() < packetLossRate) {
                System.out.println("[NETWORK] Packet lost: " + message);
                return false;
            }
            
            //Add network delay
            Timer timer = new Timer();
            timer.schedule(new TimerTask() {
                @Override
                public void run() {
                    deliverMessage(message);
                }
            }, networkDelay);
            
            return true;
        }
        
        private void deliverMessage(RobotMessage message) {
            if (message.getReceiverId() == -1) {
                //Broadcast message
                for (Robot robot : robots.values()) {
                    if (robot.getId() != message.getSenderId()) {
                        robot.receiveMessage(message);
                    }
                }
            } else {
                //Unicast message
                Robot receiver = robots.get(message.getReceiverId());
                if (receiver != null) {
                    receiver.receiveMessage(message);
                } else {
                    System.out.println("[NETWORK] Robot " + message.getReceiverId() + " not found");
                }
            }
        }
        
        public void setPacketLossRate(double rate) {
            this.packetLossRate = Math.max(0.0, Math.min(1.0, rate));
        }
        
        public void setNetworkDelay(int delay) {
            this.networkDelay = Math.max(0, delay);
        }
        
        public Map<Integer, Robot> getRobots() {
            return new HashMap<>(robots);
        }
    }
    
    //Robot class with communication capabilities
    static class Robot {
        private int id;
        private String name;
        private Position position;
        private RobotStatus status;
        private NetworkSimulator network;
        private Queue<RobotMessage> incomingMessages;
        private int sequenceNumber;
        private Map<Integer, Integer> lastReceivedSequence;
        private ExecutorService messageProcessor;
        private volatile boolean running;
        
        public Robot(int id, String name, Position initialPosition, NetworkSimulator network) {
            this.id = id;
            this.name = name;
            this.position = initialPosition;
            this.network = network;
            this.status = new RobotStatus(id, "IDLE", 1.0, initialPosition);
            this.incomingMessages = new ConcurrentLinkedQueue<>();
            this.sequenceNumber = 0;
            this.lastReceivedSequence = new ConcurrentHashMap<>();
            this.messageProcessor = Executors.newSingleThreadExecutor();
            this.running = true;
            
            //Start message processing thread
            messageProcessor.submit(this::processMessages);
        }
        
        public void sendMessage(int receiverId, MessageType type, byte[] payload) {
            RobotMessage message = new RobotMessage(id, receiverId, type, payload, ++sequenceNumber);
            
            System.out.println("[ROBOT " + id + "] Sending: " + message);
            
            if (!network.sendMessage(message)) {
                System.out.println("[ROBOT " + id + "] Failed to send message");
            }
        }
        
        public void broadcastMessage(MessageType type, byte[] payload) {
            sendMessage(-1, type, payload);
        }
        
        public void receiveMessage(RobotMessage message) {
            if (!message.verifyChecksum()) {
                System.out.println("[ROBOT " + id + "] Checksum verification failed for: " + message);
                return;
            }
            
            //Check for duplicate messages
            Integer lastSeq = lastReceivedSequence.get(message.getSenderId());
            if (lastSeq != null && message.getSequenceNumber() <= lastSeq) {
                System.out.println("[ROBOT " + id + "] Duplicate message ignored: " + message);
                return;
            }
            
            lastReceivedSequence.put(message.getSenderId(), message.getSequenceNumber());
            incomingMessages.offer(message);
        }
        
        private void processMessages() {
            while (running) {
                RobotMessage message = incomingMessages.poll();
                if (message != null) {
                    handleMessage(message);
                } else {
                    try {
                        Thread.sleep(10);
                    } catch (InterruptedException e) {
                        break;
                    }
                }
            }
        }
        
        private void handleMessage(RobotMessage message) {
            System.out.println("[ROBOT " + id + "] Received: " + message);
            
            switch (message.getType()) {
                case HEARTBEAT:
                    handleHeartbeat(message);
                    break;
                case POSITION_UPDATE:
                    handlePositionUpdate(message);
                    break;
                case TASK_ASSIGNMENT:
                    handleTaskAssignment(message);
                    break;
                case STATUS_REPORT:
                    handleStatusReport(message);
                    break;
                case EMERGENCY_STOP:
                    handleEmergencyStop(message);
                    break;
                case COORDINATION_REQUEST:
                    handleCoordinationRequest(message);
                    break;
                case SENSOR_DATA:
                    handleSensorData(message);
                    break;
                case ACKNOWLEDGMENT:
                    handleAcknowledgment(message);
                    break;
            }
        }
        
        private void handleHeartbeat(RobotMessage message) {
            //Send acknowledgment
            sendMessage(message.getSenderId(), MessageType.ACKNOWLEDGMENT, 
                       ("heartbeat_ack_" + message.getSequenceNumber()).getBytes());
        }
        
        private void handlePositionUpdate(RobotMessage message) {
            Position pos = Position.fromBytes(message.getPayload());
            System.out.println("[ROBOT " + id + "] Robot " + message.getSenderId() + " position: " + pos);
        }
        
        private void handleTaskAssignment(RobotMessage message) {
            TaskAssignment task = TaskAssignment.fromBytes(message.getPayload());
            System.out.println("[ROBOT " + id + "] Assigned task: " + task);
            
            status.currentTask = task.taskId;
            status.status = "WORKING";
            
            //Send acknowledgment
            sendMessage(message.getSenderId(), MessageType.ACKNOWLEDGMENT, 
                       ("task_accepted_" + task.taskId).getBytes());
        }
        
        private void handleStatusReport(RobotMessage message) {
            RobotStatus robotStatus = RobotStatus.fromBytes(message.getPayload());
            System.out.println("[ROBOT " + id + "] Status from robot " + message.getSenderId() + ": " + robotStatus);
        }
        
        private void handleEmergencyStop(RobotMessage message) {
            System.out.println("[ROBOT " + id + "] EMERGENCY STOP received from robot " + message.getSenderId());
            status.status = "EMERGENCY_STOP";
            
            //Broadcast acknowledgment
            broadcastMessage(MessageType.ACKNOWLEDGMENT, "emergency_stop_ack".getBytes());
        }
        
        private void handleCoordinationRequest(RobotMessage message) {
            String request = new String(message.getPayload());
            System.out.println("[ROBOT " + id + "] Coordination request: " + request);
            
            //Simple coordination response
            String response = "coordination_response_from_" + id;
            sendMessage(message.getSenderId(), MessageType.ACKNOWLEDGMENT, response.getBytes());
        }
        
        private void handleSensorData(RobotMessage message) {
            String sensorData = new String(message.getPayload());
            System.out.println("[ROBOT " + id + "] Sensor data from robot " + message.getSenderId() + ": " + sensorData);
        }
        
        private void handleAcknowledgment(RobotMessage message) {
            String ackData = new String(message.getPayload());
            System.out.println("[ROBOT " + id + "] Acknowledgment: " + ackData);
        }
        
        public void sendHeartbeat() {
            broadcastMessage(MessageType.HEARTBEAT, ("heartbeat_" + System.currentTimeMillis()).getBytes());
        }
        
        public void sendPositionUpdate() {
            broadcastMessage(MessageType.POSITION_UPDATE, position.toBytes());
        }
        
        public void sendStatusReport() {
            status.currentPosition = position;
            broadcastMessage(MessageType.STATUS_REPORT, status.toBytes());
        }
        
        public void assignTask(int targetRobotId, TaskAssignment task) {
            sendMessage(targetRobotId, MessageType.TASK_ASSIGNMENT, task.toBytes());
        }
        
        public void sendEmergencyStop() {
            broadcastMessage(MessageType.EMERGENCY_STOP, "emergency_stop".getBytes());
        }
        
        public void updatePosition(double x, double y, double z, double heading) {
            position = new Position(x, y, z, heading);
            status.currentPosition = position;
        }
        
        public void updateBatteryLevel(double level) {
            status.batteryLevel = Math.max(0.0, Math.min(1.0, level));
        }
        
        public void shutdown() {
            running = false;
            messageProcessor.shutdown();
        }
        
        //Getters
        public int getId() { return id; }
        public String getName() { return name; }
        public Position getPosition() { return position; }
        public RobotStatus getStatus() { return status; }
        
        @Override
        public String toString() {
            return String.format("Robot[%d: %s at %s]", id, name, position);
        }
    }
    
    /**
     * Demonstration and testing
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("Robot Communication Protocol System - Demonstration\n");
        
        // Test 1: Network setup and robot creation
        System.out.println("Test 1: Network Setup and Robot Creation");
        System.out.println("----------------------------------------");
        
        NetworkSimulator network = new NetworkSimulator(0.05, 100); // 5% packet loss, 100ms delay
        
        Robot robot1 = new Robot(1, "Explorer", new Position(0, 0, 0, 0), network);
        Robot robot2 = new Robot(2, "Worker", new Position(10, 5, 0, Math.PI/2), network);
        Robot robot3 = new Robot(3, "Guardian", new Position(-5, 10, 0, Math.PI), network);
        
        network.addRobot(robot1);
        network.addRobot(robot2);
        network.addRobot(robot3);
        
        System.out.println("Created 3 robots:");
        for (Robot robot : network.getRobots().values()) {
            System.out.println("  " + robot);
        }
        
        Thread.sleep(200); // Allow network setup
        System.out.println("\n" + "=".repeat(60));
        
        // Test 2: Basic message exchange
        System.out.println("\nTest 2: Basic Message Exchange");
        System.out.println("-------------------------------");
        
        System.out.println("\nSending heartbeat messages...");
        robot1.sendHeartbeat();
        robot2.sendHeartbeat();
        robot3.sendHeartbeat();
        
        Thread.sleep(500);
        
        System.out.println("\nSending position updates...");
        robot1.sendPositionUpdate();
        robot2.sendPositionUpdate();
        robot3.sendPositionUpdate();
        
        Thread.sleep(500);
        System.out.println("\n" + "=".repeat(60));
        
        // Test 3: Task assignment
        System.out.println("\nTest 3: Task Assignment");
        System.out.println("-----------------------");
        
        TaskAssignment task1 = new TaskAssignment("TASK_001", "PATROL", new Position(20, 20, 0, 0));
        task1.addParameter("speed", "2.0");
        task1.addParameter("duration", "300");
        
        TaskAssignment task2 = new TaskAssignment("TASK_002", "COLLECT", new Position(15, -10, 0, Math.PI/4));
        task2.addParameter("object_type", "sample");
        task2.addParameter("container", "A1");
        
        System.out.println("\nAssigning tasks...");
        robot1.assignTask(2, task1); // Robot 1 assigns task to Robot 2
        robot1.assignTask(3, task2); // Robot 1 assigns task to Robot 3
        
        Thread.sleep(500);
        System.out.println("\n" + "=".repeat(60));
        
        // Test 4: Status reporting
        System.out.println("\nTest 4: Status Reporting");
        System.out.println("------------------------");
        
        // Update robot statuses
        robot1.updateBatteryLevel(0.85);
        robot1.getStatus().status = "COORDINATING";
        robot1.getStatus().addSensorReading("temperature", 23.5);
        robot1.getStatus().addSensorReading("humidity", 45.2);
        
        robot2.updateBatteryLevel(0.72);
        robot2.updatePosition(12, 8, 0, Math.PI/3);
        robot2.getStatus().addSensorReading("distance", 1.25);
        
        robot3.updateBatteryLevel(0.91);
        robot3.updatePosition(-3, 12, 0, 3*Math.PI/4);
        robot3.getStatus().addSensorReading("light_level", 850.0);
        
        System.out.println("\nSending status reports...");
        robot1.sendStatusReport();
        robot2.sendStatusReport();
        robot3.sendStatusReport();
        
        Thread.sleep(500);
        System.out.println("\n" + "=".repeat(60));
        
        // Test 5: Coordination and sensor data sharing
        System.out.println("\nTest 5: Coordination and Sensor Data Sharing");
        System.out.println("---------------------------------------------");
        
        System.out.println("\nSending coordination requests...");
        robot2.sendMessage(1, MessageType.COORDINATION_REQUEST, 
                          "request_path_coordination_zone_A".getBytes());
        robot3.sendMessage(1, MessageType.COORDINATION_REQUEST, 
                          "request_resource_allocation_sensor_B".getBytes());
        
        Thread.sleep(300);
        
        System.out.println("\nSharing sensor data...");
        robot1.sendMessage(2, MessageType.SENSOR_DATA, 
                          "obstacle_detected:x=15,y=12,size=large".getBytes());
        robot2.sendMessage(3, MessageType.SENSOR_DATA, 
                          "target_found:x=18,y=22,confidence=0.87".getBytes());
        
        Thread.sleep(500);
        System.out.println("\n" + "=".repeat(60));
        
        // Test 6: Emergency stop scenario
        System.out.println("\nTest 6: Emergency Stop Scenario");
        System.out.println("--------------------------------");
        
        System.out.println("\nRobot 3 detects emergency and broadcasts stop signal...");
        robot3.sendEmergencyStop();
        
        Thread.sleep(500);
        System.out.println("\n" + "=".repeat(60));
        
        // Test 7: Network reliability testing
        System.out.println("\nTest 7: Network Reliability Testing");
        System.out.println("------------------------------------");
        
        System.out.println("\nTesting with higher packet loss rate (20%)...");
        network.setPacketLossRate(0.2);
        network.setNetworkDelay(200);
        
        for (int i = 0; i < 5; i++) {
            robot1.sendMessage(2, MessageType.HEARTBEAT, ("test_" + i).getBytes());
            Thread.sleep(100);
        }
        
        Thread.sleep(1000);
        
        // Reset network parameters
        network.setPacketLossRate(0.05);
        network.setNetworkDelay(100);
        
        System.out.println("\n" + "=".repeat(60));
        
        // Test 8: Message serialization and integrity
        System.out.println("\nTest 8: Message Serialization and Integrity");
        System.out.println("--------------------------------------------");
        
        System.out.println("\nTesting message serialization...");
        
        RobotMessage originalMessage = new RobotMessage(1, 2, MessageType.TASK_ASSIGNMENT, 
                                                       "test_payload".getBytes(), 123);
        
        byte[] serialized = originalMessage.serialize();
        RobotMessage deserializedMessage = RobotMessage.deserialize(serialized);
        
        System.out.println("Original: " + originalMessage);
        System.out.println("Deserialized: " + deserializedMessage);
        System.out.println("Checksum valid: " + deserializedMessage.verifyChecksum());
        System.out.println("Serialization size: " + serialized.length + " bytes");
        
        System.out.println("\n" + "=".repeat(60));
        
        // Final status summary
        System.out.println("\nFinal Robot Status Summary");
        System.out.println("--------------------------");
        
        for (Robot robot : network.getRobots().values()) {
            System.out.println(robot.getStatus());
        }
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Robot Communication Demo Complete!");
        System.out.println("This demonstrates multi-robot communication protocols.");
        System.out.println("\nKey Features Demonstrated:");
        System.out.println("- Message-based communication with multiple message types");
        System.out.println("- Network simulation with packet loss and delay");
        System.out.println("- Message serialization and integrity checking");
        System.out.println("- Duplicate message detection and sequence numbering");
        System.out.println("- Task assignment and coordination protocols");
        System.out.println("- Emergency stop and safety protocols");
        System.out.println("- Status reporting and sensor data sharing");
        System.out.println("- Acknowledgment and reliability mechanisms");
        
        // Cleanup
        robot1.shutdown();
        robot2.shutdown();
        robot3.shutdown();
    }
}