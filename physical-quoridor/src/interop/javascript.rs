use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct PhysicalQuoridor {
    physical_quoridor: crate::PhysicalQuoridor
}

#[wasm_bindgen]
pub struct Action {
    action_type: i32,
    force: Vec<f32>,
    fence: Vec<i32>
}

#[allow(dead_code)]
#[wasm_bindgen]
pub struct StepResult {
    observations: Vec<crate::Observation>,
    rewards: Vec<f32>,
    terminations: Vec<bool>
}

#[wasm_bindgen]
impl PhysicalQuoridor {
    #[wasm_bindgen(constructor)]
    pub fn new(seed: u64) -> PhysicalQuoridor {
        PhysicalQuoridor {
            physical_quoridor: crate::PhysicalQuoridor::new(seed)
        }
    }

    pub fn step(&mut self, actions: Vec<Action>) -> StepResult {
        let result = self.physical_quoridor.step(actions.iter().map(|action|
            match action.action_type {
                0 => crate::Action::AddForce(action.force[0], action.force[1]),
                1 => crate::Action::SetFence(action.fence[0], action.fence[1], action.fence[2] != 0),
                _ => panic!("invalid action.")
            }
        ).collect::<Vec<_>>().try_into().unwrap());

        StepResult {
            observations: result.0.to_vec(),
            rewards: result.1.to_vec(),
            terminations: result.2.to_vec()
        }
    }
}
