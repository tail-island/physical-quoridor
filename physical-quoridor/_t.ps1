$Env:RUSTFLAGS=""
maturin develop --release --features python

$Env:RUSTFLAGS='--cfg getrandom_backend="wasm_js"'
wasm-pack build --target bundler --no-typescript --release --features javascript
