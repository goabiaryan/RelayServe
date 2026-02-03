## Project layout

- `cmd/relay`: entrypoint
- `relay/internal/device`: device registry + strength scoring
- `relay/internal/profile`: probe stubs + profiling hooks
- `relay/internal/runner`: per-device runner selection
- `relay/internal/scheduler`: request scheduler and phase info
- `relay/internal/queue`: in-memory request queue
- `relay/internal/shard`: sharding plan stub
- `relay/internal/kv`: KV cache manager stub
- `relay/internal/metrics`: metrics collection stub
- `relay/internal/server`: HTTP server
