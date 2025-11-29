from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # uses your model
results = model("https://ultralytics.com/images/bus.jpg")

print(results[0].boxes)  # should print detected bus/clusters
