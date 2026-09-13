import sys
import unittest
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from demo_logic import (Counter, MINUS_QR, PLUS_QR, metrics, now_taipei,
                        progress_palette, sample_orders, validate_report_columns)


class DemoLogicTests(unittest.TestCase):
    def test_counter_repeated_code_counts_distinct_events_and_allows_over_target(self):
        state = Counter(target=1).scan(PLUS_QR, "a").scan(PLUS_QR, "b")
        self.assertEqual(state.completed, 2)
        self.assertEqual(metrics(state.target, state.completed),
                         {"target": 1, "completed": 2, "rate": 200.0, "remaining": 0})

    def test_transport_retry_and_zero_undo_are_idempotent(self):
        state = Counter().scan(MINUS_QR, "undo-zero").scan(PLUS_QR, "plus")
        self.assertEqual(state.scan(MINUS_QR, "undo-zero").completed, 1)
        self.assertEqual(state.scan(PLUS_QR, "plus").completed, 1)
        self.assertEqual(state.scan(MINUS_QR, "new-undo").completed, 0)

    def test_target_changes_keep_completed(self):
        state = Counter().scan(PLUS_QR, "a").set_target(100)
        self.assertEqual((state.target, state.completed), (100, 1))
        for target in (0, -1, True, 1.5, 1000000000):
            with self.assertRaises(ValueError):
                state.set_target(target)

    def test_unknown_code_cannot_count(self):
        with self.assertRaises(ValueError):
            Counter().scan("random", "a")

    def test_delivered_is_deducted_and_multiple_identical_barcodes_make_one_unit(self):
        state = sample_orders()[0]
        self.assertEqual(state.target, 3)
        state = state.scan("same").scan("same")
        self.assertEqual((state.completed, state.pending), (0, 2))
        state = state.scan("same")
        self.assertEqual((state.completed, state.pending), (1, 0))
        self.assertEqual(state.barcodes, ("same", "same", "same"))

    def test_order_cap_and_undo_allow_correcting_completed_group(self):
        state = sample_orders()[0]
        for _ in range(state.target * state.required):
            state = state.scan("same")
        with self.assertRaises(ValueError):
            state.scan("same")
        state = state.undo()
        self.assertEqual((state.completed, state.pending), (2, 2))
        self.assertEqual(state.scan("correction").completed, 3)

    def test_visitors_start_with_independent_state(self):
        first, second = sample_orders(), sample_orders()
        first[0] = first[0].scan("same")
        self.assertEqual(second[0].barcodes, ())

    def test_progress_thresholds(self):
        self.assertEqual(progress_palette(20)[2], "起步階段")
        self.assertEqual(progress_palette(20.1)[2], "進行中")
        self.assertEqual(progress_palette(80)[2], "進行中")
        self.assertEqual(progress_palette(80.1)[2], "接近目標")
        self.assertEqual(progress_palette(100)[2], "已達標")

    def test_report_missing_column_blocks(self):
        self.assertEqual(validate_report_columns(["訂單", "項次", "預排數量"]), ["完成數量"])
        self.assertEqual(validate_report_columns(["訂單", "項次", "預排數量", "完成數量"]), [])

    def test_clock_uses_taipei(self):
        self.assertEqual(now_taipei().utcoffset(), timedelta(hours=8))


class AppTests(unittest.TestCase):
    def start(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_all_cases_and_methods_render(self):
        app = self.start()
        for index in range(4):
            app.selectbox(key="case").select_index(index).run()
            self.assertEqual(len(app.exception), 0)
        app.radio(key="page").set_value("設計方法").run()
        self.assertEqual(len(app.exception), 0)

    def test_counter_buttons_and_target_update(self):
        app = self.start()
        app.radio(key="page").set_value("互動體驗").run()
        app.button(key="counter_plus").click().run()
        app.button(key="counter_plus").click().run()
        app.number_input(key="counter_target").set_value(1).run()
        self.assertEqual(app.session_state.counter.completed, 2)
        app.button(key="counter_minus").click().run()
        self.assertEqual(app.session_state.counter.completed, 1)
        self.assertEqual(len(app.exception), 0)

    def test_counter_target_survives_navigation(self):
        app = self.start()
        app.radio(key="page").set_value("互動體驗").run()
        app.number_input(key="counter_target").set_value(37).run()
        app.button(key="counter_plus").click().run()
        app.radio(key="demo_mode").set_value("工單派工看板").run()
        app.radio(key="demo_mode").set_value("QR 簡易計數").run()
        self.assertEqual(app.number_input(key="counter_target").value, 37)
        self.assertEqual(app.session_state.counter.completed, 1)
        self.assertEqual(len(app.exception), 0)

    def test_order_scan_complete_and_undo(self):
        app = self.start()
        app.radio(key="page").set_value("互動體驗").run()
        app.radio(key="demo_mode").set_value("工單派工看板").run()
        for _ in range(3):
            app.button(key="order_scan").click().run()
        self.assertEqual(app.session_state.orders[0].completed, 1)
        app.button(key="order_undo").click().run()
        self.assertEqual(app.session_state.orders[0].completed, 0)
        self.assertEqual(app.session_state.orders[0].pending, 2)
        self.assertEqual(len(app.exception), 0)

    def test_report_validation_changes_feedback(self):
        app = self.start()
        app.radio(key="page").set_value("互動體驗").run()
        app.radio(key="demo_mode").set_value("報表資料檢核").run()
        self.assertEqual(len(app.success), 1)
        app.toggle(key="invalid_schema").set_value(True).run()
        self.assertEqual(len(app.error), 1)
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
