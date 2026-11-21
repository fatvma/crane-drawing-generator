"""Input rules for the API. Pydantic checks these on the server.

The allowed ranges come from crane.py, so there is one place to change them.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app import crane


class CraneInputs(BaseModel):
    """The four numbers/choices that define a crane."""

    # Reject any extra fields instead of silently ignoring them.
    model_config = ConfigDict(extra="forbid")

    span_m: float = Field(
        ge=crane.SPAN_M_RANGE[0], le=crane.SPAN_M_RANGE[1],
        description="Rail centre to rail centre, in metres.",
    )
    capacity_t: float = Field(
        ge=crane.CAPACITY_T_RANGE[0], le=crane.CAPACITY_T_RANGE[1],
        description="Rated load in tonnes.",
    )
    lifting_height_m: float = Field(
        ge=crane.LIFT_M_RANGE[0], le=crane.LIFT_M_RANGE[1],
        description="Hook travel in metres.",
    )
    duty_group: Literal[*crane.DUTY_GROUPS] = Field(
        description="Crane duty group, e.g. A5.",
    )


class DesignIn(CraneInputs):
    """A crane plus a name, used when saving a design (next step)."""

    # Spaces at the start/end are removed, so "   " counts as empty.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80)