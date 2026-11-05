import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np

os.environ.setdefault("MQTT_HOST", "localhost")
os.environ.setdefault("MQTT_USER", "test")
os.environ.setdefault("MQTT_PASS", "test")
os.environ.setdefault("BACKEND_URL", "http://localhost/upload")

from config import DIFF_WARMUP
from core.detector import Detector, State
from core.frame_diff import FrameDiffer


class PipelineTests(unittest.TestCase):
    def test_frame_differ_announces_when_background_is_ready_once(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        differ = FrameDiffer()
        with patch("builtins.print") as output:
            for _ in range(DIFF_WARMUP - 1):
                differ.has_object(frame)
            output.assert_not_called()
            differ.has_object(frame)
            output.assert_called_once_with(f"[FrameDiffer] Captured {DIFF_WARMUP} background frames; detection ready")
            differ.has_object(frame)
            output.assert_called_once()

    def test_frame_differ_detects_stationary_object_against_empty_tray(self):
        differ = FrameDiffer()
        empty = np.zeros((100, 100, 3), dtype=np.uint8)
        occupied = empty.copy()
        occupied[25:75, 25:75] = 255
        for _ in range(DIFF_WARMUP):
            self.assertFalse(differ.has_object(empty))
        for _ in range(2):
            self.assertFalse(differ.has_object(occupied))
        self.assertTrue(differ.has_object(occupied))
        self.assertTrue(differ.has_object(occupied))
        self.assertFalse(differ.has_object(empty))

    def test_frame_differ_ignores_changes_outside_detector_roi(self):
        empty = np.zeros((100, 100, 3), dtype=np.uint8)
        outside = empty.copy()
        outside[:25, :25] = 255
        inside = empty.copy()
        inside[40:60, 40:60] = 255
        with patch("core.frame_diff.ROI_SIZE", 40):
            differ = FrameDiffer()
            for _ in range(DIFF_WARMUP):
                differ.has_object(empty)
            for _ in range(4):
                self.assertFalse(differ.has_object(outside))
            for _ in range(2):
                self.assertFalse(differ.has_object(inside))
            self.assertTrue(differ.has_object(inside))

    def test_roi_is_square_when_camera_is_wider_than_tall(self):
        empty = np.zeros((80, 120, 3), dtype=np.uint8)
        outside = empty.copy()
        outside[:, :15] = 255
        with patch("core.detector.ROI_SIZE", 100), patch("core.frame_diff.ROI_SIZE", 100):
            detector = Detector(1, object(), MagicMock(), MagicMock())
            self.assertEqual(detector._crop_roi(empty).shape, (80, 80, 3))
            differ = FrameDiffer()
            for _ in range(DIFF_WARMUP):
                differ.has_object(empty)
            for _ in range(4):
                self.assertFalse(differ.has_object(outside))

    def test_detector_waits_for_empty_tray_before_new_session(self):
        publisher = MagicMock()
        detector = Detector(1, object(), publisher, MagicMock())
        detector._run_yolo = lambda frame: [("recyclable", 0.9, None)]
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        with patch("core.detector.time.time") as clock:
            for moment in (0.0, 0.2, 0.4, 1.6):
                clock.return_value = moment
                detector.process(frame, True)
            self.assertEqual(detector.state, State.COOLDOWN)
            self.assertEqual(publisher.publish_classification.call_count, 1)
            clock.return_value = 10.0
            detector.process(frame, True)
            self.assertEqual(detector.state, State.COOLDOWN)
            clock.return_value = 10.1
            detector.process(frame, False)
            self.assertEqual(detector.state, State.IDLE)
            clock.return_value = 10.2
            detector.process(frame, True)
            self.assertEqual(detector.state, State.DETECTING)

    def test_detector_keeps_final_label_for_camera_preview(self):
        detector = Detector(1, object(), MagicMock(), MagicMock())
        detector._votes.update({"recyclable": 3})
        detector._best_frames["recyclable"] = (0.9, np.zeros((20, 20, 3), dtype=np.uint8))
        detector._finalize()
        self.assertEqual(detector.last_result, "recyclable")
        detector._start_detecting(1.0)
        self.assertIsNone(detector.last_result)

    def test_detector_analyzes_roi_but_uploads_full_frame(self):
        uploader = MagicMock()
        detector = Detector(1, object(), MagicMock(), uploader)
        detector._run_yolo = MagicMock(return_value=[("recyclable", 0.9, None)])
        frame = np.full((80, 120, 3), 127, dtype=np.uint8)

        with patch("core.detector.ROI_SIZE", 40), patch("core.detector.time.time") as clock:
            for moment in (0.0, 0.2, 0.4, 1.6):
                clock.return_value = moment
                detector.process(frame, True)

        self.assertEqual([call.args[0].shape for call in detector._run_yolo.call_args_list], [(40, 40, 3)] * 3)
        image_bytes = uploader.submit.call_args.args[1]
        uploaded_image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        self.assertEqual(uploaded_image.shape, frame.shape)

    def test_dominance_requires_winner_to_have_twice_runner_up_votes(self):
        frame = np.zeros((20, 20, 3), dtype=np.uint8)
        for second_votes, should_classify in ((5, True), (9, False)):
            with self.subTest(second_votes=second_votes):
                publisher = MagicMock()
                detector = Detector(1, object(), publisher, MagicMock())
                detector._votes.update({"recyclable": 10, "organic": second_votes})
                detector._best_frames["recyclable"] = (0.9, frame)
                detector._finalize()
                self.assertEqual(publisher.publish_classification.called, should_classify)
                self.assertEqual(publisher.publish_unsure.called, not should_classify)

    def test_mqtt_publishes_contract_with_qos_and_retain(self):
        from core import mqtt_pub

        client = MagicMock()
        client.connect.return_value = 0
        client.publish.return_value.rc = 0
        with patch.object(mqtt_pub.mqtt, "Client", return_value=client):
            publisher = mqtt_pub.MqttPublisher(1)
        will = client.will_set.call_args
        self.assertEqual(will.args[0], "school/area1/status/ai")
        self.assertEqual(json.loads(will.args[1]), {"status": "offline"})
        self.assertEqual(will.kwargs, {"qos": 1, "retain": True})
        client.on_connect(client, None, None, 0, None)
        self.assertEqual(json.loads(client.publish.call_args.args[1]), {"status": "online"})
        self.assertEqual(client.publish.call_args.kwargs, {"qos": 1, "retain": True})
        client.tls_set.assert_called_once()
        publisher.publish_classification("00000000-0000-4000-8000-000000000001", "recyclable", 0.9, "2026-09-10T14:32:07Z")
        sent = client.publish.call_args
        self.assertEqual(sent.args[0], "school/area1/classification")
        self.assertEqual(json.loads(sent.args[1])["waste_type"], "recyclable")
        self.assertEqual(sent.kwargs, {"qos": 1, "retain": False})
        publisher.publish_unsure()
        self.assertEqual(client.publish.call_args.args[0], "school/area1/uncertain")
        self.assertEqual(client.publish.call_args.kwargs, {"qos": 1, "retain": False})
        publisher.publish_offline()
        self.assertEqual(json.loads(client.publish.call_args.args[1]), {"status": "offline"})
        self.assertEqual(client.publish.call_args.kwargs, {"qos": 1, "retain": True})

    def test_successful_upload_posts_image_and_log_id(self):
        from core import uploader

        log_id = "00000000-0000-4000-8000-000000000002"
        with tempfile.TemporaryDirectory() as folder, patch.object(uploader, "LOCAL_IMAGE_DIR", Path(folder)):
            with patch.object(uploader.requests, "post") as post:
                sender = uploader.Uploader()
                sender.submit(log_id, b"jpeg")
                sender.close()
            self.assertEqual(post.call_args.kwargs["data"], {"log_id": log_id})
            self.assertEqual(post.call_args.kwargs["files"]["file"][1], b"jpeg")
            self.assertFalse((Path(folder) / log_id).exists())

    def test_failed_upload_is_saved_for_manual_recovery(self):
        from core import uploader

        log_id = "00000000-0000-4000-8000-000000000001"
        with tempfile.TemporaryDirectory() as folder, patch.object(uploader, "LOCAL_IMAGE_DIR", Path(folder)):
            with patch.object(uploader.requests, "post", side_effect=uploader.requests.ConnectionError):
                sender = uploader.Uploader()
                sender.submit(log_id, b"jpeg")
                sender.close()
            self.assertEqual((Path(folder) / log_id / "frame.jpg").read_bytes(), b"jpeg")
            self.assertIn(log_id, (Path(folder) / log_id / "meta.txt").read_text())

    def test_worker_passes_empty_frames_to_detector_and_cleans_up(self):
        import worker

        frame = np.zeros((20, 20, 3), dtype=np.uint8)
        frame[:5] = 255
        with patch.object(worker, "YOLO") as model_loader, patch.object(worker, "CameraStream") as camera_type, patch.object(worker, "MqttPublisher") as publisher_type, patch.object(worker, "Uploader") as uploader_type, patch.object(worker, "FrameDiffer") as differ_type, patch.object(worker, "Detector") as detector_type, patch.object(worker.cv2, "namedWindow") as named_window, patch.object(worker.cv2, "setWindowProperty") as window_property, patch.object(worker.cv2, "imshow"), patch.object(worker.cv2, "waitKey", return_value=-1), patch.object(worker.cv2, "destroyAllWindows"):
            model_loader.return_value.names = {0: "inorganic-waste", 1: "organic-waste", 2: "recyclable-waste"}
            camera_type.return_value.read.side_effect = [frame, KeyboardInterrupt()]
            differ_type.return_value.has_object.return_value = False
            differ_type.return_value._warmup_count = 1
            worker.main(1)
            np.testing.assert_array_equal(differ_type.return_value.has_object.call_args.args[0], frame[5:])
            np.testing.assert_array_equal(detector_type.return_value.process.call_args.args[0], frame[5:])
            self.assertFalse(np.any(detector_type.return_value.process.call_args.args[0]))
            camera_type.return_value.release.assert_called_once()
            uploader_type.return_value.close.assert_called_once()
            publisher_type.return_value.publish_offline.assert_called_once()
            publisher_type.return_value.disconnect.assert_called_once()
            named_window.assert_called_once_with("AI area 1", worker.cv2.WINDOW_NORMAL)
            window_property.assert_called_once_with("AI area 1", worker.cv2.WND_PROP_FULLSCREEN, worker.cv2.WINDOW_FULLSCREEN)

    def test_worker_preview_shows_roi_and_background_progress(self):
        import worker

        frame = np.zeros((80, 120, 3), dtype=np.uint8)
        differ = MagicMock(_warmup_count=5)
        detector = MagicMock(last_result=None, state=State.IDLE)
        with patch.object(worker, "ROI_SIZE", 40), patch.object(worker.cv2, "imshow") as imshow, patch.object(worker.cv2, "waitKey", return_value=ord("q")), patch.object(worker.ImageDraw.ImageDraw, "text") as text_draw:
            self.assertTrue(worker.show_preview(frame, differ, detector, 1))
        self.assertTrue(any("5/30" in str(call.args[1]) for call in text_draw.call_args_list))
        self.assertTrue(all(not (20 <= call.args[0][0] < 140 and 80 <= call.args[0][1] < 160) for call in text_draw.call_args_list))
        imshow.assert_called_once()
        self.assertEqual(imshow.call_args.args[1].shape, (400, 440, 3))
        np.testing.assert_array_equal(imshow.call_args.args[1][100, 60], [110, 215, 245])

        differ._warmup_count = DIFF_WARMUP
        for result, label in (("recyclable", "Rác tái chế"), ("organic", "Rác hữu cơ"), ("inorganic", "Rác vô cơ"), ("uncertain", "Chưa xác định")):
            with self.subTest(result=result):
                detector.last_result = result
                with patch.object(worker.ImageDraw.ImageDraw, "text") as text_draw, patch.object(worker.cv2, "imshow"), patch.object(worker.cv2, "waitKey", return_value=-1):
                    self.assertFalse(worker.show_preview(frame, differ, detector, 1))
                self.assertTrue(any(label == call.args[1] for call in text_draw.call_args_list))

        wide_frame = np.zeros((480, 1140, 3), dtype=np.uint8)
        with patch.object(worker.cv2, "imshow") as imshow, patch.object(worker.cv2, "waitKey", return_value=-1):
            worker.show_preview(wide_frame, differ, detector, 1)
        self.assertEqual(imshow.call_args.args[1].shape[1], 1460)


if __name__ == "__main__":
    unittest.main()
