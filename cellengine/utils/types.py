from __future__ import annotations
import sys
from typing import List

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
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
