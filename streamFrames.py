import cv2
import depthai as dai
import numpy as np
import time

class CameraDefinition:
    def __init__(self) -> None:
        # Create pipeline
        self.pipeline = dai.Pipeline()
        self.camRgb = None
        self.monoRight = None
        self.monoLeft = None
        self.depth = None
        self.xoutRgb = None
        self.xoutDepth = None
        self.xoutDesparity = None
        self.xoutRight = None
        self.xoutLeft = None
        self.xoutRightRec = None
        self.xoutLeftRec = None

        self.cameraRgbNode()
        self.monoRightNode()
        self.monoLeftNode()
        self.depthNode()
        self.xoutRgbNode()
        self.xoutDepthNode()
        self.xoutRightNode()
        self.xoutLeftNode()

    def cameraRgbNode(self) -> None:
        self.camRgb = self.pipeline.create(dai.node.ColorCamera)
        # Properties
        self.camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
        self.camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        self.camRgb.setPreviewSize(640, 400)
        self.camRgb.setFps(50)
        self.camRgb.setInterleaved(False)
    
    def monoRightNode(self) -> None:
        self.monoRight = self.pipeline.create(dai.node.MonoCamera)
        self.monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self.monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
        self.monoRight.setFps(50)

    def monoLeftNode(self) -> None:
        self.monoLeft = self.pipeline.create(dai.node.MonoCamera)
        self.monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self.monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
        #self.monoLeft.setFps(50)

    def depthNode(self) -> None:
        # Closer-in minimum depth, disparity range is doubled (from 95 to 190):
        extended_disparity = False
        # Better accuracy for longer distance, fractional disparity 32-levels:
        subpixel = True
        # Better handling for occlusions:
        lr_check = True
        # Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
        self.depth = self.pipeline.create(dai.node.StereoDepth)
        self.depth.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        # Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
        self.depth.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
        self.depth.setLeftRightCheck(lr_check)
        self.depth.setExtendedDisparity(extended_disparity)
        self.depth.setSubpixel(subpixel)

        # depth configuration
        config = self.depth.initialConfig.get()
        config.postProcessing.speckleFilter.enable = False
        config.postProcessing.speckleFilter.speckleRange = 50
        config.postProcessing.temporalFilter.enable = True
        config.postProcessing.spatialFilter.enable = True
        config.postProcessing.spatialFilter.holeFillingRadius = 2
        config.postProcessing.spatialFilter.numIterations = 1
        config.postProcessing.thresholdFilter.minRange = 200
        config.postProcessing.thresholdFilter.maxRange = 15000
        config.postProcessing.decimationFilter.decimationFactor = 1
        self.depth.initialConfig.set(config)

    def xoutRgbNode(self) -> None:
        # xoutRgb -> for rgb frame output
        self.xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        self.xoutRgb.setStreamName("rgb")
        # Linking rgb Camera
        self.camRgb.preview.link(self.xoutRgb.input)

    def xoutDepthNode(self) -> None:
        self.monoLeft.out.link(self.depth.left)
        self.monoRight.out.link(self.depth.right)

        self.xoutDepth = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDepth.setStreamName("depth")
        self.depth.depth.link(self.xoutDepth.input)

        self.xoutDesparity = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDesparity.setStreamName("disparity")
        self.depth.disparity.link(self.xoutDesparity.input)

        self.xoutRightRec = self.pipeline.create(dai.node.XLinkOut)
        self.xoutRightRec.setStreamName("rightRec")
        self.depth.rectifiedRight.link(self.xoutRightRec.input)

        self.xoutLeftRec = self.pipeline.create(dai.node.XLinkOut)
        self.xoutLeftRec.setStreamName("leftRec")
        self.depth.rectifiedLeft.link(self.xoutLeftRec.input)
    
    def xoutRightNode(self) -> None:
        self.xoutRight = self.pipeline.create(dai.node.XLinkOut)
        self.xoutRight.setStreamName("right")
        self.monoRight.out.link(self.xoutRight.input)

    def xoutLeftNode(self) -> None:
        self.xoutLeft = self.pipeline.create(dai.node.XLinkOut)
        self.xoutLeft.setStreamName("left")
        self.monoLeft.out.link(self.xoutLeft.input)

    def getPipeline(self) -> None:
        return self.pipeline
    
    def getDepthMaxDesparity(self) -> None:
        return self.depth.initialConfig.getMaxDisparity()

oak = CameraDefinition()
pipeLine = oak.getPipeline()
maxDesparity = oak.getDepthMaxDesparity()
cv2.namedWindow("fullView", cv2.WINDOW_NORMAL)
imageCounter = 0
# Connect to device and start pipeline
with dai.Device(pipeLine) as device:
    print('Connected cameras: ', device.getConnectedCameras())
    print('Usb speed: ', device.getUsbSpeed().name)

    # Output queue will be used to get the rgb frames from the output defined in class
    qRgb = device.getOutputQueue(name="rgb",  maxSize=4, blocking=False)
    qDisparity = device.getOutputQueue(name="disparity",  maxSize=4, blocking=False)
    qDepth = device.getOutputQueue(name="depth",  maxSize=4, blocking=False)
    qRight = device.getOutputQueue(name="right",  maxSize=4, blocking=False)
    qLeft = device.getOutputQueue(name="left",  maxSize=4, blocking=False)
    qRightRec = device.getOutputQueue(name="rightRec",  maxSize=4, blocking=False)
    qLeftRec = device.getOutputQueue(name="leftRec",  maxSize=4, blocking=False)
    inDisparity, inDepth, inRight, inLeft, inRightRec, inLeftRec = None, None, None, None, None, None
    merged = np.zeros((400, 640, 3), dtype=np.uint16)
    x = time.time()

    while True:
        inRgb = qRgb.get()
        rgbFrame = inRgb.getCvFrame()

        if inDisparity is None:
            inDisparity = qDisparity.tryGet()

        if inDepth is None:
            inDepth = qDepth.tryGet()

        if inRight is None:
            inRight = qRight.tryGet()

        if inLeft is None:
            inLeft = qLeft.tryGet()

        if inRightRec is None:
            inRightRec = qRightRec.tryGet()

        if inLeftRec is None:
            inLeftRec = qLeftRec.tryGet()

        if inDisparity is not None and inDepth is not None and inRight is not None and inLeft is not None and inRightRec is not None and inLeftRec is not None:
            depth = inDepth.getFrame()
            disparity = (inDisparity.getFrame()*(255 / maxDesparity)).astype(np.uint8)
            right = inRight.getFrame()
            left = inLeft.getFrame()
            rightRec = inRightRec.getFrame()
            leftRec = inLeftRec.getFrame()
            topImage = np.hstack([right, left, disparity])
            bottomImage = np.hstack([rightRec, leftRec])
            topImage = cv2.cvtColor(topImage, cv2.COLOR_GRAY2BGR)
            bottomImage = cv2.cvtColor(bottomImage, cv2.COLOR_GRAY2BGR)
            bottomImage = np.hstack([bottomImage, rgbFrame])
            fullView = np.vstack([topImage, bottomImage])
            cv2.imshow("fullView", fullView)
            inDisparity, inDepth, inRight, inLeft, inRightRec, inLeftRec = None, None, None, None, None, None
    
        #cv2.imshow("RGB", rgbFrame)
        key = cv2.waitKey(1)
        if key == ord("Q") or key == ord("q"):
            break
        if key == ord("X") or key == ord("x"):
            cv2.imwrite("fullview{}.jpg".format(imageCounter), fullView)
            imageCounter += 1
