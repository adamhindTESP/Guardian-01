# Guardian Planner Training Plan (v1)

## Frozen Inputs
- Guardian Seed: training-ready-v1.0 (tag)
- Records: 83 total
- Splits: 58 train / 12 val / 13 test
- Safety authority: Guardian G1–G3.5 (unchanged)

## Training Objective
- Reduce planner veto rate
- Do NOT change safety semantics
- Guardian veto remains final authority

## Model
- Base: microsoft/phi-2
- Method: LoRA fine-tuning
- Hardware: GTX 1060 (6GB VRAM)

## Steps
1. `pip install -r requirements_training.txt`
2. `python train_planner_phi2.py`
3. `python validate_planner.py`

## Success Criteria
- ≥70% safe proposals on test scenarios
- 0 safety regressions (Guardian still vetoes violations)

## Notes
- Training optimizes efficiency, not safety
- Guardian Seed v1 must not be modified
