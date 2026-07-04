# 如何写一个 BMB 适配器

实现 `bmb/contract.py` 的 `BMBMemoryArchitecture` 协议:

```python
class YourMemory:
    def ingest(self, user_id, ts, text): ...      # 按时间序流入,更新内部状态
    def assemble(self, user_id, query, budget_tokens): ...  # 返回 ≤budget 的纯文本载荷
```

要点:
- `ingest` 按时间顺序被调用;`user_id` 间隔离。
- `assemble` 返回后**不得**再检索/回调外部;载荷即全部。
- 返回 >budget 会被 harness 硬截断——把最重要的信息放前面。
- 内部随机性用固定 seed,保证可复现。
- 注册:在 `run_benchmark.py` 的 `_ADAPTERS` 加一行。

参考实现:`bmb/adapters/naive_dump.py`(地板)、`bmb/adapters/oracle.py`(天花板)。
