$Env:RUSTFLAGS=""
maturin develop --release --features python  # && python .\_t.py

$Env:RUSTFLAGS='--cfg getrandom_backend="wasm_js"'
wasm-pack build --target bundler --release --features javascript
