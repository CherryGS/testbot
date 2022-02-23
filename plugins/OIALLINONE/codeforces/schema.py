# generated by datamodel-codegen:
#   filename:  in.json
#   timestamp: 2022-02-22T15:41:23+00:00

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Type(Enum):
    PRELIMINARY = "PRELIMINARY"
    FINAL = "FINAL"


class ProblemResult(BaseModel):
    points: float = Field(..., description="Floating point number.")
    penalty: Optional[int] = Field(
        None,
        description="Integer. Penalty (in ICPC meaning) of the party for this problem. Can be absent.",
    )
    rejectedAttemptCount: int = Field(
        ..., description="Integer. Number of incorrect submissions."
    )
    type: Type = Field(
        ...,
        description="Enum: PRELIMINARY, FINAL. If type is PRELIMINARY then points can decrease (if, for example, solution will fail during system test). Otherwise, party can only increase points for this problem by submitting better solutions.",
    )
    bestSubmissionTimeSeconds: Optional[int] = Field(
        None,
        description="Integer. Number of seconds after the start of the contest before the submission, that brought maximal amount of points for this problem. Can be absent.",
    )


class ParticipantType(Enum):
    CONTESTANT = "CONTESTANT"
    PRACTICE = "PRACTICE"
    VIRTUAL = "VIRTUAL"
    MANAGER = "MANAGER"
    OUT_OF_COMPETITION = "OUT_OF_COMPETITION"


class Type1(Enum):
    CF = "CF"
    IOI = "IOI"
    ICPC = "ICPC"


class Phase(Enum):
    BEFORE = "BEFORE"
    CODING = "CODING"
    PENDING_SYSTEM_TEST = "PENDING_SYSTEM_TEST"
    SYSTEM_TEST = "SYSTEM_TEST"
    FINISHED = "FINISHED"


class Contest(BaseModel):
    id: int = Field(..., description="Integer.")
    name: str = Field(..., description="String. Localized.")
    type: Type1 = Field(
        ..., description="Enum: CF, IOI, ICPC. Scoring system used for the contest."
    )
    phase: Phase = Field(
        ...,
        description="Enum: BEFORE, CODING, PENDING_SYSTEM_TEST, SYSTEM_TEST, FINISHED.",
    )
    frozen: bool = Field(
        ...,
        description="Boolean. If true, then the ranklist for the contest is frozen and shows only submissions, created before freeze.",
    )
    durationSeconds: int = Field(
        ..., description="Integer. Duration of the contest in seconds."
    )
    preparedBy: Optional[str] = Field(
        None,
        description="String. Can be absent. Handle of the user, how created the contest.",
    )
    websiteUrl: Optional[str] = Field(
        None, description="String. Can be absent. URL for contest-related website."
    )
    relativeTimeSeconds: Optional[int] = Field(
        None,
        description="Integer. Can be absent. Number of seconds, passed after the start of the contest. Can be negative.",
    )
    kind: Optional[str] = Field(
        None,
        description="String. Localized. Can be absent. Human-readable type of the contest from the following categories: Official ICPC Contest, Official School Contest, Opencup Contest, School/University/City/Region Championship, Training Camp Contest, Official International Personal Contest, Training Contest.",
    )
    country: Optional[str] = Field(
        None, description="String. Localized. Can be absent."
    )
    icpcRegion: Optional[str] = Field(
        None,
        description="String. Localized. Can be absent. Name of the Region for official ICPC contests.",
    )
    city: Optional[str] = Field(None, description="String. Localized. Can be absent.")
    startTimeSeconds: Optional[int] = Field(
        None, description="Integer. Can be absent. Contest start time in unix format."
    )
    description: Optional[str] = Field(
        None, description="String. Localized. Can be absent."
    )
    season: Optional[str] = Field(None, description="String. Can be absent.")
    difficulty: Optional[int] = Field(
        None,
        description="Integer. Can be absent. From 1 to 5. Larger number means more difficult problems.",
    )


