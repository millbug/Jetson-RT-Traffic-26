import sys
import csv
import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
from vision_msgs.msg import ObjectHypothesisWithPose
from math import sqrt
from datetime import datetime

# ----- To Run the node -----
# ros2 run inputCSVSubscriber inputCSVSubscriber 

# A node that subscribes to /tracked_object_summary to put data into CSV
class ObjectSubscriber(Node):
    def __init__(self, name):
        super().__init__('tracked_object_subscriber')
        self.name = name
        
        # Subscriber to /tracked_object_summary
        self.sub_ = self.create_subscription(Detection2DArray, '/tracked_object_summary', self.callback, 10)
        self.count = 0

        # Open csv once and add the header
        #self.file = open("csv/test3.csv", "w", newline="")
        self.file = open(f"csv/{self.name}.csv", "w", newline="")
        self.write = csv.writer(self.file) # ensure setup is complete elsewhere
        self.write.writerow(["Class ID", "ID", "Confidence LV", "x_initial", "y_initial", "x_mid1", "y_mid1", "x_mid2", "y_mid2", "x_mid3", "y_mid3", "x_final", "y_final", "datetime"])
    
def callback(self, msg):

    # Loop through completed vehicle tracks
    for detection in msg.detections:

        # Make sure all five points are available
        if len(detection.results) < 5:
            self.get_logger().warning(
                f"Vehicle ID #{detection.id} does not have 5 trajectory points"
            )
            continue

        class_id = detection.results[0].hypothesis.class_id
        confidence = detection.results[0].hypothesis.score
        object_id = detection.id

        # Extract all five trajectory points
        points = []

        for result in detection.results[:5]:

            x = result.pose.pose.position.x
            y = result.pose.pose.position.y

            points.append((x, y))

        # Initial point
        x_initial, y_initial = points[0]

        # First midpoint
        x_mid1, y_mid1 = points[1]

        # Second midpoint
        x_mid2, y_mid2 = points[2]

        # Third midpoint
        x_mid3, y_mid3 = points[3]

        # Final point
        x_final, y_final = points[4]

        # Only write objects with confidence >= 50%
        if confidence >= 0.5:

            self.count += 1

            self.get_logger().info(
                f"Current count: {self.count}"
            )

            self.get_logger().info(
                f"Detected {class_id} ID #{object_id}\n"
                f"Point 1: ({x_initial:.1f}, {y_initial:.1f})\n"
                f"Point 2: ({x_mid1:.1f}, {y_mid1:.1f})\n"
                f"Point 3: ({x_mid2:.1f}, {y_mid2:.1f})\n"
                f"Point 4: ({x_mid3:.1f}, {y_mid3:.1f})\n"
                f"Point 5: ({x_final:.1f}, {y_final:.1f})"
            )

            # Write all five points to CSV
            self.write.writerow([
                class_id,
                object_id,
                f"{confidence:.4f}",

                x_initial,
                y_initial,

                x_mid1,
                y_mid1,

                x_mid2,
                y_mid2,

                x_mid3,
                y_mid3,

                x_final,
                y_final
            ])

def main():
    # Parse command-line argument
    if (len(sys.argv) > 1):
        filename = sys.argv[1] # Grab the filename from cmd line
    else:
        filename = "default"

    rclpy.init()
    node = ObjectSubscriber(filename)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

