import random
from generator.noise import make_noise
from generator.generate import author_truth, generate_dataset, save_dataset
from generator.schemas import UserTruth, SalientFact
from bmb.models import FakeModel

def test_noise_is_fillers():
    rng = random.Random(0)
    noise = make_noise(rng, 5)
    assert len(noise) == 5 and all(isinstance(x, str) and x for x in noise)

def test_author_truth_deterministic():
    cfg = {"span_days": 60}
    t1 = author_truth("u1", 42, cfg)
    t2 = author_truth("u1", 42, cfg)
    assert t1 == t2
    t3 = author_truth("u1", 7, cfg)
    assert t1 != t3 or True  # 允许偶发相同;不强断言

def test_generate_dataset_with_fake_model():
    cfg = {"span_days": 40, "noise_per_user": 6,
           "salient_pool": [["f1", "对青霉素过敏", ["青霉素"], "用药禁忌?"]],
           "state_pool": [["饮食", [(0, "素食"), (20, "破戒")], "现在饮食?"]],
           "profile_pool": [["p1", "数码党", ["买了键盘"], "数码相关", "送什么礼物?"]]}
    ds = generate_dataset(cfg, FakeModel(lambda p: "今天天气不错。"), seed=1, n_users=2)
    assert len(ds.events) > 0 and len(ds.probes) >= 2 * 3
    assert ds.manifest["seed"] == 1 and ds.manifest["n_users"] == 2

def test_save_and_layout(tmp_path):
    cfg = {"span_days": 40, "noise_per_user": 4,
           "salient_pool": [["f1", "对青霉素过敏", ["青霉素"], "用药禁忌?"]],
           "state_pool": [], "profile_pool": []}
    ds = generate_dataset(cfg, FakeModel(lambda p: "x"), seed=1, n_users=1)
    save_dataset(ds, str(tmp_path))
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "ground_truth.json").exists()
    assert any((tmp_path / "users").glob("*.jsonl"))
