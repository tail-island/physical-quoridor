mod interop;

use std::f32::consts::PI;
use rapier2d::prelude::*;
use rand::prelude::*;
use rand_distr::*;

const FRAME_RATE: i32 = 10;  // 物理エンジンのフレーム・レートである60の約数を設定してください。

pub enum Action {
    AddForce(f32, f32),
    SetFence(i32, i32, bool)
}

type Observation = ([f32; 2], [f32; 2], [f32; 2], [f32; 2], [[[bool; 2]; 8]; 8], i32, i32, i32, i32);

pub struct PhysicalQuoridor {
    // ゲーム用の属性。
    rng: StdRng,
    tick: i32,
    pawn_handles: [RigidBodyHandle; 2],
    remained_fences: [i32; 2],
    can_fence_after: [i32; 2],
    fences: [[[bool; 2]; 8]; 8],

    // rapier2d用の属性。
    physics_pipeline: PhysicsPipeline,
    integration_parameters: IntegrationParameters,
    islands: IslandManager,
    broad_phase: DefaultBroadPhase,
    narrow_phase: NarrowPhase,
    bodies: RigidBodySet,
    colliders: ColliderSet,
    impulse_joints: ImpulseJointSet,
    multibody_joints: MultibodyJointSet,
    ccd_solver: CCDSolver,
    query_pipeline: QueryPipeline
}

impl PhysicalQuoridor {
    pub fn new(seed: u64) -> PhysicalQuoridor {
        let mut bodies = RigidBodySet::new();
        let mut colliders = ColliderSet::new();

        let pawn_handles = [-4.0, 4.0].map(|x| {
            let handle = bodies.insert(RigidBodyBuilder::dynamic().ccd_enabled(true).linear_damping(0.5).translation(vector![x, 0.0]).build());
            colliders.insert_with_parent(ColliderBuilder::ball(0.2).restitution(1.0).build(), handle, &mut bodies);

            handle
        });

        PhysicalQuoridor {
            rng: rand::rngs::StdRng::seed_from_u64(seed),
            tick: 0,
            pawn_handles,
            remained_fences: [10, 10],
            can_fence_after: [0, 0],
            fences: [[[false; 2]; 8]; 8],

            physics_pipeline: PhysicsPipeline::new(),
            integration_parameters: IntegrationParameters::default(),
            islands: IslandManager::new(),
            broad_phase: DefaultBroadPhase::new(),
            narrow_phase: NarrowPhase::new(),
            bodies,
            colliders,
            impulse_joints: ImpulseJointSet::new(),
            multibody_joints: MultibodyJointSet::new(),
            ccd_solver: CCDSolver::new(),
            query_pipeline: QueryPipeline::new()
        }
    }

    fn add_force(&mut self, player_index: usize, x: f32, y: f32) {
        // 力を作成します。

        let mut force = vector![x, y] * if player_index == 0 { 1.0 } else { -1.0 };  // 同じプログラムがplayer 1も担当できるように、力を反転します。

        // 力は最大1に制限します。

        if force.norm() > 0.5 {
            force *= 0.5 / force.norm();
        }

        // 不確実性のために、ランダムな値を追加します。

        force += {
            let normal_distr = Normal::new(0.0, force.norm() * 0.05).unwrap();
            vector![normal_distr.sample(&mut self.rng), normal_distr.sample(&mut self.rng)]
        };

        // 駒を取得します。

        let pawn = self.bodies.get_mut(self.pawn_handles[player_index]).unwrap();

        // 駒に力を加えます。

        pawn.reset_forces(true);
        pawn.add_force(force, true);
    }

    fn can_goal(&self, player_index: usize, fences: &[[[bool; 2]; 8]; 8]) -> bool {
        let r = (4.0 - self.bodies[self.pawn_handles[player_index]].translation().y).round() as i32;
        let c = (4.0 + self.bodies[self.pawn_handles[player_index]].translation().x).round() as i32;

        let mut stack = vec![(r, c)];
        let mut visiteds = [[false; 9]; 9];
        visiteds[r as usize][c as usize] = true;

        while let Some((r, c)) = stack.pop() {
            if (player_index == 0 && c == 8) || (player_index == 1 && c == 0) {
                return true;
            }

            for (next_r, next_c) in [(r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)] {
                if next_r < 0 || next_r > 8 || next_c < 0 || next_c > 8 {
                    continue;
                }

                if next_c == c {
                    if (c > 0 && fences[std::cmp::min(r, next_r) as usize][(c - 1) as usize][0]) || (c < 8 && fences[std::cmp::min(r, next_r) as usize][c as usize][0]) {
                        continue;
                    }
                } else {
                    if (r > 0 && fences[(r - 1) as usize][std::cmp::min(c, next_c) as usize][1]) || (r < 8 && fences[r as usize][std::cmp::min(c, next_c) as usize][1]) {
                        continue;
                    }
                }

                if visiteds[next_r as usize][next_c as usize] {
                    continue;
                }
                visiteds[next_r as usize][next_c as usize] = true;

                stack.push((next_r, next_c));
            }
        }

        false
    }

