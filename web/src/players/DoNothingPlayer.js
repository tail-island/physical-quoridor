export class DoNothingPlayer {
  getAction (_observation) {
    return [0, [0, 0], [0, 0, 0]]
  }
}
