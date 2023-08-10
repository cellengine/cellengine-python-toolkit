from __future__ import annotations
from typing import List

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

ApplyTailoringInsert = TypedDict("ApplyTailoringInsert", {"_id": str, "fcsFileId": str})
ApplyTailoringUpdate = TypedDict("ApplyTailoringUpdate", {"_id": str, "fcsFileId": str})
ApplyTailoringDelete = TypedDict("ApplyTailoringDelete", {"_id": str, "fcsFileId": str})
ApplyTailoringRes = TypedDict(
    "ApplyTailoringRes",
    {
        "inserted": List[ApplyTailoringInsert],
        "updated": List[ApplyTailoringUpdate],
        "deleted": List[ApplyTailoringDelete],
    },
)
