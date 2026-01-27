from fastapi import Depends, HTTPException, status
from app.feature_flags.flags import flags

def require_feature(feature: str):
    def _dep(posto_id: int):
        if not flags.is_enabled(feature, posto_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature}' desativada para o posto {posto_id}"
            )
    return _dep