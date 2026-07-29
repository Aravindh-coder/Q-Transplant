import hashlib
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.domain import BlockchainBlock


class BlockchainService:
    """
    Cryptographic Blockchain Audit Layer.
    Every critical action creates an immutable SHA-256 hashed block.
    Supports tamper detection, integrity verification, and chain export.
    """

    @staticmethod
    def compute_hash(index: int, timestamp: str, actor: str, hospital: str,
                     action: str, details: str, prev_hash: str) -> str:
        block_string = json.dumps({
            "index": index, "timestamp": timestamp, "actor": actor,
            "hospital": hospital, "action": action, "details": details,
            "prev_hash": prev_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    @staticmethod
    def sign_block(hash_val: str) -> str:
        sig_raw = f"QT-SIG-{hash_val[:16]}-{uuid.uuid4().hex[:8]}"
        return hashlib.sha256(sig_raw.encode()).hexdigest()[:32]

    @classmethod
    def add_block(cls, db: Session, actor: str, hospital: str, action: str, details: str = "") -> Dict[str, Any]:
        # Get current chain length for index
        from sqlalchemy import func
        max_index = db.query(func.max(BlockchainBlock.index)).scalar() or -1
        new_index = max_index + 1

        # Get previous hash
        if max_index >= 0:
            prev_block = db.query(BlockchainBlock).filter(
                BlockchainBlock.index == max_index).first()
            prev_hash = prev_block.hash if prev_block else "0" * 64
        else:
            prev_hash = "0" * 64  # Genesis block

        timestamp = datetime.utcnow().isoformat()
        block_hash = cls.compute_hash(new_index, timestamp, actor, hospital, action, details, prev_hash)
        signature = cls.sign_block(block_hash)

        block = BlockchainBlock(
            index=new_index,
            timestamp=datetime.utcnow(),
            actor=actor,
            hospital=hospital,
            action=action,
            details=details,
            prev_hash=prev_hash,
            hash=block_hash,
            digital_signature=signature
        )
        db.add(block)
        db.commit()

        return {
            "index": new_index,
            "timestamp": timestamp,
            "actor": actor,
            "hospital": hospital,
            "action": action,
            "details": details,
            "prev_hash": prev_hash,
            "hash": block_hash,
            "digital_signature": signature
        }

    @classmethod
    def get_chain(cls, db: Session) -> List[Dict[str, Any]]:
        blocks = db.query(BlockchainBlock).order_by(BlockchainBlock.index).all()
        return [
            {
                "index": b.index,
                "timestamp": b.timestamp.isoformat() if b.timestamp else "",
                "actor": b.actor,
                "hospital": b.hospital,
                "action": b.action,
                "details": b.details,
                "prev_hash": b.prev_hash,
                "hash": b.hash,
                "digital_signature": b.digital_signature
            }
            for b in blocks
        ]

    @classmethod
    def verify_chain_integrity(cls, db: Session) -> Dict[str, Any]:
        blocks = db.query(BlockchainBlock).order_by(BlockchainBlock.index).all()
        if not blocks:
            return {"valid": True, "message": "Chain is empty (genesis ready)", "tampered_at": None}

        for i, block in enumerate(blocks):
            # Recompute hash
            expected_hash = cls.compute_hash(
                block.index,
                block.timestamp.isoformat() if block.timestamp else "",
                block.actor, block.hospital, block.action,
                block.details or "", block.prev_hash
            )
            if expected_hash != block.hash:
                return {
                    "valid": False,
                    "message": f"TAMPER DETECTED at Block #{block.index}",
                    "tampered_at": block.index
                }
            if i > 0 and block.prev_hash != blocks[i - 1].hash:
                return {
                    "valid": False,
                    "message": f"CHAIN BROKEN between Block #{blocks[i-1].index} and #{block.index}",
                    "tampered_at": block.index
                }

        return {
            "valid": True,
            "message": f"Chain integrity verified. {len(blocks)} blocks are tamper-free.",
            "tampered_at": None,
            "block_count": len(blocks)
        }
