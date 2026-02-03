## Project layout

- `relayserve`: CLI entrypoint
- `relayserve/internal/device`: device registry + strength scoring
- `relayserve/internal/profile`: probe stubs + profiling hooks
- `relayserve/internal/runner`: per-device runner selection
- `relayserve/internal/scheduler`: request scheduler and phase info
- `relayserve/internal/queue`: in-memory request queue
- `relayserve/internal/shard`: sharding plan stub
- `relayserve/internal/kv`: KV cache manager stub
- `relayserve/internal/metrics`: metrics collection stub
- `relayserve/internal/server`: HTTP server
