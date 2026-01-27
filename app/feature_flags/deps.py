from fastapi import Depends, HTTPException, status
from app.feature_flags.flags import flags

def require_feature(nome_feature: str):
    def _checker():
        if not flags.get(nome_feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{nome_feature}' desativada"
            )
    return _checker