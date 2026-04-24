from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class LanguageLearnerDto:
    id:                 int
    user_id:            int
    language_to_code:   str
    language_to_name:   str
    language_from_code: str | None
    language_from_name: str | None
    xp:                 int
    is_active:          bool

    @staticmethod
    def from_model(ll) -> LanguageLearnerDto:
        return LanguageLearnerDto(
            id=ll.id,
            user_id=ll.user_id,
            language_to_code=ll.language_to.code,
            language_to_name=ll.language_to.name,
            language_from_code=ll.language_from.code if ll.language_from else None,
            language_from_name=ll.language_from.name if ll.language_from else None,
            xp=ll.xp,
            is_active=ll.is_active,
        )


@dataclass
class CreateLanguageLearnerResult:
    success: bool
    learner: LanguageLearnerDto | None = None
    error:   str | None = None


@dataclass
class UpdateLanguageLearnerResult:
    success: bool
    learner: LanguageLearnerDto | None = None
    error:   str | None = None


@dataclass
class DeleteLanguageLearnerResult:
    success: bool
    error:   str | None = None


@dataclass
class GetLanguageLearnerResult:
    success: bool
    learner: LanguageLearnerDto | None = None
    error:   str | None = None


@dataclass
class ListLanguageLearnersResult:
    success:  bool
    learners: list[LanguageLearnerDto] = field(default_factory=list)
    error:    str | None = None