class User(BaseModel):
    lastName: Optional[str] = Field(
        None, description="String. Localized. Can be absent."
    )
    country: Optional[str] = Field(
        None, description="String. Localized. Can be absent."
    )
    lastOnlineTimeSeconds: int = Field(
        ...,
        description="Integer. Time, when user was last seen online, in unix format.",
    )
    city: Optional[str] = Field(None, description="String. Localized. Can be absent.")
    rating: Optional[int] = Field(None, description="Integer.")
    friendOfCount: int = Field(
        ..., description="Integer. Amount of users who have this user in friends."
    )
    titlePhoto: str = Field(..., description="String. User's title photo URL.")
    handle: str = Field(..., description="String. Codeforces user handle.")
    avatar: str = Field(..., description="String. User's avatar URL.")
    firstName: Optional[str] = Field(
        None, description="String. Localized. Can be absent."
    )
    contribution: int = Field(..., description="Integer. User contribution.")
    organization: Optional[str] = Field(
        None, description="String. Localized. Can be absent."
    )
    rank: Optional[str] = Field(
        None, description="String. Localized. һ��������δ�μӹ������޴���"
    )
    maxRating: Optional[int] = Field(
        None, description="Integer.һ��������δ�μӹ������޴���"
    )
    registrationTimeSeconds: int = Field(
        ..., description="Integer. Time, when user was registered, in unix format."
    )
    maxRank: Optional[str] = Field(
        None, description="String. Localized.һ��������δ�μӹ������޴���"
    )
    email: Optional[str] = Field(
        None,
        description="String. Shown only if user allowed to share his contact info.",
    )
    vkId: Optional[str] = Field(
        None,
        description="String. User id for VK social network. Shown only if user allowed to share his contact info.",
    )
    openId: Optional[str] = Field(
        None,
        description="String. Shown only if user allowed to share his contact info.",
    )


class Type2(Enum):
    PROGRAMMING = "PROGRAMMING"
    QUESTION = "QUESTION"


class Problem(BaseModel):
    contestId: Optional[int] = Field(
        None,
        description="Integer. Can be absent. Id of the contest, containing the problem.",
    )
    problemsetName: Optional[str] = Field(
        None,
        description="String. Can be absent. Short name of the problemset the problem belongs to.",
    )
    index: str = Field(
        ...,
        description="String. Usually, a letter or letter with digit(s) indicating the problem index in a contest.",
    )
    name: str = Field(..., description="String. Localized.")
    type: Type2 = Field(..., description="Enum: PROGRAMMING, QUESTION.")
    points: Optional[int] = Field(
        None,
        description="Floating point number. Can be absent. Maximum amount of points for the problem.",
    )
    rating: Optional[int] = Field(
        None, description="Integer. Can be absent. Problem rating (difficulty)."
    )
    tags: List[str] = Field(..., description="String list. Problem tags.")


class Member(BaseModel):
    handle: str = Field(..., description="String. Codeforces user handle.")
    name: Optional[str] = Field(
        None, description="String. Can be absent. User's name if available."
    )


class Party(BaseModel):
    contestId: Optional[int] = Field(
        None,
        description="Integer. Can be absent. Id of the contest, in which party is participating.",
    )
    members: List[Member] = Field(
        ..., description="List of Member objects. Members of the party."
    )
    participantType: ParticipantType = Field(
        ...,
        description="Enum: CONTESTANT, PRACTICE, VIRTUAL, MANAGER, OUT_OF_COMPETITION.",
    )
    teamId: Optional[int] = Field(
        None,
        description="Integer. Can be absent. If party is a team, then it is a unique team id. Otherwise, this field is absent.",
    )
    teamName: Optional[str] = Field(
        None,
        description="String. Localized. Can be absent. If party is a team or ghost, then it is a localized name of the team. Otherwise, it is absent.",
    )
    room: Optional[int] = Field(
        None,
        description="Integer. Can be absent. Room of the party. If absent, then the party has no room.",
    )
    ghost: bool = Field(
        ...,
        description="Boolean. If true then this party is a ghost. It participated in the contest, but not on Codeforces. For example, Andrew Stankevich Contests in Gym has ghosts of the participants from Petrozavodsk Training Camp.",
    )
    startTimeSeconds: Optional[int] = Field(
        None,
        description="Integer. Can be absent. Time, when this party started a contest.",
    )


class RanklistRow(BaseModel):
    party: Party
    rank: int = Field(..., description="Integer. Party place in the contest.")
    points: int = Field(
        ...,
        description="Floating point number. Total amount of points, scored by the party.",
    )
    penalty: int = Field(
        ..., description="Integer. Total penalty (in ICPC meaning) of the party."
    )
    successfulHackCount: int = Field(..., description="Integer.")
    unsuccessfulHackCount: int = Field(..., description="Integer.")
    problemResults: List[ProblemResult] = Field(
        ...,
        description='List of ProblemResult objects. Party results for each problem. Order of the problems is the same as in "problems" field of the returned object.',
    )
    lastSubmissionTimeSeconds: Optional[int] = Field(
        None,
        description="Integer. For IOI contests only. Time in seconds from the start of the contest to the last submission that added some points to the total score of the party. Can be absent.",
    )
