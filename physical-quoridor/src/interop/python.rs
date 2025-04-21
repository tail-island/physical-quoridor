use pyo3::prelude::*;

#[pyclass]
struct PhysicalQuoridor {
    physical_quoridor: crate::PhysicalQuoridor
}

#[pymethods]
impl PhysicalQuoridor {
    #[new]
    fn new(seed: u64) -> PhysicalQuoridor {
        PhysicalQuoridor {
            physical_quoridor: crate::PhysicalQuoridor::new(seed)
        }
    }

    fn step(&mut self, actions: [(i32, [f32; 2], (i32, i32, i32)); 2]) -> ([crate::Observation; 2], [f32; 2], [bool; 2]) {
        self.physical_quoridor.step(actions.map(|action|
            match action.0 {
                0 => crate::Action::AddForce(action.1[0], action.1[1]),
                1 => crate::Action::SetFence(action.2.0, action.2.1, action.2.2 != 0),
                _ => panic!("invalid action.")
            }
        ))
    }
}

#[pymodule]
fn physical_quoridor(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PhysicalQuoridor>()?;

    Ok(())
}
