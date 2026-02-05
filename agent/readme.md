### Agent Contract

- Backend must call `agent_step(session, incoming_text)`
- Backend must not modify agent_state or intelligence
- Backend must return reply verbatim
- Backend must trigger callback only when `should_finalize == true`
