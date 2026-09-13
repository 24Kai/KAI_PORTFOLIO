"""Isolated, in-memory demonstrations. No connection to production systems."""
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone

TAIPEI = timezone(timedelta(hours=8), name="Asia/Taipei")
PLUS_QR = "DEMO-COMPLETE-1"
MINUS_QR = "DEMO-UNDO-1"


def now_taipei():
    return datetime.now(TAIPEI)


def metrics(target: int, completed: int) -> dict:
    return {"target": target, "completed": completed,
            "rate": completed / target * 100 if target else 0.0,
            "remaining": max(target - completed, 0)}


def progress_palette(rate: float) -> tuple[str, str, str]:
    if rate >= 100:
        return "#079d50", "#2aeb84", "已達標"
    if rate > 80:
        return "#269264", "#79e5a6", "接近目標"
    if rate > 20:
        return "#c68d26", "#ffe37c", "進行中"
    return "#b6364d", "#ff6478", "起步階段"


@dataclass(frozen=True)
class Counter:
    target: int = 20
    completed: int = 0
    receipts: frozenset[str] = field(default_factory=frozenset)

    def set_target(self, target: int):
        if isinstance(target, bool) or not isinstance(target, int) or not 1 <= target <= 999999999:
            raise ValueError("每日目標必須是 1 至 999,999,999 的整數。")
        return replace(self, target=target)

    def scan(self, token: str, event_id: str):
        if token.strip() not in (PLUS_QR, MINUS_QR):
            raise ValueError("這不是示範計數或撤銷條碼，數量維持不變。")
        if not event_id:
            raise ValueError("缺少事件識別碼。")
        if event_id in self.receipts:
            return self
        delta = -1 if token.strip() == MINUS_QR else 1
        return replace(self, completed=max(self.completed + delta, 0),
                       receipts=self.receipts | {event_id})


@dataclass(frozen=True)
class Order:
    order_id: str
    sales_order: str
    item: str
    model: str
    quantity: int
    delivered: int
    required: int
    barcodes: tuple[str, ...] = ()

    @property
    def target(self):
        return max(self.quantity - self.delivered, 0)

    @property
    def completed(self):
        return len(self.barcodes) // self.required

    @property
    def pending(self):
        return len(self.barcodes) % self.required

    def scan(self, barcode: str):
        if not barcode.strip():
            raise ValueError("請先輸入示範條碼。")
        if self.completed >= self.target:
            raise ValueError("這筆工單已達今日派工數量，沒有再新增條碼。")
        return replace(self, barcodes=(*self.barcodes, barcode.strip()))

    def undo(self):
        return replace(self, barcodes=self.barcodes[:-1])


def sample_orders() -> list[Order]:
    # Deliberately synthetic identifiers and product descriptions.
    return [Order("DEMO-WO-001", "DEMO-SO-A", "000010", "示範城市車 / M", 8, 5, 3),
            Order("DEMO-WO-002", "DEMO-SO-A", "000020", "示範旅行車 / L", 10, 4, 1),
            Order("DEMO-WO-003", "DEMO-SO-B", "000010", "示範通勤車 / S", 5, 3, 2)]


def validate_report_columns(columns: list[str]) -> list[str]:
    return [name for name in ("訂單", "項次", "預排數量", "完成數量") if name not in columns]