    fn set_fence(&mut self, player_index: usize, r: i32, c: i32, is_vertical: bool) {
        // 設置可能なフェンスは10枚まで。フェンス設置は、前のフェンス設置の後1秒たってから。

        if self.remained_fences[player_index] == 0 || self.can_fence_after[player_index] > 0 {
            return;
        }

        // フェンスの位置を取得します。

        let [r, c] = [r, c].map(|index| if player_index == 0 { index } else { 7 - index });  // 同じプログラムがplayer 1も担当できるように、rowとcolumnを反転します。

        // 既存のフェンスと重なる位置へは設置できません。

        if is_vertical {
            if self.fences[r as usize][c as usize][0] || self.fences[r as usize][c as usize][1] || (r > 0 && self.fences[(r - 1) as usize][c as usize][1]) || (r < 7 && self.fences[(r + 1) as usize][c as usize][1]) {
                return;
            }
        } else {
            if self.fences[r as usize][c as usize][1] || self.fences[r as usize][c as usize][0] || (c > 0 && self.fences[r as usize][(c - 1) as usize][0]) || (c < 7 && self.fences[r as usize][(c + 1) as usize][0]) {
                return;
            }
        }

        // フェンスの有無を設定します。

        let mut fences = self.fences.clone();
        fences[r as usize][c as usize][is_vertical as usize] = true;

        // ゴールできなくなるフェンスの設置は許可されません。

        if !self.can_goal(0, &fences) || !self.can_goal(1, &fences) {
            return;
        }

        // フェンスの有無を更新します。

        self.fences = fences;

        // フェンスの残り枚数を減らします。

        self.remained_fences[player_index] -= 1;

        // 次のフェンス設置は1秒後。

        self.can_fence_after[player_index] = FRAME_RATE;

        // 物理エンジン上にフェンスを設置します。

        let handle = self.bodies.insert(RigidBodyBuilder::fixed().translation(vector![c as f32 - 3.5, (r as f32 - 3.5) * -1.0]).build());
        self.colliders.insert_with_parent(ColliderBuilder::cuboid(1.1, 0.1).restitution(1.0).rotation(if is_vertical { PI / 2.0 } else { 0.0 }).build(), handle, &mut self.bodies);
    }

    pub fn step(&mut self, actions: [Action; 2]) -> ([Observation; 2], [f32; 2], [bool; 2]) {
        // アクションを実行します。

        for (i, action) in actions.iter().enumerate() {
            match action {
                Action::AddForce(x, y) => self.add_force(i, *x, *y),
                Action::SetFence(row, column, is_vertical) => self.set_fence(i, *row, *column, *is_vertical)
            }
        }

        // 物理エンジンのステップを進めます。

        let gravity = vector![0.0, 0.0];
        let physics_hooks = ();
        let event_handler = ();

        let (rewards, mut termination) = {
            let mut i = 0;

            loop {
                self.physics_pipeline.step(
                    &gravity,
                    &self.integration_parameters,
                    &mut self.islands,
                    &mut self.broad_phase,
                    &mut self.narrow_phase,
                    &mut self.bodies,
                    &mut self.colliders,
                    &mut self.impulse_joints,
                    &mut self.multibody_joints,
                    &mut self.ccd_solver,
                    Some(&mut self.query_pipeline),
                    &physics_hooks,
                    &event_handler
                );

                // 勝利判定をします。

                let pawn_0 = &self.bodies[self.pawn_handles[0]];
                let pawn_1 = &self.bodies[self.pawn_handles[1]];

                let (rewards, termination) = match (
                    pawn_0.translation().x >  4.3,
                    pawn_1.translation().x < -4.3,
                    pawn_0.translation().x < -4.5 || pawn_0.translation().y > 4.5 || pawn_0.translation().y < -4.5,
                    pawn_1.translation().x >  4.5 || pawn_1.translation().y > 4.5 || pawn_1.translation().y < -4.5
                ) {
                    (_,     _,     true,  true ) => ([-0.5, -0.5], true ),
                    (_,     _,     true,  false) => ([-1.0,  1.0], true ),
                    (_,     _,     false, true ) => ([ 1.0, -1.0], true ),
                    (true,  true,  _,     _    ) => ([ 0.5,  0.5], true ),
                    (true,  false, _,     _    ) => ([ 1.0, -1.0], true ),
                    (false, true,  _,     _    ) => ([-1.0,  1.0], true ),
                    (false, false, false, false) => ([ 0.0,  0.0], false)
                };

                i += 1;

                if i == 60 / FRAME_RATE || termination {
                    break (rewards, termination);
                }
            }
        };

        // 120秒でゲーム終了とします。

        self.tick += 1;

        if self.tick == 120 * FRAME_RATE {
            termination = true;
        }

        // 観測結果と報酬、終了判定を作成します。

        let pawn_0 = &self.bodies[self.pawn_handles[0]];
        let pawn_1 = &self.bodies[self.pawn_handles[1]];

        let result = (
            [
                (
                    [ pawn_0.translation().x,  pawn_0.translation().y], [ pawn_0.linvel().x,  pawn_0.linvel().y],
                    [ pawn_1.translation().x,  pawn_1.translation().y], [ pawn_1.linvel().x,  pawn_1.linvel().y],
                    self.fences,
                    self.remained_fences[0],
                    self.remained_fences[1],
                    self.can_fence_after[0],
                    self.can_fence_after[1]
                ),
                (
                    [-pawn_1.translation().x, -pawn_1.translation().y], [-pawn_1.linvel().x, -pawn_1.linvel().y],  // 同じプログラムがplayer 1も担当できるように、観測結果を反転します。
                    [-pawn_0.translation().x, -pawn_0.translation().y], [-pawn_0.linvel().x, -pawn_0.linvel().y],
                    {
                        let mut result = [[[false; 2]; 8]; 8];

                        for i in 0..8 {
                            for j in 0..8 {
                                for k in 0..2 {
                                    result[i][j][k] = self.fences[7 - i][7 - j][k];
                                }
                            }
                        }

                        result
                    },
                    self.remained_fences[1],
                    self.remained_fences[0],
                    self.can_fence_after[1],
                    self.can_fence_after[0]
                )
            ],
            rewards,
            [termination, termination]
        );

        for i in 0..2 {
            self.can_fence_after[i] -= 1;
        }

        result
    }
}
