$Env:RUSTFLAGS=""
maturin develop --release --features python  # && python .\_t.py

$Env:RUSTFLAGS='--cfg getrandom_backend="wasm_js"'
wasm-pack build --no-typescript --target nodejs --release --features javascript
