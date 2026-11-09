"""Camera UX scenarios, using a fake clock/model and no camera or broker."""
import os
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

for key, value in {"MQTT_HOST": "localhost", "MQTT_USER": "test",
                   "MQTT_PASS": "test", "BACKEND_URL": "http://localhost/upload"}.items():
    os.environ.setdefault(key, value)

from config import DIFF_WARMUP, MISS_MAX
from core.detector import Detector, State
from core.frame_diff import FrameDiffer
from core.camera_ui import CameraUI, build_view


class CameraUITests(unittest.TestCase):
    def setUp(self):
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.detector = Detector(1, object(), MagicMock(), MagicMock())
        self.detector._run_yolo = MagicMock(return_value=[("organic", .9, None)])
        self.differ = FrameDiffer()

    def view(self, occupied, now):
        return build_view(self.detector.get_status(now), self.differ.get_status(), occupied)

    def warmup(self):
        for _ in range(DIFF_WARMUP):
            self.differ.has_object(self.frame)

    def classify(self):
        with patch("core.detector.time.time") as clock:
            for now in (0., .2, .4, 1.6):
                clock.return_value = now
                self.detector.process(self.frame, True)

    def test_warmup_progress_then_ready(self):
        self.differ.has_object(self.frame)
        self.assertEqual(self.view(False, 0)["phase"], "WARMUP")
        self.assertAlmostEqual(self.view(False, 0)["progress"], 1 / DIFF_WARMUP)
        for _ in range(DIFF_WARMUP - 1):
            self.differ.has_object(self.frame)
        self.assertEqual(self.view(False, 0)["phase"], "READY")

    def test_object_without_yolo_detection_shows_waiting(self):
        self.warmup()
        self.detector._run_yolo.return_value = []
        self.detector.process(self.frame, True)
        self.assertEqual(self.view(True, 0)["phase"], "WAITING")

    def test_miss_counter_and_cancel_reason_survive_session_reset(self):
        self.warmup()
        with patch("core.detector.time.time", return_value=0):
            self.detector.process(self.frame, True)
        with patch("core.detector.time.time", return_value=.1):
            self.detector.process(self.frame, False)
        self.assertEqual(self.detector.get_status(.1)["miss_count"], 1)
        for _ in range(MISS_MAX - 1):
            with patch("core.detector.time.time", return_value=.2):
                self.detector.process(self.frame, False)
        status = self.detector.get_status(.2)
        self.assertEqual(status["state"], "IDLE")
        self.assertEqual(status["last_event"]["kind"], "cancelled")
        self.assertIn(str(MISS_MAX), status["last_event"]["message"])
        self.detector.publisher.publish_classification.assert_not_called()
        self.detector.publisher.publish_unsure.assert_not_called()

    def test_countdown_zero_still_waits_for_tray_then_ready(self):
        self.warmup()
        self.classify()
        self.assertEqual(self.view(True, 2)["phase"], "COOLDOWN")
        self.assertAlmostEqual(self.detector.get_status(2)["cooldown_remaining"], 7.6)
        with patch("core.detector.time.time", return_value=10):
            self.detector.process(self.frame, True)
        self.assertEqual(self.view(True, 10)["phase"], "REMOVE_WASTE")
        with patch("core.detector.time.time", return_value=10.1):
            self.detector.process(self.frame, False)
        self.assertEqual(self.view(False, 10.1)["phase"], "READY")
        self.assertEqual(self.detector.get_status(10.1)["last_result"]["waste_type"], "organic")

    def test_empty_tray_before_deadline_does_not_skip_countdown(self):
        self.warmup()
        self.classify()
        with patch("core.detector.time.time", return_value=3):
            self.detector.process(self.frame, False)
        self.assertEqual(self.view(False, 3)["phase"], "COOLDOWN")
        self.assertTrue(self.detector.get_status(3)["tray_cleared"])

    def test_uncertain_has_reason_and_preserves_final_votes(self):
        self.detector._votes.update({"organic": 4, "recyclable": 3})
        self.detector._finalize()
        status = self.detector.get_status()
        self.assertEqual(status["last_result"]["outcome"], "uncertain")
        self.assertEqual(status["last_result"]["votes"], {"organic": 4, "recyclable": 3})
        self.assertEqual(status["last_event"]["kind"], "uncertain")

    def test_publish_failure_is_visible_and_not_reported_as_delivered(self):
        self.detector.publisher.publish_classification.side_effect = RuntimeError("offline")
        self.classify()
        status = self.detector.get_status()
        self.assertEqual(status["last_result"]["mqtt"], "error")
        self.assertTrue(any(event["kind"] == "error" for event in status["events"]))

    def test_render_does_not_modify_camera_frame_or_stored_evidence(self):
        self.warmup()
        self.classify()
        original = self.frame.copy()
        ui = CameraUI(1)
        rendered = ui.render(self.frame, self.detector.get_status(2), self.differ.get_status(), True)
        self.assertGreater(rendered.shape[1], self.frame.shape[1])
        self.assertTrue(np.array_equal(self.frame, original))
        self.assertGreater(np.count_nonzero(rendered), 0)

    def test_repeated_frames_do_not_flood_event_history(self):
        self.detector._run_yolo.return_value = []
        for _ in range(100):
            self.detector.process(self.frame, True)
        self.assertLessEqual(len(self.detector.get_status()["events"]), 1)

    def test_too_few_votes_explains_uncertain_result(self):
        self.detector._votes.update({"organic": 2})
        self.detector._finalize()
        result = self.detector.get_status()["last_result"]
        self.assertEqual(result["outcome"], "uncertain")
        self.assertIn("phiếu tối thiểu", result["reason"])

    def test_uncertain_publish_failure_still_enters_cooldown(self):
        self.detector._votes.update({"organic": 2})
        self.detector.publisher.publish_unsure.side_effect = RuntimeError("offline")
        self.detector._finalize()
        self.assertEqual(self.detector.state, State.COOLDOWN)
        self.assertTrue(any(e["kind"] == "error" for e in self.detector.get_status()["events"]))

    def test_quit_from_camera_window_stops_worker_and_cleans_resources(self):
        import worker
        with patch.object(worker, "MODEL_PATH"), patch.object(worker, "load_model") as model, \
             patch.object(worker, "CameraStream") as camera, patch.object(worker, "MqttPublisher") as mqtt, \
             patch.object(worker, "Uploader") as uploader, patch.object(worker, "CameraUI") as ui:
            model.return_value.names = {0: "organic-waste", 1: "inorganic-waste", 2: "recyclable waste"}
            camera.return_value.read.return_value = self.frame
            ui.return_value.show.return_value = False
            worker.main(1)
            camera.return_value.read.assert_called_once()
            camera.return_value.release.assert_called_once()
            ui.return_value.close.assert_called_once()
            uploader.return_value.close.assert_called_once()
            mqtt.return_value.publish_offline.assert_called_once()
            mqtt.return_value.disconnect.assert_called_once()

    def test_headless_worker_does_not_create_camera_window(self):
        import worker
        with patch.object(worker, "MODEL_PATH"), patch.object(worker, "load_model") as model, \
             patch.object(worker, "CameraStream") as camera, patch.object(worker, "MqttPublisher"), \
             patch.object(worker, "Uploader"), patch.object(worker, "CameraUI") as ui:
            model.return_value.names = {0: "organic-waste", 1: "inorganic-waste", 2: "recyclable waste"}
            camera.return_value.read.side_effect = KeyboardInterrupt
            worker.main(1, show_ui=False)
            ui.assert_not_called()


if __name__ == "__main__":
    unittest.main()
