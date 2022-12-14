import dataclasses
import re
import typing


PARTY_PAYMENT_REGEX = re.compile(r'^(?P<name>.*)\s+(?P<payment>[-+]?[\d.]+)$')


class BaseError(Exception):
    """Base exception for this module."""


class ValidationError(BaseError):
    """Data validation error."""


class NoMemberError(BaseError):
    """No member specified."""


@dataclasses.dataclass
class PartyMember:
    name: str
    payment: float

    @classmethod
    def from_dict(cls, row: typing.Dict):
        return cls(name=row['name'], payment=float(row['payment']))

    @classmethod
    def from_string(cls, string: str):
        found = PARTY_PAYMENT_REGEX.search(string)
        if not found:
            raise ValidationError(f'invalid string format: "{string}"')
        return cls.from_dict(found.groupdict())


def get_total(members: typing.List[PartyMember]) -> float:
    if not members:
        raise NoMemberError('no members specified')
    return sum(member.payment for member in members)


def get_average(members: typing.List[PartyMember]) -> float:
    total = get_total(members)
    return total / len(members)
