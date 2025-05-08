export class RandomPlayer {
  getAction (_observation) {
    return [Math.random() < 0.5 ? 0 : 1, [Math.random() - 0.5, Math.random() - 0.5], [Math.floor(Math.random() * 8), Math.floor(Math.random() * 8), Math.floor(Math.random() * 2)]]
  }
}
