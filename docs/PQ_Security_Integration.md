# Post-Quantum Security Integration
## AEGIS + PQ-DR Integration Guide

---

## Overview

This document describes how **PQ-DR** (Post-Quantum Double Ratchet) library (`https://github.com/peter14l/pq-dr`) integrates with AEGIS for quantum-resistant communications.

**Status:** Not integrated in MVP. Integration hooks added for Phase 2.

---

## Security Architecture

### What Gets Encrypted

| Component | Data | Priority |
|-----------|------|----------|
| **Kafka sensor topics** | Raw sensor detections | HIGH |
| **Kafka fused.tracks** | Track positions/velocities | HIGH |
| **Kafka threat.scores** | Threat classifications | HIGH |
| **Kafka assignments** | Interceptor commands | CRITICAL |
| **Redis state** | Full system state | HIGH |
| **WebSocket** | Real-time dashboard | CRITICAL |

### Why This Matters

- AEGIS targets DoD/AFWERX contracts
- Post-quantum encryption is a **hard requirement** for classified systems
- Competitors don't have this → **competitive moat**

---

## Integration Points

### 1. Kafka Message Encryption

**File:** `api-gateway/src/main.py`

```python
# Before producing to Kafka (publish method)
from pq_aura import RatchetEngine

def produce_encrypted(self, topic, message):
    encrypted = RatchetEngine.encrypt(self.ratchet_state, message, self.ad, self.rng)
    self.producer.produce(topic, encrypted)

# After consuming from Kafka (consume method)
def consume_and_decrypt(self, topic):
    encrypted = self.consumer.consume()
    return RatchetEngine.decrypt(self.ratchet_state, encrypted, self.ad)
```

### 2. Redis State Encryption

**File:** `api-gateway/src/state_manager.py`

```python
# write_system_state → encrypt before Redis set
encrypted = pq_aura.encrypt(ratchet_state, state_json, ad, rng)
await self.redis.set("aegis:state", encrypted)

# read_system_state → decrypt after Redis get
encrypted = await self.redis.get("aegis:state")
state_json = pq_aura.decrypt(ratchet_state, encrypted, ad)
```

### 3. WebSocket Encryption

**File:** `api-gateway/src/ws_handler.py`

```python
# Encrypt all WebSocket messages
async def send_state(self, state):
    encrypted = RatchetEngine.encrypt(self.ratchet_state, state, self.ad, self.rng)
    await self.websocket.send(encrypted)
    
# Decrypt incoming messages
async def receive_message(self, data):
    return RatchetEngine.decrypt(self.ratchet_state, data, self.ad)
```

---

## Key Exchange Protocol

### Initial Handshake (Pre-Shared)

1. **Publish pre-key bundle** to a secure server:
   - ML-KEM encapsulation keys
   - X25519 identity keys
   - Signed by identity key

2. **Initiate from any service:**
   ```python
   (state, initial_msg, root_key) = HandshakeEngine.initiate_alice(
       bundle, id_pk, id_sk, rng
   )
   ```

3. **Respond:**
   ```python
   (state, root_key) = HandshakeEngine.respond_bob(
       initial_msg, id_pk, id_sk, signed_sk, ot_sk
   )
   ```

4. **Derive session keys** from shared root_key

---

## Implementation Checklist

- [ ] Add `pq-aura` to `requirements.txt`
- [ ] Implement handshake on service startup
- [ ] Add key refresh mechanism (asymmetric ratchet)
- [ ] Add header encryption (hide ratchet count)
- [ ] Test in staging environment
- [ ] Get security audit
- [ ] Document for DFARS compliance

---

## Alternatives Considered

| Option | Why Not |
|--------|--------|
| TLS 1.3 | Doesn't protect at-rest or end-to-end |
| Signal Protocol | Not hybrid PQ by default |
| WireGuard | No post-quantum KEM |

---

## Reference

- **PQ-DR:** https://github.com/peter14l/pq-dr
- **NIST FIPS 203:** ML-KEM-1024 specification
- **ML-KEM:** Module-Lattice-Based Key-Encapsulation Mechanism
- **X25519:** Elliptic Curve Diffie-Hellman

---

*Document Version: 1.0 | Integration Lead: AEGIS Security Team*