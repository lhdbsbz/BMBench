"""用 FakeModel 生成随仓库分发的 smoke 数据集(测试+冒烟用,无需 LLM)。"""
import sys
from pathlib import Path

# 项目根入 sys.path,使脚本从任意目录独立可跑
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

import yaml
from bmb.models import FakeModel
from generator.generate import generate_dataset, save_dataset

if __name__ == "__main__":
    cfg = yaml.safe_load((_ROOT / "configs/smoke.yaml").read_text(encoding="utf-8"))
    ds = generate_dataset(cfg, FakeModel(lambda p: "今天发生了些日常琐事。"), seed=42, n_users=3)
    save_dataset(ds, str(_ROOT / "datasets/smoke"))
    print("smoke 数据集已生成:datasets/smoke")
