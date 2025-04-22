use serde::{Deserialize, Serialize};
use tsify::Tsify;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct PhysicalQuoridor {
    physical_quoridor: crate::PhysicalQuoridor
}

#[derive(Tsify, Serialize, Deserialize)]
#[tsify(into_wasm_abi, from_wasm_abi)]
pub struct Action(i32, Vec<f32>, Vec<i32>);

#[derive(Tsify, Serialize, Deserialize)]
#[tsify(into_wasm_abi, from_wasm_abi)]
pub struct StepResult(Vec<crate::Observation>, Vec<f32>, Vec<bool>);

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
            match action.0 {
                0 => crate::Action::AddForce(action.1[0], action.1[1]),
                1 => crate::Action::SetFence(action.2[0], action.2[1], action.2[2] != 0),
                _ => panic!("invalid action.")
            }
        ).collect::<Vec<_>>().try_into().unwrap());

        StepResult(result.0.to_vec(), result.1.to_vec(), result.2.to_vec())
    }
}
